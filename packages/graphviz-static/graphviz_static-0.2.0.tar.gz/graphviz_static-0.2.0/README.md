# graphviz-static

This is a Python package for Graphviz. It has static binaries inside for easy use.

You are working in cross-platform environment, and want to use graphviz without having to install it over and over again? Well, this package allows you to enjoy that moment by simply installs every platform possible in it (yes, this is a lazy approach)

Current version of Graphviz is 14.1.1


Inspired by static-ffmpeg.





## Installation

```bash
pip install graphviz-static
```

Install this package with pip.

## Usage

```python
from graphviz_static import load_paths, export_to_image

# Start Graphviz (loads the right programs for your computer)
load_paths()

# Make a DOT file
dot_content = """
digraph G {
    node [shape=box, style=filled, color=lightblue];
    A -> B -> C;
    B -> D;
}
"""

# Save the file
with open("example.dot", "w", encoding="utf-8") as f:
    f.write(dot_content)

# Make a PNG picture
export_to_image("example.dot", "png", "output")
```

## API Reference

### `load_paths()`
This loads the right Graphviz programs for your computer and adds them to PATH.

### `export_to_image(dot_file, file_type="png", file_name="output")`
This renders your dotfile into raster image.

- `dot_file`: The path to your DOT file
- `file_type`: The image format (png, svg, pdf, etc.)
- `file_name`: The image name (without the type at the end)

This will returns your image result path.


### `get_dot_path()`
This gives you the path to the dot program for your computer.

## Supported Platforms

- Windows (32-bit and 64-bit)

## Notes

- You can use this along with official graphviz, you just need to put the `load_paths()` in the code in order to work.