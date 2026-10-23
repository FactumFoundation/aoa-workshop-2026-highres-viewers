# Photometric Stereo Web Viewer — without Python

Turn the outputs of a photometric stereo recording into full-resolution JPEGs and a deep-zoom web viewer, using Photoshop and vips. No programming is needed: two double-clicks do the technical part.

The viewer shows three perfectly aligned layers of the same piece: the **albedo** (surface colour without shadows), the **relief** (shaded surface) and the **overlay** of both. It is built with [OpenSeadragon](https://openseadragon.github.io/) and opens with a double-click, without installing anything.

## What you need

- A Windows computer.
- **Photoshop**, to prepare the images. Optional: `make_images.bat` can do the same with vips.
- **vips**, a free, open-source image tool (Step 1 explains how to get it).
- The Selene exports: the colour albedo (16-bit TIFF) and the shaded relief (PNG or TIFF). Both must have exactly the same size in pixels.
- An internet connection when opening the viewer, because it loads OpenSeadragon from a CDN.

## What is in this folder

```
wo_python/
  data/                 put the Selene exports here
  images/               albedo.jpg, relief.jpg, overlay.jpg (you create them)
  viewer/
    viewer.html         the full viewer
    viewer_minimal.html the shortest possible viewer, for teaching
    tiles/              created by make_tiles.bat
  make_images.bat       optional: Steps 2 to 4 without Photoshop
  make_tiles.bat        cuts the images into tiles for the viewer
```

## Step 1. Install vips (only once)

1. Download `vips-dev-x64-web-8.18.7.zip` (11 MB) from the releases page of [github.com/libvips/build-win64-mxe](https://github.com/libvips/build-win64-mxe/releases).
2. Unzip it to `C:\vips`. There is no installer and no administrator rights are needed.
3. Check that this file exists: `C:\vips\vips-dev-8.18\bin\vips.exe`. Both `.bat` files use that path; if you unzip it elsewhere, edit the `VIPS` line at the top of each one.

## Step 2. Prepare the albedo (Photoshop)

1. Open the albedo TIFF from `data`.
2. While still in 16 bits, adjust Levels or Curves if the image looks too dark or flat. Editing before the conversion avoids banding.
3. Go to **Edit > Convert to Profile** and choose **sRGB IEC61966-2.1**. Browsers assume sRGB, so any other profile shows wrong colours on the web.
4. Go to **Image > Mode > 8 Bits/Channel**.
5. Go to **File > Save a Copy**, choose JPEG, quality 12, and save it in `images` as `albedo.jpg`.
6. Keep this document open for Step 4.

## Step 3. Save the relief (Photoshop)

1. Open the shaded relief from `data`.
2. If the document tab shows 16 or 32 bits, go to **Image > Mode > 8 Bits/Channel**.
3. Save a copy as JPEG in `images` as `relief.jpg`.
4. Press **Ctrl+A** and then **Ctrl+C** to copy the whole image.

## Step 4. Build the overlay (Photoshop)

1. Go back to the albedo document and press **Ctrl+V**. The relief is pasted centred and aligned, because both images have the same size.
2. In the Layers panel, set the new layer to **Multiply** at **60%** opacity. Try **Soft Light** for more contrast and less darkening.
3. Zoom to 100% on a detailed area and check that the layers line up.
4. Go to **Layer > Flatten Image**.
5. Save a copy as JPEG in `images` as `overlay.jpg`.
6. Close the document without saving, so the original files stay untouched.

Tip: record Steps 2 to 4 as an Action (**Window > Actions**) to repeat them on every piece with one click.

Photoshop cannot save JPEGs larger than 30,000 px on either side. For bigger pieces, save TIFF files instead and change `EXT=jpg` to `EXT=tif` at the top of `make_tiles.bat`.

### Shortcut: Steps 2 to 4 without Photoshop

`make_images.bat` creates the same three JPEGs with vips in about 10 seconds. It is handy for a quick test or for many pieces; Photoshop gives more control over colour and the overlay. Open a Command Prompt in this folder and run it with the albedo and the relief:

```
make_images.bat data\albedo_m1.tif data\depthmap_m1_shaded.png
```

What it does: converts the albedo to 8-bit sRGB, saves the relief as a greyscale JPEG and multiplies the albedo by the relief with the same result as Multiply at 60% in Photoshop.

## Step 5. Make the tiles (vips)

1. Double-click `make_tiles.bat`.
2. It cuts `albedo`, `relief` and `overlay` into small tiles inside `viewer\tiles`, in about 2 seconds per image for a 75-megapixel piece.
3. It also writes the image size into the viewer, so there is nothing to edit by hand.

Running it again rebuilds the tiles, so repeat it after any change in Photoshop. For each image it runs this command:

```
vips dzsave images\albedo.jpg viewer\tiles\albedo --layout zoomify --suffix .jpg[Q=90]
```

## Step 6. Open the viewer

1. Double-click `viewer\viewer.html`. No server is needed.
2. To show the name of the piece, open `viewer.html` in a text editor and change `title` in the `CONFIG` block near the end.

`viewer_minimal.html` shows the shortest possible OpenSeadragon viewer, with a single layer, which is a good starting point to explain how it works.

## Using the viewer

The viewer has four modes, chosen with the buttons at the bottom of the screen or with the number keys 1 to 4.

| Mode | Key | What you see | Use it to |
| --- | --- | --- | --- |
| Albedo | 1 | The surface colour, without shadows | Study pigments, inks, inscriptions and colour variations |
| Relief | 2 | The shaded surface, in grey | Read tool marks, brushstrokes, plate marks, cracks and texture |
| Overlay | 3 | Colour and relief combined | Get a natural, readable image that shows both at once |
| Compare | 4 | Albedo with the relief faded on top | Relate a colour feature to the surface shape beneath it |

1. Start in **Albedo**. Zoom with the mouse wheel or a pinch, and drag to move around.
2. Stop on an area of interest and press **2** to switch to **Relief** without losing your position.
3. Press **3** to see the **Overlay**.
4. Press **4** for **Compare** and move the slider between Albedo and Relief to fade one into the other.
5. Use the minimap in the bottom-right corner to see where you are and jump to another area.
6. Use the buttons in the top-right corner to zoom in, zoom out, return to the full view or go full screen.

All layers are preloaded, so switching between modes is instant. On phones the minimap is hidden so it does not cover the controls.

## Publishing the viewer

The `viewer` folder is a static website: upload it as it is and it works, with nothing to install on the server.

1. Check that the viewer works on your computer first.
2. Upload the whole `viewer` folder, including `tiles`, keeping the same structure.
3. Open the address of `viewer.html` on the server.

Good options are GitHub Pages (free, for public projects), any Apache or Nginx server, or your institution's web space. The tile folders contain thousands of small files, so an FTP client is faster than uploading through a web form.

To embed the viewer in an existing web page, use an `iframe`:

```
<iframe src="viewer/viewer.html" width="100%" height="600" allowfullscreen></iframe>
```

## Troubleshooting

| Problem | Likely cause | Fix |
| --- | --- | --- |
| The viewer shows "The tiles could not be loaded" | `make_tiles.bat` has not been run, or `images` is missing a file | Check that `images` has the three JPEGs and run `make_tiles.bat` again |
| A `.bat` says it cannot find vips | vips is unzipped somewhere else | Fix the `VIPS` line at the top of the `.bat` so it points to `vips.exe` |
| The image looks stretched or cut off | The tiles were rebuilt from a different image size | Run `make_tiles.bat` again; it rewrites the size in the viewer |
| Colours look duller on the web than in Photoshop | The albedo was not converted to sRGB | Repeat **Edit > Convert to Profile > sRGB** before saving |
| The layers do not line up | The Selene exports have different sizes | Export albedo and relief at the same resolution |
| Visible bands in smooth areas | Levels were adjusted after converting to 8 bits | Adjust in 16 bits, then convert |
| Photoshop refuses to save the JPEG | The piece is over 30,000 px on one side | Save TIFF and set `EXT=tif` in `make_tiles.bat` |
| The viewer buttons have no icons, or nothing appears | No internet connection | OpenSeadragon loads from the internet; connect, or download it and point the `script` tag to the local copy |

## Credits

Developed by [Factum Foundation](https://www.factumfoundation.org) for the AOA-2026 workshop. The viewer uses [OpenSeadragon](https://openseadragon.github.io/) and the tiles are made with [libvips](https://www.libvips.org/).
