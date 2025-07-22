#!/bin/bash

# This script creates a Python virtual environment with all required dependencies
# for running the variability analysis script.

# Set the base directory
BASE_DIR="/Users/abubakribrahim/Desktop/observations/ASKAP/ZTFJ1901_new_data/my_scripts"
VENV_DIR="$BASE_DIR/venv_variability"
SCRIPT_PATH="$BASE_DIR/analyze_variability.py"

echo "Setting up Python environment for variability analysis..."
echo "--------------------------------------------------------"

# Check if Python 3 is available
if command -v python3 &>/dev/null; then
    PYTHON_CMD="python3"
elif command -v python &>/dev/null && python --version 2>&1 | grep -q "Python 3"; then
    PYTHON_CMD="python"
else
    echo "Error: Python 3 not found. Please install Python 3 and try again."
    exit 1
fi

echo "Using Python command: $PYTHON_CMD ($(${PYTHON_CMD} --version 2>&1))"

# Create virtual environment if it doesn't exist
if [ ! -d "$VENV_DIR" ]; then
    echo "Creating new virtual environment in $VENV_DIR..."
    $PYTHON_CMD -m venv "$VENV_DIR"
    if [ $? -ne 0 ]; then
        echo "Error: Failed to create virtual environment."
        echo "Trying alternative method with virtualenv..."
        
        # Try with virtualenv if venv fails
        if command -v pip3 &>/dev/null; then
            pip3 install virtualenv
            virtualenv -p $PYTHON_CMD "$VENV_DIR"
            if [ $? -ne 0 ]; then
                echo "Error: Failed to create virtual environment with virtualenv."
                exit 1
            fi
        else
            echo "Error: pip3 not found. Cannot install virtualenv."
            exit 1
        fi
    fi
else
    echo "Using existing virtual environment in $VENV_DIR"
fi

# Determine activation script based on OS
if [[ "$OSTYPE" == "darwin"* ]]; then
    # macOS
    ACTIVATE_SCRIPT="$VENV_DIR/bin/activate"
else
    # Linux
    ACTIVATE_SCRIPT="$VENV_DIR/bin/activate"
fi

# Activate the virtual environment and install packages
echo "Activating virtual environment and installing required packages..."
source "$ACTIVATE_SCRIPT"

# Set environment variable to avoid NumPy/Accelerate issues on macOS
export VECLIB_MAXIMUM_THREADS=1

# Install required packages
pip install --upgrade pip
pip install numpy matplotlib astropy photutils scipy

# Check installation
echo "Verifying package installation..."
python -c "import numpy; print('NumPy:', numpy.__version__)"
python -c "import matplotlib; print('Matplotlib:', matplotlib.__version__)"
python -c "import astropy; print('Astropy:', astropy.__version__)"
python -c "import photutils; print('Photutils:', photutils.__version__)"
python -c "import scipy; print('SciPy:', scipy.__version__)"

echo ""
echo "Setup complete!"
echo ""
echo "To run the variability analysis script, use:"
echo "source \"$ACTIVATE_SCRIPT\" && python \"$SCRIPT_PATH\" <path_to_fits_files> <source_ra> <source_dec> <aperture_radius>"
echo ""
echo "Example:"
echo "source \"$ACTIVATE_SCRIPT\" && python \"$SCRIPT_PATH\" ./VAST/scienceData.VAST_1856+12.SB62085.VAST_1856+12.beam20/small_images 285.3871 14.9691 5"
