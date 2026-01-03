"""miu-code: AI coding agent with CLI."""

from importlib.metadata import PackageNotFoundError, version

try:
    __version__ = version("miu-code")
except PackageNotFoundError:
    __version__ = "1.0.0"

__all__ = ["__version__"]
