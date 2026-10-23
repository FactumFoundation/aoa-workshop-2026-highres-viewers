# Photometric Stereo Web Viewer

Workshop materials for turning photometric stereo recordings into deep-zoom web viewers, prepared by [Factum Foundation](https://www.factumfoundation.org) for the AOA-2026 workshop.

A photometric stereo recording, such as one made with Selene, produces a colour **albedo** (the surface colour without shadows) and a **relief** (the shape of the surface, shown as a shaded image). These materials turn both into full-resolution JPEGs, combine them into an **overlay**, and publish the three layers in a web viewer built with [OpenSeadragon](https://openseadragon.github.io/), where they stay perfectly aligned and you can switch between them while zooming.

## Two independent versions

Each folder is self-contained, with its own step-by-step tutorial (`README.md`, also as `TUTORIAL.pdf`), scripts and viewer. Pick one:

| | [`with_python`](with_python) | [`wo_python`](wo_python) |
| --- | --- | --- |
| For | People comfortable with a terminal | People who prefer visual tools, with no coding |
| Image preparation | `process.py` | Photoshop, or `make_images.bat` |
| Tiling | `make_tiles.py` (pyvips) | `make_tiles.bat` (vips) |
| Tile format | Deep Zoom (DZI) | Zoomify |
| Relief input | Selene shaded relief, or a 32-bit height map | Selene shaded relief |
| System | Windows, macOS, Linux | Windows |

Both produce the same images and the same viewer, which opens with a double-click and can be uploaded as it is to any static web hosting.

## Viewer

The viewer has four modes, switched with the buttons or the keys 1 to 4: **Albedo**, **Relief**, **Overlay**, and **Compare**, which fades the relief over the albedo with a slider.

## Data

Recordings are not included in this repository. Put your own files in the `data` folder of the version you use; the `data`, `images` and `viewer/tiles` folders are ignored by git.
