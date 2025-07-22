# Complete ASKAP Radio Variability Analysis Workflow

This document provides a comprehensive guide to the complete workflow for analyzing radio variability in ASKAP data, particularly focused on the ZTF J1901+1458 source.

## 1. Workflow Overview

The analysis consists of two complementary approaches:

1. **Full-Field High-Quality Imaging** - Creating detailed images of the entire field with optimized parameters
2. **Time-Series Variability Analysis** - Creating time-segmented images to detect variability of specific sources

![Workflow Diagram](workflow_diagram.png)

## 2. Step-by-Step Workflow

### 2.1 Initial Data Preparation

Before running any analysis, ensure the measurement set (MS) is calibrated:

```bash
# Data should already be calibrated with:
# - Bandpass calibration
# - Gain calibration
# - Flux scaling
# - Phase calibration
```

### 2.2 Full-Field High-Quality Imaging

To create a high-quality image of the entire field:

```bash
cd /path/to/measurement/set/directory
/path/to/my_scripts/tclean_clean_image.sh your_calibrated_data.ms
```

This creates a high-quality reference image for source identification.

### 2.3 Time-Series Image Generation

The enhanced `askap_small_images.sh` script now automatically extracts timing information:

```bash
cd /path/to/measurement/set/directory

# Basic usage - auto-extracts timing info
/path/to/my_scripts/askap_small_images.sh your_calibrated_data.ms

# With custom settings
/path/to/my_scripts/askap_small_images.sh your_calibrated_data.ms --interval 10 --parallel 4
```

This creates a series of FITS images at the specified time intervals.

### 2.4 Variability Analysis

Run the variability analysis on the time-series images:

```bash
cd /path/to/time/series/fits/files
/path/to/my_scripts/run_with_venv.sh
```

This measures flux at the source position in each image and creates light curve plots.

## 3. Technical Implementation Details

### 3.1 Auto-Extraction Features

The `askap_small_images.sh` script includes several auto-extraction features:

#### Timing Information:
- Automatically reads the observation start time
- Calculates total observation duration
- Determines appropriate time interval boundaries

#### Phase Center:
- Extracts field center coordinates from MS metadata
- Formats them properly for CASA's tclean
- Falls back to default if extraction fails

### 3.2 Imaging Parameter Comparison

| Parameter | Full-Field Imaging | Time Variability Imaging |
|-----------|-------------------|-------------------------|
| Weighting | natural | briggs (robust=0.5) |
| Cell Size | auto-calculated | fixed at 2 arcsec |
| Image Size | auto-calculated | fixed at 4000 pixels |
| Threshold | 5 × RMS noise | fixed at 0.4 mJy |
| Time Selection | entire observation | configurable intervals |
| Parallelization | single image | multiple parallel images |

## 4. Advanced Customization

### 4.1 Controlling Image Quality

To customize image quality parameters:

```bash
/path/to/my_scripts/askap_small_images.sh your_calibrated_data.ms \
  --imsize 6000 \
  --cell 1.5arcsec \
  --robust 0.2 \
  --threshold 0.3mJy
```

### 4.2 Managing Resource Usage

For resource-intensive processing:

```bash
/path/to/my_scripts/askap_small_images.sh your_calibrated_data.ms \
  --parallel 8 \         # Increase for faster processing on powerful systems
  --interval 60 \        # Larger intervals require less processing
  --cleanup full         # Save disk space by removing intermediate files
```

## 5. Interpreting Results

The analysis produces several output files:

1. **FITS images** for each time segment
2. **Light curve plot** showing flux vs. time
3. **Variability statistics** in text format
4. **Log files** with processing details

## 6. Troubleshooting

| Issue | Solution |
|-------|----------|
| Missing dependencies | Run `setup_env.sh` to create the Python environment |
| Processing errors | Check the log files in `logs_YYYYMMDD_HHMMSS` directory |
| Auto-extraction fails | Provide parameters manually with `--start-time`, `--total-duration`, and `--phase-center` |
| Out of memory | Increase interval size or reduce parallel jobs |

## 7. References and Resources

- [CASA Documentation](https://casa.nrao.edu/casadocs/)
- [ASKAP Documentation](https://www.atnf.csiro.au/computing/software/askapsoft/sdp/docs/current/index.html)
- [Astropy Documentation](https://docs.astropy.org/)
