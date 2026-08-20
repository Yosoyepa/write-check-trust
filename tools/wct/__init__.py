"""Write, Check, Trust: the wct hardening harness."""

from importlib.metadata import PackageNotFoundError, version

try:
    # Fuente única: pyproject.toml. Un bump de release no se sincroniza a mano.
    __version__ = version("write-check-trust")
except PackageNotFoundError:
    __version__ = "0.0.0+local"
