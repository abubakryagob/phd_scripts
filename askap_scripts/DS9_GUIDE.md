# Using DS9 for Time-Series FITS Analysis

This guide explains how to effectively analyze a series of FITS images with DS9, particularly for examining source variability across multiple time segments.

## Quick Start

To open all FITS files in the current directory with consistent display settings and start blinking immediately:

```bash
./ds9_blink.sh
```

This will open all FITS files with:
- Heat color map
- zscale scaling
- Region file loaded (if available)
- Frames locked for WCS coordinates
- Blink mode enabled

## Command-Line Options

You can customize the display settings:

```bash
./ds9_blink.sh --region ZTFJ1901+1458.reg --colormap heat --scale zscale
```

Available options:
- `-r, --region FILE` - Region file to load
- `-c, --colormap MAP` - Color map (heat, viridis, cool, etc.)
- `-s, --scale SCALE` - Scale method (zscale, linear, log, etc.)
- `-z, --zoom LEVEL` - Zoom level (to fit, 2, 4, etc.)

## DS9 Keyboard Shortcuts

Once DS9 is open with your FITS files, you can use:

| Key       | Function                                  |
|-----------|-------------------------------------------|
| `Space`   | Start/stop blinking frames                |
| `b`       | Enter blink mode                          |
| `+`/`-`   | Increase/decrease blink rate (in blink mode) |
| `.`/`,`   | Next/previous frame                       |
| `z`       | Enter zoom mode                           |
| `p`       | Enter pan mode                            |

## Using the DS9 GUI for Blinking

If you prefer using the DS9 GUI:

1. Launch DS9
2. Open multiple FITS files: **File → Open**
3. Load your region file: **Region → Load Region**
4. Set consistent display settings:
   - **Scale → Scale Parameters → zscale**
   - **Color → heat**
   - **Frame → Match → Frame → wcs**
   - **Frame → Lock → Scale**
   - **Frame → Lock → Colorbar**
5. Start blinking: **Frame → Blink**
6. Adjust blink rate: **Frame → Blink Interval**

## Advanced Analysis Tips

- **Tile frames** instead of blinking: **Frame → Tile** 
- **Create a mosaic**: **Frame → New Frame → Mosaic**
- **Show pixel values**: **Analysis → Pixel Table**
- **Measure source properties**: **Analysis → Imexam**
- **Create a light curve**: Select a region, then **Analysis → Statistics**
- **Match scales precisely**: Use **Frame → Match → Scale** after examining each image

## Working with Regions

To highlight your source across all frames:
1. Create a region on one frame (**Region → Shape → Circle**)
2. Save the region file (**Region → Save Region**)
3. Load the region file in all frames (**Region → Load Region**)

## Example Workflow

1. Process your measurement set with `askap_small_images.sh`
2. Create a region file for your source of interest
3. Run `./ds9_blink.sh` to examine all time segments
4. Look for frames where the source appears brighter
5. For identified frames, use DS9's analysis tools to measure flux

Happy source hunting!
