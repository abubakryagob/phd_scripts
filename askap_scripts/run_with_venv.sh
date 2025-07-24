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

# Function to display help
show_help() {
  echo "Usage: $0 [options]"
  echo ""
  echo "Options:"
  echo "  -f, --fits FILE1 [FILE2...]  Specify specific FITS files to analyze"
  echo "  -r, --radius NUM             Set aperture radius in pixels (default: 5)"
  echo "  -h, --help                   Display this help message"
  echo ""
  echo "Examples:"
  echo "  $0                           Analyze all FITS files in current directory"
  echo "  $0 -f image1.fits image2.fits  Analyze only specified FITS files"
  exit 0
}

# Array to hold specific FITS files if provided
SPECIFIC_FITS_FILES=()

# Parse command line arguments
while [[ $# -gt 0 ]]; do
  case $1 in
    -f|--fits)
      # Collect all FITS files until the next option
      shift
      while [[ $# -gt 0 && ! $1 =~ ^- ]]; do
        SPECIFIC_FITS_FILES+=("$1")
        shift
      done
      ;;
    -r|--radius)
      APERTURE_RADIUS="$2"
      shift 2
      ;;
    -h|--help)
      show_help
      ;;
    *)
      # Unknown option
      echo "Unknown option: $1"
      echo "Use -h or --help to see available options."
      shift
      ;;
  esac
done

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

# Build the command depending on whether specific files were provided
COMMAND="python \"$SCRIPT_PATH\" \"$(pwd)\" \"$RA\" \"$DEC\" \"$APERTURE_RADIUS\""

if [ ${#SPECIFIC_FITS_FILES[@]} -gt 0 ]; then
  echo "Running analysis on ${#SPECIFIC_FITS_FILES[@]} specified FITS files..."
  COMMAND="$COMMAND --fits"
  for file in "${SPECIFIC_FITS_FILES[@]}"; do
    COMMAND="$COMMAND \"$file\""
  done
else
  echo "Running analysis on all FITS files in directory..."
fi

cd "$(pwd)"  # Change to current directory to ensure outputs are saved here
eval $COMMAND

# Check if analysis was successful
if [ $? -eq 0 ]; then
  echo ""
  echo "Variability analysis completed successfully."
  echo "Results are in files named with the MS identifier for each MS source detected:"
  echo "- variability_results_[MS_NAME].txt (numerical results)"
  echo "- ZTF_J1901_[MS_NAME]_light_curve.png (light curve plot)"
  echo "- ZTF_J1901_[MS_NAME]_flux_data.csv (raw measurements)"
  echo ""
  echo "Note: If multiple MS sources were detected in your FITS files,"
  echo "separate output files have been created for each source."
else
  echo ""
  echo "Error: Variability analysis failed."
  echo "Check the error messages above for details."
fi
