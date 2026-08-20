"""Example application demonstrating the enforced dependency direction."""

from importlib.metadata import PackageNotFoundError, version

try:
    # Convención del template: la versión vive SOLO en pyproject.toml.
    __version__ = version("write-check-trust")
except PackageNotFoundError:
    __version__ = "0.0.0+local"
