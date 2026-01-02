"""Parallel computing runner module.

This module provides a flexible interface for executing tasks
using different parallel computing backends. It implements a factory pattern
through mprunner_factory that creates appropriate runners based on the client
type provided.

The module supports multiple execution modes:
1. ThreadPoolExecutor: For local multi-threaded processing
2. SLURMConfig: For job submission to SLURM clusters
3. DaskClient (future): For distributed computing with Dask

Key Components:
- MPRunner: Abstract base class defining the interface for all runners
- ThreadPoolRunner: Implementation for local thread-based parallelism
- SLURMRunner: Implementation for SLURM cluster job submission
- SLURMConfig: Configuration class for SLURM job parameters
- mprunner_factory: Factory function to create appropriate runner instances
- MPClient: Type alias for Union[ThreadPoolExecutor, SLURMConfig]

The API provides two main execution methods:
- batch_run: For executing command-line operations
- batch_function_run: For executing Python functions

Each runner implementation handles the execution details while providing
a consistent interface. The abstract methods _submit_command, _submit_function,
_join_futures, and _cancel_futures provide extension points for new runners.

Usage:
```python
# For local processing with limited workers
executor = ThreadPoolExecutor(max_workers=4)
runner = mprunner_factory(executor, log_file)
runner.batch_run(cmd_args_list)
runner.batch_function_run(process_video, video_paths, presets)

# For SLURM cluster processing
config = SLURMConfig(partition="batch", num_cpus=12, memory="8G", output=log_file)
runner = mprunner_factory(config, log_file)
runner.batch_run(cmd_args_list)

# For future Dask distributed processing
client = Client("scheduler-address:8786")
runner = mprunner_factory(client, log_file)
runner.batch_function_run(process_video, video_paths, presets)

# Using the MPClient type alias for better type hints
def process_videos(client: MPClient, videos: list[str]) -> None:
    runner = mprunner_factory(client)
    runner.batch_run(create_ffmpeg_commands(videos))
```
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from concurrent.futures import Future, ThreadPoolExecutor
from pathlib import Path
import queue
import shlex
from subprocess import run, CompletedProcess
import threading
from typing import Callable

from xutk.log import CtxLogger as Logger

vidtidy_logger = Logger("vidtidy")


class MPRunner(ABC):
    """Handles video processing with string parameters."""

    def __init__(self, client, log_file: Path | None) -> None:  # noqa: ANN001
        """Initialize with basic file patterns and optional config.

        Args:
            client: Configuration or executor for the runner
            log_file: Path to the log file (optional, if None logging is disabled)

        """
        self._log_queue = queue.Queue()
        self._log_lock = threading.Lock()

        if log_file:
            self._log_file = log_file
            self._log_thread = threading.Thread(target=self._log_writer, daemon=True)
            self._log_thread.start()
        else:
            self._log_file = Path()
            self._log_thread = None

        self.client = client

    def _log_writer(self) -> None:
        """Background thread that writes logs sequentially.

        This method runs as a daemon thread, continuously processing log messages
        from the queue and writing them to the log file. Only active when log_file
        is not None.
        """
        if not self._log_file:
            return

        while True:
            log_msg = self._log_queue.get()
            try:
                with self._log_file.open("a") as f:
                    f.write(log_msg)
            except Exception as e:
                vidtidy_logger.error(
                    {"caller": self.__class__.__name__}, f"Failed to write log: {e}"
                )
            self._log_queue.task_done()

    @abstractmethod
    def batch_run(self, cmd_args_list: list[list[str]]) -> list:
        """Run multiple commands synchronously, blocking until completion.

        Args:
            cmd_args_list: List of command argument lists to execute

        """
        ...

    @abstractmethod
    def batch_function_run(
        self,
        func: Callable,
        *args_lists: list,
        **common_kwargs,  # noqa: ANN003
    ) -> list:
        """Run multiple instances of a function together, blocking until completion.

        Supports two calling conventions:
        1. Multiple argument lists: batch_function_run
           (func, arg1_list, arg2_list, kwarg=value)
        2. List of argument tuples: batch_function_run
           (func, [(arg1, arg2), ...], kwarg=value)

        Args:
            func: The function to execute
            *args_lists: Variable length argument lists
            **common_kwargs: Common keyword arguments for all function calls

        """
        ...


class ThreadPoolRunner(MPRunner):
    """Handles video processing with string parameters."""

    client: ThreadPoolExecutor

    def batch_run(self, cmd_args_list: list[list[str]]) -> list[CompletedProcess[str]]:  # noqa: D102
        futures: list[Future[CompletedProcess[str]]] = []
        results: list[CompletedProcess[str]] = []
        try:
            with self.client as executor:
                for cmd_item in cmd_args_list:
                    future = executor.submit(self._thread_pool_execute, cmd_item)
                    futures.append(future)
                # Wait for all futures and logs to complete
                try:
                    results.extend(future.result() for future in futures)
                    self._log_queue.join()
                except KeyboardInterrupt:
                    vidtidy_logger.warning(
                        {"caller": self.__class__.__name__},
                        "\nProcessing interrupted by user. Cleaning up...",
                    )
                    # Cancel all pending futures on interrupt
                    for future in futures:
                        future.cancel()
                    # Wait for any running tasks to complete
                    for future in futures:
                        if not future.done():
                            future.result()
                    self._log_queue.join()
                    raise
        except KeyboardInterrupt:
            vidtidy_logger.warning(
                {"caller": self.__class__.__name__},
                "\nJob scheduling interrupted by user. Cleaning up...",
            )
            raise
        return results

    def _thread_pool_execute(self, cmd_args: list[str]) -> CompletedProcess[str]:
        process = run(cmd_args, check=True, capture_output=True, text=True)
        with self._log_lock:
            # FFmpeg uses stderr for normal output and stdout for progress
            # Use the last argument as the processing file if available,
            # otherwise use command name
            target_file = cmd_args[-1] if len(cmd_args) > 1 else cmd_args[0]
            self._log_queue.put(
                f"=== Processing {target_file} ===\n"
                f"Output:\n{process.stdout}\n"
                f"Errors:\n{process.stderr}\n\n"
            )
        return process

    def batch_function_run(  # noqa: D102
        self,
        func: Callable,
        *args_lists: list,
        **common_kwargs,  # noqa: ANN003
    ) -> list:
        if not args_lists:
            vidtidy_logger.warning(
                {"caller": self.__class__.__name__},
                "\nBatch runner got args_list with different length.",
            )
            return []

        arg_list_tuple = self._batch_function_parse_args(args_lists)

        # === Build Tasks and Submit ===
        futures: list[Future] = []
        results: list = []
        try:
            with self.client as executor:
                for args in arg_list_tuple:
                    future = executor.submit(func, *args, **common_kwargs)
                    futures.append(future)

                # Wait for completion and collect results in order
                try:
                    # Wait for all futures and collect results in original order
                    results.extend(future.result() for future in futures)
                    self._log_queue.join()
                except KeyboardInterrupt:
                    vidtidy_logger.warning(
                        {"caller": self.__class__.__name__},
                        "\nProcessing interrupted by user. Cancelling tasks...",
                    )
                    for future in futures:
                        future.cancel()
                    # Allow running tasks to finish cleanly
                    for future in futures:
                        if not future.done():
                            try:
                                future.result()
                            except:  # noqa: E722
                                pass
                    self._log_queue.join()
                    raise

            return results

        except KeyboardInterrupt:
            vidtidy_logger.warning(
                {"caller": self.__class__.__name__},
                "\nJob Scheduling interrupted by user. Cleaning up...",
            )
            raise

    @staticmethod
    def _batch_function_parse_args(args_lists: tuple[list, ...]) -> list[tuple]:
        """Parse input arguments into list of argument tuples.

        Supports two calling conventions:
        1. Multiple argument lists: [a1,a2], [b1,b2] -> [(a1,b1), (a2,b2)]
        2. List of tuples: [(a1,b1), (a2,b2)] -> [(a1,b1), (a2,b2)]

        Args:
            args_lists: Tuple of argument lists (from *args)

        Returns:
            List of argument tuples for function calls

        Raises:
            ValueError: If argument lists have different lengths or invalid format

        """
        if not args_lists:
            return []

        first_arg = args_lists[0]

        if len(args_lists) == 1 and isinstance(first_arg, list) and first_arg:
            # Case 1: Single list of tuples - [(arg1, arg2), ...]
            if isinstance(first_arg[0], tuple):
                return first_arg  # Already in (arg1, arg2) format
            else:
                # Case 2: Single list of non-tuples, treat as single argument
                return [(x,) for x in first_arg]
        else:
            # Case 3: Multiple argument lists - [a1,a2], [b1,b2]
            n_args = len(args_lists[0])
            if any(len(lst) != n_args for lst in args_lists):
                raise ValueError("All argument lists must have the same length.")
            return list(zip(*args_lists))


@dataclass
class SLURMConfig:
    """Configuration for SLURM job submission.

    Attributes:
        output: Path for stdout log file
        error: Path for stderr log file
        partition: SLURM partition to use
        node: Specific node to run on (optional)
        num_cpus: Number of CPU cores to allocate per task
        memory: Memory allocation in GB
        job_name: Name for the SLURM job
        time_limit: Time limit for the job (HH:MM:SS format)

    """

    output: Path | None = None
    error: Path | None = None
    partition: str = "batch"
    node: str | None = None
    num_cpus: int = 12
    memory: str = "8G"
    job_name: str = "vidtidy_job"
    time_limit: str = "02:00:00"


class SLURMRunner(MPRunner):
    """Handles SLURM job submission for video processing tasks."""

    client: SLURMConfig

    def batch_run(self, cmd_args_list: list[list[str]]) -> list[int]:
        """Submit multiple commands as SLURM jobs using the client configuration.

        Args:
            cmd_args_list: List of command argument lists to execute

        Raises:
            RuntimeError: If any job submission fails

        """
        job_ids: list[int] = []
        try:
            for i, cmd_args in enumerate(cmd_args_list):
                # Create unique job name for each task
                job_name = f"{self.client.job_name}_{i}"

                # Build sbatch command with options from config
                sbatch_cmd = [
                    "sbatch",
                    "--job-name",
                    job_name,
                    "--time",
                    self.client.time_limit,
                    "--partition",
                    self.client.partition,
                    "--cpus-per-task",
                    str(self.client.num_cpus),
                    "--mem",
                    self.client.memory,
                ]

                # Add node specification if provided
                if self.client.node:
                    sbatch_cmd.extend(["--nodelist", self.client.node])

                # Add output and error log paths if specified
                if self.client.output:
                    sbatch_cmd.extend(
                        [
                            "--output",
                            str(
                                self.client.output.with_suffix(
                                    f".{i}{self.client.output.suffix}"
                                )
                            ),
                        ]
                    )
                if self.client.error:
                    sbatch_cmd.extend(
                        [
                            "--error",
                            str(
                                self.client.error.with_suffix(
                                    f".{i}{self.client.error.suffix}"
                                )
                            ),
                        ]
                    )

                # Add the actual command to run
                sbatch_cmd.extend(["--wrap", shlex.join(cmd_args)])

                # Submit the job
                result = run(sbatch_cmd, capture_output=True, text=True, check=True)

                if result.returncode != 0:
                    raise RuntimeError(f"SLURM job submission failed: {result.stderr}")

                # Extract job ID from output (format: "Submitted batch job <job_id>")
                job_id_line = result.stdout.strip()
                if "Submitted batch job" in job_id_line:
                    job_id = int(job_id_line.split()[-1])
                    job_ids.append(job_id)
                    self._log_queue.put(
                        f"Submitted SLURM job {job_id} for "
                        + f"command: {shlex.join(cmd_args)}\n"
                    )
                else:
                    raise RuntimeError(
                        f"Could not parse SLURM job ID from: {job_id_line}"
                    )

        except Exception:
            # Cancel all submitted jobs if there's an error
            for job_id in job_ids:
                run(["scancel", str(job_id)], capture_output=True, check=True)
            raise

        # Wait for all jobs to complete and logs to be written
        try:
            self._log_queue.join()
        except KeyboardInterrupt:
            # Cancel all jobs on interrupt
            for job_id in job_ids:
                run(["scancel", str(job_id)], capture_output=True, check=True)
            self._log_queue.join()
            raise

        return job_ids

    def batch_function_run(  # noqa: D102
        self,
        func: Callable,
        *args_lists: list,
        **common_kwargs,  # noqa: ANN003
    ) -> None:
        raise NotImplementedError(
            """
            SLURMRunner does not support function execution.
            Use batch_run with shell commands.
            """
        )


MPClient = int | ThreadPoolExecutor | SLURMConfig


def mprunner_factory(mp_client: MPClient, log_file: Path | None = None) -> MPRunner:
    """Create appropriate runner based on client type.

    Args:
        mp_client: A multi-processing implement instance
        log_file: Path to the log file

    Returns:
        Appropriate runner instance
        (ThreadPoolRunner, SLURMRunner, or future DaskRunner)

    Raises:
        NotImplementedError: If client type is not supported

    """
    if isinstance(mp_client, int) and mp_client > 0:
        return ThreadPoolRunner(ThreadPoolExecutor(max_workers=mp_client), log_file)
    elif isinstance(mp_client, ThreadPoolExecutor):
        return ThreadPoolRunner(mp_client, log_file)
    if isinstance(mp_client, SLURMConfig):
        return SLURMRunner(mp_client, log_file)
    else:
        raise NotImplementedError(f"Unsupported client type: {type(mp_client)}")
