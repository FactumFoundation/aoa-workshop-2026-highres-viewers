#!/usr/bin/env python3
"""
render_relief.py - example: renders a shaded relief from a depth map (height map),
instead of using the shaded image exported by Selene.

By default the light comes from azimuth 45 degrees (the top right corner, measured
clockwise from the top of the image) at 45 degrees elevation. The result is an
8-bit PNG that process.py uses like Selene's shaded relief.

Examples
  python render_relief.py data/depthmap_m1.tif
  python render_relief.py data/depthmap_m1.tif --exaggeration 5
  python render_relief.py data/depthmap_m1.tif --azimuth 45 135 225 315
  python process.py data/albedo_m1.tif data/depthmap_m1_render.png
"""
import argparse
from pathlib import Path

import numpy as np
from PIL import Image

from process import hillshade, read


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("depthmap", type=Path, help="depth map: 32-bit float TIFF, or 16-bit TIFF/PNG")
    p.add_argument("--azimuth", type=float, nargs="+", default=[45.0],
                   help="light direction in degrees, clockwise from the top (45 = top right); "
                        "give several values to render several lights")
    p.add_argument("--elevation", type=float, default=45.0, help="light elevation in degrees (45 = standard)")
    p.add_argument("--exaggeration", type=float, default=1.0, help="vertical exaggeration")
    p.add_argument("--pixel-size", type=float, default=1.0,
                   help="pixel size in the same unit as the depths, e.g. 0.05 for 0.05 mm")
    p.add_argument("-o", "--output", type=Path, help="output PNG (default: next to the depth map, *_render.png)")
    a = p.parse_args()

    z = read(a.depthmap).squeeze().astype(np.float32)
    if z.ndim != 2:
        raise SystemExit(f"{a.depthmap.name} has {z.shape[-1]} channels; a depth map has only one.")
    valid = z[np.isfinite(z)]
    print(f"Depth map {z.shape[1]} x {z.shape[0]} px, depths from {valid.min():.4g} to {valid.max():.4g}")

    # Median slope, to warn when the relief would look flat
    step = max(1, int(np.sqrt(z.size / 4e6)))
    zs = np.nan_to_num(z[::step, ::step] * a.exaggeration, nan=float(np.nanmedian(valid)))
    gy, gx = np.gradient(zs, a.pixel_size * step)
    median_slope = float(np.degrees(np.arctan(np.median(np.hypot(gx, gy)))))
    print(f"Median slope: {median_slope:.2f} degrees")
    if 0 < median_slope < 2:
        hint = a.exaggeration * np.tan(np.radians(10)) / np.tan(np.radians(median_slope))
        print(f"  The relief will look flat. Try --exaggeration {hint:.3g}, or check --pixel-size.")

    for az in a.azimuth:
        shade = hillshade(z, azimuth=az, altitude=a.elevation,
                          exaggeration=a.exaggeration, pixel_size=a.pixel_size)
        out = a.output or a.depthmap.with_name(a.depthmap.stem + "_render.png")
        if len(a.azimuth) > 1:
            out = out.with_name(f"{out.stem}_az{az:g}{out.suffix}")
        Image.fromarray((shade * 255 + 0.5).astype(np.uint8)).save(out, optimize=True)
        print(f"  {out}  (azimuth {az:g}, elevation {a.elevation:g})")


if __name__ == "__main__":
    main()
