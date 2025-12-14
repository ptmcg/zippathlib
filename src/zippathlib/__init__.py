from .zip_pathlib import ZipPath

import importlib.metadata
__version__ = importlib.metadata.version(__package__)


__all__ = [
    '__version__',
    'ZipPath',
]
