"""Coordinate representation classes for points and vectors."""

from typing import Optional
import numpy as np

from .frame import Frame
from .types import CoordinateType


def transform_coordinate(transform: np.ndarray, coordinates: np.ndarray, coordinate_type: CoordinateType) -> np.ndarray:
    """Applies an affine transformation to a coordinate, respecting point vs vector semantics.
    
    Points and vectors transform differently under affine transformations:
    - Points (weight=1): Affected by translation, rotation, and scaling
    - Vectors (weight=0): Affected only by rotation and scaling, NOT translation
    
    This function converts to homogeneous coordinates, applies the transformation,
    and converts back to Cartesian coordinates.
    
    Args:
        transform: 3x3 affine transformation matrix in homogeneous coordinates.
        coordinates: 2D coordinate as numpy array [x, y].
        coordinate_type: CoordinateType.POINT or CoordinateType.VECTOR.
    
    Returns:
        Transformed 2D coordinate as numpy array [x', y'].
    
    Examples:
        >>> # Point translation
        >>> transform_coordinate(translate2D(5, 3), np.array([1, 2]), CoordinateType.POINT)
        array([6., 5.])  # Point moved by (5, 3)
        
        >>> # Vector translation (no effect)
        >>> transform_coordinate(translate2D(5, 3), np.array([1, 2]), CoordinateType.VECTOR)
        array([1., 2.])  # Vector unchanged
    """
    # Convert to homogeneous coordinates
    weight = 1.0 if coordinate_type == CoordinateType.POINT else 0.0
    homogeneous_point = np.append(coordinates, weight) 
    transformed_point = transform @ homogeneous_point

    # Return to Cartesian coordinates
    # Normalize if necessary
    weight = transformed_point[2]
    if weight != 0:
        transformed_point /= weight
    return transformed_point[:2]


class Coordinate:
    """Base class for representing coordinates (points or vectors) in a coordinate frame.
    
    Coordinates can be defined in any coordinate frame and converted between frames.
    The distinction between points and vectors is crucial:
    - Points: Represent positions, affected by all transformations including translation
    - Vectors: Represent directions/displacements, unaffected by translation
    
    Attributes:
        coordinate_type: CoordinateType.POINT or CoordinateType.VECTOR
        local_coords: 2D numpy array [x, y] in the local coordinate frame
        frame: The coordinate frame this coordinate is defined in
    
    Examples:
        >>> frame = Frame(transform=translate2D(5, 3))
        >>> coord = Coordinate(CoordinateType.POINT, np.array([1, 2]), frame)
        >>> absolute_coord = coord.to_absolute()
    """

    def __init__(self, coordinate_type: CoordinateType, local_coords: np.ndarray, frame: Optional[Frame] = None):
        """Initialize a coordinate.
        
        Args:
            coordinate_type: CoordinateType.POINT or CoordinateType.VECTOR
            local_coords: 2D numpy array [x, y] in the local coordinate frame
            frame: Coordinate frame this coordinate is defined in.
                   If None, uses absolute/identity frame.
        """
        self.coordinate_type = coordinate_type
        self.local_coords = local_coords
        self.frame = frame if frame is not None else Frame()

    def to_absolute(self) -> 'Coordinate':
        """Converts this coordinate to absolute (identity) coordinate frame.
        
        Applies the cumulative transformation from this coordinate's frame through
        all parent frames to express the coordinate in absolute space.
        
        Returns:
            New Coordinate with coordinates expressed in absolute frame.
        
        Examples:
            >>> root = Frame(transform=translate2D(10, 5))
            >>> child = Frame(transform=translate2D(3, 2), parent=root)
            >>> point = Point(np.array([1, 1]), frame=child)
            >>> absolute_point = point.to_absolute()
            >>> absolute_point.local_coords  # Should be [14, 8]
        """
        absolute_transform = self.frame.compute_absolute_transform()
        absolute_coords = transform_coordinate(absolute_transform, self.local_coords, self.coordinate_type)
        return Coordinate(local_coords=absolute_coords, coordinate_type=self.coordinate_type, frame=None)
        
    def relative_to(self, target_frame: Frame) -> 'Coordinate':
        """Converts this coordinate to a different coordinate frame.
        
        Transforms the coordinate from its current frame to the target frame,
        properly handling the coordinate type (point vs vector) semantics.
        
        Args:
            target_frame: The destination coordinate frame.
        
        Returns:
            New Coordinate with coordinates expressed in the target frame.
        
        Examples:
            >>> frame_a = Frame(transform=translate2D(5, 0))
            >>> frame_b = Frame(transform=translate2D(0, 3))
            >>> point_in_a = Point(np.array([0, 0]), frame=frame_a)
            >>> point_in_b = point_in_a.relative_to(frame_b)
            >>> point_in_b.local_coords  # Should be [5, -3]
        """
        # Inverse transform from absolute to target frame
        relative_transform = self.frame.compute_relative_transform_to(target_frame)
        relative_coords = transform_coordinate(relative_transform, self.local_coords, self.coordinate_type)
        return Coordinate(local_coords=relative_coords, coordinate_type=self.coordinate_type, frame=target_frame)


class Point(Coordinate):
    """Represents a point (position) in a coordinate frame.
    
    Points are affected by all transformations including translation, rotation, and scaling.
    Use this class to represent positions in space.
    
    Args:
        local_coords: 2D numpy array [x, y] representing the point position
        frame: Coordinate frame this point is defined in. If None, uses absolute frame.
    
    Examples:
        >>> # Point at origin in a translated frame
        >>> frame = Frame(transform=translate2D(10, 5))
        >>> point = Point(np.array([0, 0]), frame=frame)
        >>> absolute_point = point.to_absolute()
        >>> absolute_point.local_coords  # [10, 5] - affected by translation
    """
    
    def __init__(self, local_coords: np.ndarray, frame: Optional[Frame] = None):
        super().__init__(
            coordinate_type=CoordinateType.POINT,
            local_coords=local_coords, 
            frame=frame)
        

class Vector(Coordinate):
    """Represents a vector (direction/displacement) in a coordinate frame.
    
    Vectors are NOT affected by translation, only by rotation and scaling.
    Use this class to represent directions, velocities, or relative displacements.
    
    Args:
        local_coords: 2D numpy array [x, y] representing the vector components
        frame: Coordinate frame this vector is defined in. If None, uses absolute frame.
    
    Examples:
        >>> # Vector in a translated frame
        >>> frame = Frame(transform=translate2D(10, 5))
        >>> vector = Vector(np.array([1, 0]), frame=frame)
        >>> absolute_vector = vector.to_absolute()
        >>> absolute_vector.local_coords  # Still [1, 0] - unaffected by translation
    """
    
    def __init__(self, local_coords: np.ndarray, frame: Optional[Frame] = None):
        super().__init__(
            coordinate_type=CoordinateType.VECTOR,
            local_coords=local_coords, 
            frame=frame)
