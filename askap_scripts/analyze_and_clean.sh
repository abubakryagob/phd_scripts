#!/bin/bash

# Automated CASA analysis and cleaning script
# Usage: ./analyze_and_clean.sh <ms_file> [--auto]

if [ $# -lt 1 ]; then
    echo "Usage: $0 <ms_file> [--auto]"
    echo ""
    echo "Examples:"
    echo "  $0 data.ms                    # Analysis only"
    echo "  $0 data.ms --auto             # Analysis + automatic tclean"
    echo ""
    exit 1
fi

MS_FILE="$1"
AUTO_FLAG=""

if [ "$2" == "--auto" ]; then
    AUTO_FLAG="--auto"
fi

# Get the directory of this script
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Check if MS file exists
if [ ! -d "$MS_FILE" ]; then
    echo "Error: Measurement Set '$MS_FILE' not found"
    exit 1
fi

echo "=== CASA Automated Analysis and Cleaning ==="
echo "MS File: $MS_FILE"
if [ -n "$AUTO_FLAG" ]; then
    echo "Mode: Analysis + Automatic tclean"
else
    echo "Mode: Analysis only"
fi
echo ""

# Run CASA with the verification script
if [ -n "$AUTO_FLAG" ]; then
    /Applications/CASA.app/Contents/MacOS/casa --nologger --nogui -c "
import sys
sys.argv = ['verify_params.py', '$MS_FILE', '--auto']
exec(open('$SCRIPT_DIR/verify_params.py').read())
"
else
    /Applications/CASA.app/Contents/MacOS/casa --nologger --nogui -c "
import sys
sys.argv = ['verify_params.py', '$MS_FILE']
exec(open('$SCRIPT_DIR/verify_params.py').read())
"
fi
