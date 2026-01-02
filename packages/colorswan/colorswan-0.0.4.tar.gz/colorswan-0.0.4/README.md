# colorswan

**colorswan** is a precision color conversion library for Python, focused on converting sRGB to the perceptual color spaces **Oklab** and **Oklch**.

It provides accurate conversions using standard white points and matrices, suitable for color science, data visualization, and web design applications.

## Installation

```bash
pip install colorswan
```

## Usage

### Basic Conversion (Hex to Oklab/Oklch)

```python
from colorswan import OkColor

converter = OkColor()

# Convert from Hex
result = converter.convert("#FF0000") # Red
print(result)
# Output:
# {
#   'oklab': {'L': 0.6279..., 'a': 0.2248..., 'b': 0.1258...},
#   'oklch': {'L': 0.6279..., 'C': 0.2576..., 'h': 29.233...}
# }
```

### Tuple Input

You can also pass RGB tuples (0-255).

```python
# Convert from RGB Tuple
white = converter.convert((255, 255, 255))
print(white['oklab'])
# {'L': 1.0, 'a': 0.0, 'b': 0.0}
```

### Using Constants

The library exposes standard color matrices and white points.

```python
from colorswan import constants

print(constants.WHITE_POINT_D65)
# (0.95047, 1.0, 1.08883)
```

## Features
- **Accurate**: Implements the official Oklab matrices (sRGB -> Linear -> XYZ -> LMS -> Oklab).
- **Zero Dependencies**: Pure Python implementation.
- **Easy to Use**: Simple API for common color tasks.

## License
MIT
