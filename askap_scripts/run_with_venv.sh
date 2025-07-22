#!/bin/bash

# This script runs the variability analysis using the Python virtual environment

# Set the base directory
BASE_DIR="/Users/abubakribrahim/Desktop/observations/ASKAP/ZTFJ1901_new_data/my_scripts"
VENV_DIR="$BASE_DIR/venv_variability"
SCRIPT_PATH="$BASE_DIR/analyze_variability.py"

# Source coordinates for ZTF J1901+1458
# RA: 19h01m32.9s = 285.3871 degrees
# Dec: +14d58m08.7s = 14.9691 degrees
RA=285.3871
DEC=14.9691
APERTURE_RADIUS=5  # Default aperture radius in pixels

# Function to find the FITS directory
find_fits_directory() {
  possible_dirs=(
    "."
    "./VAST"
    "./VAST/new_vast_data"
    "../VAST/new_vast_data"
  )
  
  for dir in "${possible_dirs[@]}"; do
    if ls $dir/*_t*.fits 1>/dev/null 2>&1; then
      echo "$dir"
      return 0
    fi
  done
  
  echo "Searching for time sequence FITS files..."
  fits_dir=$(find . -path "*/VAST/*" -name "*_t*.fits" -print 2>/dev/null | head -n 1 | xargs dirname 2>/dev/null)
  
  if [ -n "$fits_dir" ]; then
    echo "$fits_dir"
    return 0
  fi
  
  echo "Error: Could not find time sequence FITS files" >&2
  return 1
}

# Check if virtual environment exists
if [ ! -d "$VENV_DIR" ]; then
  echo "Python virtual environment not found."
  echo "Please run setup_env.sh first to create the environment."
  exit 1
fi

# Determine activation script
ACTIVATE_SCRIPT="$VENV_DIR/bin/activate"

# Use the current directory for FITS files
echo "Setting FITS directory path..."
FITS_DIR="$(pwd)"
# Check for FITS files with full path and wider search
FITS_COUNT=$(find "$(pwd)" -name "*.fits" | wc -l)
if [ "$FITS_COUNT" -eq 0 ]; then
  echo "Warning: No FITS files found in the current directory tree."
  echo "Please make sure you're running this script from a directory containing FITS files."
  read -p "Continue anyway? (y/n): " continue_anyway
  if [[ "$continue_anyway" != "y" && "$continue_anyway" != "Y" ]]; then
    echo "Analysis cancelled."
    exit 1
  fi
else
  echo "Found $FITS_COUNT FITS files"
fi

echo "Using FITS files in: $FITS_DIR"

# Activate virtual environment and set environment variable
echo "Activating Python virtual environment..."
source "$ACTIVATE_SCRIPT"
export VECLIB_MAXIMUM_THREADS=1

# Run the analysis
echo ""
echo "ZTF J1901+1458 Variability Analysis"
echo "=================================="
echo "Source position: RA=$RA, Dec=$DEC (J2000)"
echo "Running full variability analysis..."
cd "$(pwd)"  # Change to current directory to ensure outputs are saved here
python "$SCRIPT_PATH" "$(pwd)" "$RA" "$DEC" "$APERTURE_RADIUS"

# Check if analysis was successful
if [ $? -eq 0 ]; then
  echo ""
  echo "Variability analysis completed successfully."
  echo "Results are in:"
  echo "- variability_results.txt (numerical results)"
  echo "- ZTF_J1901_light_curve.png (light curve plot)"
  echo "- ZTF_J1901_flux_data.csv (raw measurements)"
else
  echo ""
  echo "Error: Variability analysis failed."
  echo "Check the error messages above for details."
fi
