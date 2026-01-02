"""Manage packages and versions."""

from importlib import metadata
import packaging.version as pv


def check_version(version_need: str, package_name: str) -> None:
    """Check if the installed version of a package satisfies the required version.

    Args:
        version_need (str): The minimum required version string (e.g., '0.3.0a1').
        package_name (str): The name of the package to check (e.g., 'plotma').

    Raises:
        ImportError: If the package is not installed or the version is incompatible.

    """
    # Get versions: required, installed
    required = pv.parse(version_need)
    try:
        installed = pv.parse(metadata.version(package_name))
    except metadata.PackageNotFoundError:
        raise ImportError(f"错误: {package_name} 包未安装。")

    # Check version compatibility
    if installed >= required:  # satisfied minimum version required
        if installed.release[0] == required.release[0]:  # satisfied MAJOR
            if required.release[0] > 0 or installed.release[1] == required.release[1]:
                # version compatible
                return
    raise ImportError(
        f"版本不兼容：需要 {package_name} = {version_need}, 当前为 {installed}"
    )
    return
