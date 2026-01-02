"""Version utilities for miu-core."""

from importlib.metadata import PackageNotFoundError, version
from typing import NamedTuple


class VersionInfo(NamedTuple):
    """Structured version information."""

    major: int
    minor: int
    patch: int
    prerelease: str = ""


def get_version() -> str:
    """Get package version from metadata or fallback."""
    try:
        return version("miu-core")
    except PackageNotFoundError:
        return "0.1.0"


def version_info() -> VersionInfo:
    """Parse version into components."""
    v = get_version()
    parts = v.replace("-", "+").split("+")
    version_str = parts[0]
    prerelease = parts[1] if len(parts) > 1 else ""

    nums = [int(x) for x in version_str.split(".")[:3]]
    while len(nums) < 3:
        nums.append(0)

    return VersionInfo(nums[0], nums[1], nums[2], prerelease)
