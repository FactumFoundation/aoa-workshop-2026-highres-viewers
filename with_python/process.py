#!/usr/bin/env python3
"""
process.py - turns photometric stereo outputs into full-resolution 8-bit JPEGs.

Inputs
  albedo   colour albedo, usually a 16-bit TIFF
  relief   either the shaded relief exported by Selene (8 or 16-bit PNG/TIFF),
           or a 32-bit floating-point height map, which is shaded here (hillshade)

Outputs (in the images folder)
  albedo.jpg, relief.jpg, overlay.jpg

Examples
  python process.py data/albedo_m1.tif data/depthmap_m1_shaded.png
  python process.py data/albedo.tif data/heights.tif --exaggeration 3 --pixel-size 0.05
"""
import argparse
from pathlib import Path

import numpy as np
import tifffile
from PIL import Image

Image.MAX_IMAGE_PIXELS = None   # pieces of several hundred megapixels
JPEG_LIMIT = 65500              # largest side the JPEG format allows
HERE = Path(__file__).resolve().parent


def read(path):
    """Reads TIFF with tifffile (keeps 16 and 32 bits) and anything else with Pillow."""
    if path.suffix.lower() in (".tif", ".tiff"):
        img = tifffile.imread(path)
        if img.ndim == 3 and img.shape[0] in (3, 4) and img.shape[-1] not in (3, 4):
            img = np.moveaxis(img, 0, -1)          # stored as channels x height x width
        return img
    return np.asarray(Image.open(path))


def to_unit(img):
    """Scales an 8-bit, 16-bit or floating-point image to the 0-1 range."""
    if img.dtype == np.uint8:
        return img.astype(np.float32) / 255.0
    if img.dtype == np.uint16:
        return img.astype(np.float32) / 65535.0
    return img.astype(np.float32)


def percentiles(img, low, high):
    """Percentiles on a subsample, so it stays fast on huge images."""
    step = max(1, int(np.sqrt(img.shape[0] * img.shape[1] / 4e6)))
    return np.nanpercentile(img[::step, ::step], [low, high])


def albedo_8bit(img, stretch=False, gamma=1.0):
    """Converts the albedo to 8 bits. With stretch, the range between the 0.1 and 99.9
    percentiles is expanded, with the same limits for all channels to keep the colour balance."""
    if img.ndim == 3:
        img = img[..., :3]                          # drop the alpha channel if there is one
    if stretch or np.issubdtype(img.dtype, np.floating):
        lo, hi = percentiles(img, 0.1, 99.9)
        x = (img.astype(np.float32) - lo) / max(hi - lo, 1e-12)
    else:
        x = to_unit(img)
    x = np.clip(x, 0, 1)
    if gamma != 1.0:
        x = x ** (1.0 / gamma)
    return (x * 255 + 0.5).astype(np.uint8)


def hillshade(z, azimuth=315.0, altitude=45.0, exaggeration=1.0, pixel_size=1.0):
    """Classic hillshade (the ESRI / gdaldem formula). Returns values from 0 to 1."""
    z = z.astype(np.float32)
    if np.isnan(z).any():
        z = np.where(np.isnan(z), np.nanmedian(z), z)
    dzdy, dzdx = np.gradient(z * exaggeration, pixel_size)
    slope = np.arctan(np.hypot(dzdx, dzdy))
    aspect = np.arctan2(dzdy, -dzdx)
    zenith = np.radians(90.0 - altitude)
    az = np.radians(360.0 - azimuth + 90.0)
    shade = (np.cos(zenith) * np.cos(slope)
             + np.sin(zenith) * np.sin(slope) * np.cos(az - aspect))
    return np.clip(shade, 0, 1).astype(np.float32)


def save_jpeg(arr, path, quality):
    h, w = arr.shape[:2]
    if max(h, w) > JPEG_LIMIT:
        raise SystemExit(f"{path.name}: {w} x {h} px is larger than JPEG allows "
                         f"({JPEG_LIMIT} px per side).")
    Image.fromarray(arr).save(path, quality=quality, subsampling=0, optimize=True)
    print(f"  {path}  ({w} x {h} px)")


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("albedo", type=Path, help="colour albedo (TIFF, 16 bits)")
    p.add_argument("relief", type=Path, help="Selene shaded relief, or a 32-bit height map")
    p.add_argument("-o", "--output", type=Path, default=HERE / "images", help="output folder")
    p.add_argument("--strength", type=float, default=0.6,
                   help="how much the relief darkens the overlay, 0-1 (0.6 = Multiply at 60%%)")
    p.add_argument("--stretch", action="store_true", help="expand the albedo contrast (percentile stretch)")
    p.add_argument("--gamma", type=float, default=1.0, help="2.2 if the albedo is linear")
    p.add_argument("--azimuth", type=float, default=315, help="height maps only: light direction in degrees")
    p.add_argument("--altitude", type=float, default=45, help="height maps only: light elevation in degrees")
    p.add_argument("--exaggeration", type=float, default=1.0, help="height maps only: vertical exaggeration")
    p.add_argument("--pixel-size", type=float, default=1.0,
                   help="height maps only: pixel size in the same unit as the heights")
    p.add_argument("--quality", type=int, default=95, help="JPEG quality")
    a = p.parse_args()
    a.output.mkdir(parents=True, exist_ok=True)

    print("Albedo...")
    albedo = albedo_8bit(read(a.albedo), a.stretch, a.gamma)
    save_jpeg(albedo, a.output / "albedo.jpg", a.quality)

    print("Relief...")
    rel = read(a.relief)
    if np.issubdtype(rel.dtype, np.floating):
        print("  32-bit height map: computing the hillshade")
        shade = hillshade(rel.squeeze(), a.azimuth, a.altitude, a.exaggeration, a.pixel_size)
    else:
        print("  shaded relief (Selene): used as it is")
        shade = to_unit(rel)
        if shade.ndim == 3:
            shade = shade[..., :3].mean(axis=2)
    del rel
    if shade.shape[:2] != albedo.shape[:2]:
        raise SystemExit(f"Size mismatch: albedo {albedo.shape[1]} x {albedo.shape[0]}, "
                         f"relief {shade.shape[1]} x {shade.shape[0]} px")
    save_jpeg((shade * 255 + 0.5).astype(np.uint8), a.output / "relief.jpg", a.quality)

    print("Overlay...")
    factor = (1.0 - a.strength) + a.strength * shade
    if albedo.ndim == 3:
        factor = factor[..., None]
    overlay = np.clip(albedo.astype(np.float32) * factor + 0.5, 0, 255).astype(np.uint8)
    save_jpeg(overlay, a.output / "overlay.jpg", a.quality)
    print("Done. Now run: python make_tiles.py")


if __name__ == "__main__":
    main()
