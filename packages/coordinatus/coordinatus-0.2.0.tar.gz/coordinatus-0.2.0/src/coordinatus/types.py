"""Coordinate type definitions."""

from enum import Enum


class CoordinateType(Enum):
    """Defines whether a coordinate represents a point or a vector."""
    POINT = "point"
    VECTOR = "vector"
