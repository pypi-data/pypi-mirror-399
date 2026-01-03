"""Coordinate package for managing coordinate systems and transformations."""

# Import main classes and functions for convenient access
from .types import CoordinateType
from .transforms import translate2D, rotate2D, scale2D, trs2D
from .frame import Frame, create_frame
from .coordinate import Coordinate, Point, Vector, transform_coordinate

# Visualization is optional - only available if matplotlib is installed
try:
    from . import visualization
except ImportError:
    visualization = None  # type: ignore[assignment]

# Define what's available when using "from coordinate import *"
__all__ = [
    # Nothing to export explicitly, avoinding namespace conflictions
]


