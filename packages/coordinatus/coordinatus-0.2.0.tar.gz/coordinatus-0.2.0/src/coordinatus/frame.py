"""Coordinate frame representation and operations."""

from typing import Optional
import numpy as np

from .transforms import trs2D

class Frame:
    """A coordinate frame that can be nested within other frames.
    
    Each frame has a position, rotation, and scale relative to its parent frame,
    encoded in a transform matrix. Use functions from transforms.py to easily
    create these matrices. Frames can be organized in a hierarchy, like objects
    in a scene graph.
    
    Attributes:
        transform: 3x3 affine transformation matrix from this frame to its parent.
                  Defaults to identity if not specified.
        parent: Optional parent coordinate frame. If None, this is a root/absolute frame.
    
    Examples:
        >>> # Create a root coordinate frame
        >>> root = Frame()
        >>> 
        >>> # Create a child frame translated by (5, 3) relative to root
        >>> child = Frame(transform=translate2D(5, 3), parent=root)
        >>> 
        >>> # Get transformation to absolute space
        >>> absolute_t = child.compute_absolute_transform()
    """
    def __init__(self, transform: Optional[np.ndarray] = None, parent: Optional['Frame'] = None):
        """Initialize a coordinate frame.
        
        Args:
            transform: 3x3 affine transformation matrix relative to parent.
                      If None, uses identity (no transformation).
            parent: Parent coordinate frame. If None, this is a root frame.
        """
        self.transform = transform if transform is not None else np.eye(3)
        self.parent = parent

    def compute_absolute_transform(self) -> np.ndarray:
        """Computes the cumulative transformation matrix from this frame to absolute space.
        
        Recursively multiplies transformation matrices up the hierarchy to compute
        the complete transformation from this coordinate frame to the root (absolute)
        coordinate frame.
        
        Returns:
            3x3 numpy array representing the transformation from frame-relative to absolute coordinates.
        
        Examples:
            >>> root = Frame(transform=translate2D(10, 5))
            >>> child = Frame(transform=translate2D(3, 2), parent=root)
            >>> absolute_t = child.compute_absolute_transform()
            >>> # absolute_t represents translation by (13, 7)
        """
        if self.parent is None:
            return self.transform
        else:
            return self.parent.compute_absolute_transform() @ self.transform

    def compute_relative_transform_to(self, target_frame: 'Frame') -> np.ndarray:
        """Computes the transformation matrix to convert coordinates from this frame to another.
        
        Calculates the transformation needed to express coordinates defined in this
        coordinate frame in the target coordinate frame. This is computed by:
        1. Transforming from this frame to absolute space
        2. Transforming from absolute space to the target frame
        
        Args:
            target_frame: The destination coordinate frame.
        
        Returns:
            3x3 transformation matrix that converts coordinates from this frame
            to the target frame.
        
        Examples:
            >>> frame_a = Frame(transform=translate2D(5, 0))
            >>> frame_b = Frame(transform=translate2D(0, 3))
            >>> convert_t = frame_a.compute_relative_transform_to(frame_b)
            >>> # Use convert_t to express frame_a coordinates in frame_b
        """
        inv_transform = np.linalg.inv(target_frame.compute_absolute_transform())
        return inv_transform @ self.compute_absolute_transform()


def create_frame(parent: Optional[Frame], tx: float=0.0, ty: float=0.0, angle_rad: float=0.0, sx: float=1.0, sy: float=1.0) -> Frame:
    """Factory function to create a coordinate frame using TRS (Translation-Rotation-Scale) parameters.
    
    Convenience function that constructs a coordinate frame from intuitive transformation
    parameters instead of requiring a raw transformation matrix. The transformations are
    applied in TRS order: scale first, then rotate, then translate.
    
    Args:
        parent: Parent coordinate frame. If None, creates a root frame.
        tx: Translation along X-axis (default: 0.0)
        ty: Translation along Y-axis (default: 0.0)
        angle_rad: Rotation angle in radians, counter-clockwise (default: 0.0)
        sx: Scale factor along X-axis (default: 1.0)
        sy: Scale factor along Y-axis (default: 1.0)
    
    Returns:
        A new Frame with the specified transformation relative to its parent.
    
    Examples:
        >>> # Create root frame at (10, 5) with no rotation or scaling
        >>> root = create_frame(None, tx=10, ty=5)
        >>> 
        >>> # Create child rotated 90° and scaled 2x
        >>> child = create_frame(root, angle_rad=np.pi/2, sx=2, sy=2)
    """
    transform = trs2D(tx, ty, angle_rad, sx, sy)
    return Frame(transform=transform, parent=parent)
