# Radio Variability Analysis Workflow Documentation

This document outlines the complete workflow for analyzing radio variability in ASKAP data, particularly for the ZTF J1901+1458 source.

## Overview of the Workflow

The analysis consists of two complementary approaches:

1. **Full-Field Imaging** - Creating high-quality images of the entire field using optimized parameters
2. **Time Variability Analysis** - Creating time-series images to detect variability of specific sources

## Workflow Steps

### Step 1: Initial Data Preparation

Before running any analysis, ensure the measurement set (MS) is calibrated and ready for imaging:
- Bandpass calibration
- Gain calibration
- Flux scaling
- Phase calibration

### Step 2: Field Characterization and Source Identification

Use the automated imaging script to create a high-quality image of the entire field:

```bash
cd /path/to/measurement/set/directory
/Users/abubakribrahim/Desktop/observations/ASKAP/ZTFJ1901_new_data/my_scripts/analyze_and_clean.sh your_calibrated_data.ms --auto
```

This script:
1. Analyzes the MS file properties
2. Determines optimal imaging parameters
3. Creates a cleaned image with maximum sensitivity
4. Provides a reference image for source identification

### Step 3: Time Series Image Generation

Once targets are identified, create time-series images for variability analysis:

```bash
cd /path/to/measurement/set/directory
/Users/abubakribrahim/Desktop/observations/ASKAP/ZTFJ1901_new_data/my_scripts/askap_small_images.sh your_calibrated_data.ms "YYYY/MM/DD/HH:MM:SS" total_duration interval_duration
```

Parameters:
- `your_calibrated_data.ms`: The measurement set
- `"YYYY/MM/DD/HH:MM:SS"`: Start time of the observation
- `total_duration`: Total observation duration in seconds
- `interval_duration`: Time interval for each image (e.g., 10 seconds)

This creates a series of FITS images at the specified time intervals.

### Step 4: Variability Analysis

Run the variability analysis script on the time-series images:

```bash
cd /path/to/time/series/fits/files
/Users/abubakribrahim/Desktop/observations/ASKAP/ZTFJ1901_new_data/my_scripts/run_with_venv.sh
```

This script:
1. Activates the Python environment with required packages
2. Processes all FITS images in the directory
3. Measures the flux at the source position in each image
4. Calculates variability statistics
5. Creates a light curve plot and data files

### Step 5: Results Interpretation

The analysis produces three main output files:
1. `variability_results.txt`: Summary statistics of the variability analysis
2. `ZTF_J1901_light_curve.png`: Plot of the source flux over time
3. `ZTF_J1901_flux_data.csv`: Raw flux measurements for each time step

## Technical Details

### Imaging Parameter Comparison

| Parameter | Full-Field Imaging | Time Variability Imaging |
|-----------|-------------------|-------------------------|
| Weighting | natural | briggs (robust=0.5) |
| Cell Size | auto-calculated | fixed at 2 arcsec |
| Image Size | auto-calculated | fixed at 4000 pixels |
| Threshold | 5 × RMS noise | fixed at 0.4 mJy |
| Time Selection | entire observation | 10-second intervals |

### Key Scripts

1. **analyze_and_clean.sh** - Analyzes MS and runs optimal cleaning
   - Calls `verify_params.py` to determine parameters
   - Calls `tclean_clean_image.sh` to perform cleaning

2. **askap_small_images.sh** - Creates time-series images
   - Segments data into time intervals
   - Creates FITS image for each interval
   - Uses fixed parameters for consistent comparison

3. **run_with_venv.sh** - Runs the variability analysis
   - Activates Python virtual environment
   - Calls `analyze_variability.py` to measure source flux
   - Generates plots and statistics

4. **setup_env.sh** - Creates the Python environment
   - Installs required packages (numpy, matplotlib, astropy, etc.)
   - Only needs to be run once

## Dependencies

- CASA (for imaging)
- Python 3 with:
  - numpy
  - matplotlib
  - astropy
  - photutils
  - scipy

## Troubleshooting

- If `photutils` is unavailable, the script falls back to a simpler flux extraction method
- Time variability script requires the correct observation start time format (YYYY/MM/DD/HH:MM:SS)
- Ensure the phase center coordinates match the target source position
