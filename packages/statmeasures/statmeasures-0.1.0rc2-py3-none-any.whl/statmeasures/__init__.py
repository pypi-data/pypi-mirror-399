__all__ = ["__version__", "center", "spread"]

from importlib import metadata

from statmeasures import center, spread

__version__ = metadata.version(__name__)
