#!/usr/bin/env python3
"""
make_tiles.py - cuts images/albedo.jpg, relief.jpg and overlay.jpg into Deep Zoom
tiles in viewer/tiles, and writes the image size into viewer/viewer.html so the
viewer opens with a double-click. Running it again rebuilds the tiles.

Example
  python make_tiles.py
"""
import argparse
import re
import shutil
from pathlib import Path

HERE = Path(__file__).resolve().parent
LAYERS = ("albedo", "relief", "overlay")


def write_size(html, width, height):
    """Replaces 'width: ...,' and 'height: ...,' in the viewer CONFIG block."""
    text = html.read_text(encoding="utf-8")
    text = re.sub(r"width: (null|\d+),", f"width: {width},", text, count=1)
    text = re.sub(r"height: (null|\d+),", f"height: {height},", text, count=1)
    html.write_text(text, encoding="utf-8")


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--images", type=Path, default=HERE / "images", help="folder with the three JPEGs")
    p.add_argument("--viewer", type=Path, default=HERE / "viewer", help="viewer folder")
    p.add_argument("--quality", type=int, default=90, help="JPEG quality of the tiles")
    a = p.parse_args()

    import pyvips   # imported here so the error message is clear if it is missing

    tiles = a.viewer / "tiles"
    tiles.mkdir(parents=True, exist_ok=True)
    size = None
    for name in LAYERS:
        src = a.images / f"{name}.jpg"
        if not src.exists():
            print(f"Missing {src} - skipped")
            continue
        shutil.rmtree(tiles / f"{name}_files", ignore_errors=True)
        (tiles / f"{name}.dzi").unlink(missing_ok=True)
        img = pyvips.Image.new_from_file(str(src), access="sequential")
        print(f"Tiling {src.name} ({img.width} x {img.height} px)")
        img.dzsave(str(tiles / name), tile_size=254, overlap=1, suffix=f".jpg[Q={a.quality}]")
        size = size or (img.width, img.height)

    if size:
        write_size(a.viewer / "viewer.html", *size)
        print(f"Image size written into the viewer: {size[0]} x {size[1]} px")
        print("Done. Double-click viewer/viewer.html")


if __name__ == "__main__":
    main()
