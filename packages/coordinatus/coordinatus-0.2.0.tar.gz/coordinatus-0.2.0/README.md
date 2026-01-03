# Coordinatus

**Simple coordinate transformations with hierarchical frames**

Ever needed to convert coordinates between different spaces?  *Coordinatus* makes it easy to work with nested coordinate systems—like transforming from a character's local space to world space, or from one object to another.

> **Note:** Currently supports 2D Cartesian coordinates. Support for 3D, polar, and spherical coordinate systems is planned.

## Why Coordinatus?

- **Intuitive API**: Work with Points and Vectors that transform correctly (vectors ignore translation!)
- **Hierarchical Frames**: Build parent-child relationships just like scene graphs in game engines
- **Clean transformations**: Simple functions for translation, rotation, and scaling
- **Type-safe**: Points and Vectors are distinct types with correct transformation behavior

## Quick Start

```python
from coordinatus import Frame, Point, create_frame
import numpy as np

# Create a world frame
world = Frame()

# Create a car frame, positioned at (100, 50) in the world
car = create_frame(parent=world, tx=100, ty=50, angle_rad=np.pi/4)

# Create a wheel frame, offset (10, 0) from the car
wheel = create_frame(parent=car, tx=10, ty=0)

# A point at the wheel's center
point_in_wheel = Point(x=0, y=0, frame=wheel)

# Convert to world coordinates
point_in_world = point_in_wheel.as_absolute()
print(f"Wheel center in world: ({point_in_world.x}, {point_in_world.y})")

# Convert between any two frames
point_in_car = point_in_wheel.relative_to(car)
print(f"Wheel center in car frame: ({point_in_car.x}, {point_in_car.y})")
```

## Core Concepts

### Frames
A `Frame` represents a coordinate system with its own position, rotation, and scale. Frames can be nested to create hierarchies.

### Points vs Vectors
- **Points** represent positions and are affected by translation
- **Vectors** represent directions/offsets and ignore translation

```python
from coordinatus import Point, Vector, Frame, create_frame

frame = create_frame(parent=None, tx=10, ty=5)

# Point gets translated
point = Point(x=0, y=0, frame=frame)
absolute = point.as_absolute()  # (10, 5)

# Vector does NOT get translated
vector = Vector(x=1, y=0, frame=frame)
absolute_vec = vector.as_absolute()  # (1, 0) - only rotation/scale applied
```

### Coordinate Conversion

Convert between any two frames in your hierarchy:

```python
# Convert from frame_a to frame_b
point_in_a = Point(np.array([5, 3]), frame=frame_a)
point_in_b = point_in_a.relative_to(frame_b)

# Or get absolute (world) coordinates
point_in_world = point_in_a.as_absolute()
```

## The Relativity of Coordinates

A fundamental concept in coordinate transformations is that **the same geometry looks different depending on your point of view**. The same F-shaped object can appear rotated, scaled, or sheared simply by changing which reference frame you're observing from.

Consider these three views of the same scene with an F-shaped object and two coordinate frames:

### View from Frame 1
![Frame1 View](https://raw.githubusercontent.com/ManuGira/Coordinatus/45d97475cd735e7b580256e23fbc62d0ae5d6862/examples/frame_visualization_Frame1.png)

The F shape appears undistorted in its canonical form because it was defined using Frame 1 coordinates. From this perspective, Frame 1's axes are the standard orthogonal x and y axes at the origin. Frame 2 (green) appears in a different position and orientation relative to Frame 1.

### View from Absolute Space
![Absolute View](https://raw.githubusercontent.com/ManuGira/Coordinatus/45d97475cd735e7b580256e23fbc62d0ae5d6862/examples/frame_visualization_Absolute.png)

In absolute (world) space, we see how the F shape actually looks in reality. Frame 1 (blue) is sheared and the F inherits this shearing. Frame 2 (green) is rotated and scaled. This reveals the true geometric relationships between all elements.

### View from Frame 2  
![Frame2 View](https://raw.githubusercontent.com/ManuGira/Coordinatus/45d97475cd735e7b580256e23fbc62d0ae5d6862/examples/frame_visualization_Frame2.png)

From Frame 2's perspective, Frame 2 is now at the origin with standard axes. The same F shape appears with a completely different orientation and distortion, even though the geometry itself hasn't changed—only our reference frame has.

**Key insight:** Coordinates are not absolute—they depend on the observer. The F shape's numerical coordinates change in each view, but the shape's position in physical space remains constant. This is the essence of relative coordinate systems.

## Installation

```bash
pip install coordinatus
```

### Optional: Visualization Support

For plotting and visualization features (used in examples):

```bash
pip install coordinatus[plotting]
```

This installs matplotlib for the `coordinatus.visualization` module.

## API Overview

### Creating Frames

```python
from coordinatus import Frame, create_frame
import numpy as np

# Manually with a transform matrix
frame = Frame(transform=my_matrix, parent=parent_frame)

# Or use the convenient factory
frame = create_frame(
    parent=parent_frame,
    tx=10, ty=5,           # Translation
    angle_rad=np.pi/4,     # Rotation
    sx=2, sy=2             # Scale
)
```

### Transformation Utilities

```python
from coordinatus.transforms import translate2D, rotate2D, scale2D, trs2D

# Individual transformations (2D)
t = translate2D(tx=10, ty=5)
r = rotate2D(angle_rad=np.pi/2)
s = scale2D(sx=2, sy=3)

# Combined TRS (Translation-Rotation-Scale)
transform = trs2D(tx=10, ty=5, angle_rad=np.pi/4, sx=2, sy=2)
```

### Visualization (Optional)

```python
from coordinatus.visualization import draw_frame_axes, draw_points
import matplotlib.pyplot as plt

# Create figure
fig, ax = plt.subplots()

# Draw frames and points
draw_frame_axes(ax, frame1, color='blue', label='Frame1')
draw_frame_axes(ax, frame2, color='green', label='Frame2')
draw_points(ax, [point1, point2], color='red')

plt.show()
```

**Note:** Requires `pip install coordinatus[plotting]`

## Examples

Check out the [`examples/`](examples/) folder for complete, runnable examples:
- [nested_frames.py](examples/nested_frames.py)
- [frame_visualization.py](examples/frame_visualization.py)

## Testing

```bash
uv run pytest tests
```

## License

MIT