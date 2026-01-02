"""Performance measurement utilities.

This module provides tools for measuring and analyzing code performance,
including execution time and memory usage.
"""

import os
import time
import tracemalloc
import psutil
from contextlib import ContextDecorator
from pathlib import Path


class Perf(ContextDecorator):
    """Performance measurement context manager and decorator.

    Measures wall time, CPU time, memory usage and allocations.
    """

    def __init__(self, label: str | None = None, print_output: bool = True) -> None:
        """Initialize performance measurement context.

        Args:
            label: Optional label for the measurement
            print_output: Whether to print results automatically

        """
        self.label = label
        self.cpu = 0
        self.wall = 0
        self.ratio = 0
        self.rss = 0
        self.peak = 0
        self.final_rss = 0
        self.print = print_output

        self.label_str = ""

    def __enter__(self) -> "Perf":
        """Enter the performance measurement context.

        Returns:
            The Perf instance itself

        """
        self.proc = psutil.Process(os.getpid())
        self.t0_cpu = time.process_time()
        self.t0_wall = time.time()
        self.t0_rss = self.proc.memory_info().rss
        tracemalloc.start()
        return self

    def __exit__(self, *exc) -> None:  # noqa: ANN002
        """Exit the performance measurement context.

        Args:
            *exc: Exception information if any

        """
        self.cpu = time.process_time() - self.t0_cpu
        self.wall = time.time() - self.t0_wall
        self.ratio = self.cpu / self.wall if self.wall > 0 else 0
        self.rss = self.proc.memory_info().rss - self.t0_rss
        self.peak = tracemalloc.get_traced_memory()[1] / 1_048_576
        self.final_rss = self.proc.memory_info().rss / 1_048_576
        tracemalloc.stop()

        self.label_str = f"[{self.label}]" if self.label is not None else ""
        self.label_str += f"\tWall Time: {self.wall:.3f}s"
        self.label_str += f"\tCPU Time: {self.cpu:.3f}s({self.ratio:.2f}x)"
        self.label_str += f"\tΔRSS: {self.rss / 1_048_576:.1f} MiB"
        self.label_str += f"\tPeak alloc: {self.peak:.1f} MiB"
        self.label_str += f"\tFinal RSS: {self.final_rss:.1f} MiB"

        if self.print:
            print(self.label_str)


def fadvise_remove_cache(path: str) -> None:
    """Advise OS to remove file from cache.

    Args:
        path: Path to the file to remove from cache

    """
    with Path(path).open("rb") as f:
        fd = f.fileno()
        os.posix_fadvise(fd, 0, 0, os.POSIX_FADV_DONTNEED)
