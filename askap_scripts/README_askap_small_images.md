# ASKAP Time-Series Imaging Script

## Overview

This script creates time-segmented images from a measurement set (MS) file for the purpose of radio source variability analysis. It divides the observation into short time segments and creates a separate image for each segment.

## Key Features

- **Parallel Processing**: Process multiple time segments simultaneously for faster imaging
- **Automatic Parameter Detection**: Auto-extracts timing information and phase center from MS metadata
- **Flexible Cleanup Options**: Control how much disk space to save after processing
- **Cross-Platform Support**: Works on both macOS and Linux systems
- **Detailed Logging**: Creates logs for each time segment for easier troubleshooting
- **Progress Reporting**: Shows real-time progress and summary statistics
- **Smart Defaults**: Minimal required input with reasonable defaults

## Requirements

- CASA (Common Astronomy Software Applications) installed
- Python with casacore installed (for automatic phase center extraction)
- A calibrated measurement set (MS) file

## Basic Usage

```bash
./askap_small_images.sh <ms_file> [options]
```

The script automatically extracts timing information from the measurement set!

Examples:
```bash
# Simplest usage - auto-extracts timing with default settings (30-second intervals)
./askap_small_images.sh scienceData.ms

# Auto-extract timing with custom interval
./askap_small_images.sh scienceData.ms --interval 10

# Auto-extract timing with parallel processing and cleanup options
./askap_small_images.sh scienceData.ms --interval 10 --parallel 4 --cleanup minimal
```

## Advanced Options

```
# Timing Options (all auto-extracted by default)
--start-time TIME   Initial observation start time (YYYY/MM/DD/HH:MM:SS)
--total-duration N  Total duration of observation in seconds
--interval N        Time interval for each image in seconds (default: 30)

# Processing Options
--casa-path PATH    Path to CASA executable (default: /Applications/CASA.app/Contents/MacOS/casa)
--parallel N        Maximum number of parallel jobs (default: 4)
--imsize SIZE       Image size in pixels (default: 4000)
--cell SIZE         Cell size (default: 2arcsec)
--robust VALUE      Robust parameter for Briggs weighting (default: 0.5)
--threshold VALUE   Clean threshold (default: 0.4mJy)
--phase-center POS  Phase center (default: auto-extract from MS)
--cleanup LEVEL     Cleanup level: none, minimal, full (default: minimal)
--help              Display help and exit
```

Examples with advanced options:

```bash
# Custom imaging parameters with auto-extracted timing
./askap_small_images.sh scienceData.ms \
  --parallel 8 \
  --imsize 5000 \
  --cell 1arcsec \
  --cleanup full

# Manual specification of all parameters
./askap_small_images.sh scienceData.ms \
  --start-time 2019/04/24/19:08:34 \
  --total-duration 925 \
  --interval 10 \
  --parallel 4
```

## Output

For each time segment, the script creates:
- `.image` files (CASA image format)
- `.fits` files (standard FITS format for analysis)

With default cleanup settings (`minimal`), the script removes temporary files but keeps both the `.image` and `.fits` files.

## Auto-Extraction Details

The script automatically extracts important information from the MS file:

1. **Timing Information**:
   - Start time of the observation
   - Total duration of the observation
   - Number of timesteps available

2. **Phase Center**:
   - Coordinates of the field center
   - Properly formatted for CASA's tclean

This eliminates the need to manually check the MS file with `listobs` or similar tools before running the script.

## Troubleshooting

- If processing fails, check the log files in the `logs_YYYYMMDD_HHMMSS` directory
- If automatic phase center extraction fails, provide it manually using `--phase-center`
- Adjust the number of parallel jobs based on your system's capabilities
- If Python 2/3 compatibility issues arise, try with explicit timing parameters
- For large MS files, auto-extraction may take a moment - be patient
- When using very small interval sizes, increase memory resources if needed
