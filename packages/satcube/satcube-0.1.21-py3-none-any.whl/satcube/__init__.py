from __future__ import annotations

import importlib

from satcube.download import metadata
from satcube.objects import SatCubeMetadata

importlib.import_module("satcube._quiet")

from_directory = SatCubeMetadata.from_directory

__all__ = ["SatCubeMetadata", "from_directory", "metadata"]

try:
    from importlib.metadata import version

    __version__ = version("satcube")
except Exception:
    __version__ = "0.0.0-dev"
