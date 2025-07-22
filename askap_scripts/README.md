# ZTF J1901+1458 Variability Analysis

This directory contains scripts to analyze the time variability of ZTF J1901+1458 using ASKAP data.

## Scripts Overview

- **analyze_variability.py**: Main analysis script that processes FITS images, measures flux, and calculates variability statistics
- **setup_env.sh**: Creates a Python virtual environment with all required dependencies
- **run_with_venv.sh**: Runs the analysis script with the proper environment settings

## How to Run the Analysis

### First-time Setup

1. Make sure the scripts are executable:
   ```bash
   chmod +x setup_env.sh run_with_venv.sh
   ```

2. Set up the Python environment (only needs to be done once):
   ```bash
   cd /Users/abubakribrahim/Desktop/observations/ASKAP/ZTFJ1901_new_data/my_scripts
   ./setup_env.sh
   ```

### Running the Analysis

1. Navigate to the directory containing your FITS files:
   ```bash
   cd /path/to/your/fits/files
   ```

2. Run the variability analysis from that directory:
   ```bash
   /Users/abubakribrahim/Desktop/observations/ASKAP/ZTFJ1901_new_data/my_scripts/run_with_venv.sh
   ```

3. The output files will be saved in the current directory (where your FITS files are).

## Output Files

The analysis generates three output files in the directory where you run the script (where your FITS files are located):

1. **variability_results.txt**: Summary of variability statistics
2. **ZTF_J1901_light_curve.png**: Plot of the light curve
3. **ZTF_J1901_flux_data.csv**: Raw flux measurements for each time step

## Source Information

- **Source Name**: ZTF J1901+1458
- **RA**: 285.3871° (19h01m32.9s)
- **Dec**: 14.9691° (+14°58'08.7")

## Example Usage

For example, to analyze data for beam07:

```bash
cd /Users/abubakribrahim/Desktop/observations/ASKAP/ZTFJ1901_new_data/VAST/scienceData.VAST_1856+12.SB62085.VAST_1856+12.beam07/small_images
/Users/abubakribrahim/Desktop/observations/ASKAP/ZTFJ1901_new_data/my_scripts/run_with_venv.sh
```

This will create the output files directly in the beam07/small_images directory.
