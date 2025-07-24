#!/bin/bash
# ds9_blink.sh
# This script opens all FITS files in the current directory in DS9 with consistent display settings
# and loads a region file for source examination with blinking capability.

# Default variables (change these as needed)
REGION_FILE="/Users/abubakribrahim/Desktop/observations/ASKAP/ZTFJ1901_new_data/RACS/ZTFJ1901+1458_ds9.reg"
COLOR_MAP="heat"
SCALE="minmax linear"
ZOOM="0.5"
SPECIFIC_FILES=()  # Empty array for specific FITS files to load

# Help function
show_help() {
    echo "Usage: $0 [options]"
    echo "Options:"
    echo "  -r, --region FILE    Region file to load (default: $REGION_FILE)"
    echo "  -c, --colormap MAP   Color map to use (default: $COLOR_MAP)"
    echo "  -s, --scale SCALE    Scale method to use (default: $SCALE)"
    echo "  -z, --zoom LEVEL     Zoom level (default: $ZOOM)"
    echo "  -f, --file FILE      Specific FITS file to load (can be used multiple times)"
    echo "  -h, --help           Show this help message"
    echo ""
    echo "If no specific FITS files are provided with -f, all FITS files in the current directory will be loaded."
    exit 0
}

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    key="$1"
    case $key in
        -r|--region)
            REGION_FILE="$2"
            shift 2
            ;;
        -c|--colormap)
            COLOR_MAP="$2"
            shift 2
            ;;
        -s|--scale)
            SCALE="$2"
            shift 2
            ;;
        -z|--zoom)
            ZOOM="$2"
            shift 2
            ;;
        -f|--file)
            # Add specific FITS file to the array
            if [[ -f "$2" ]]; then
                SPECIFIC_FILES+=("$2")
            else
                echo "Warning: File '$2' not found, ignoring."
            fi
            shift 2
            ;;
        -h|--help)
            show_help
            ;;
        *)
            echo "Unknown option: $1"
            show_help
            ;;
    esac
done

# Check if DS9 is installed
if ! command -v ds9 &> /dev/null; then
    echo "Error: DS9 is not installed or not in your PATH"
    exit 1
fi

# Use specific files if provided, otherwise use all FITS files in current directory
if [ ${#SPECIFIC_FILES[@]} -gt 0 ]; then
    FITS_FILES=("${SPECIFIC_FILES[@]}")
    echo "Using ${#FITS_FILES[@]} specified FITS file(s)"
else
    # Check if there are any FITS files
    FITS_FILES=(*.fits)
    if [ ${#FITS_FILES[@]} -eq 0 ] || [ ! -f "${FITS_FILES[0]}" ]; then
        echo "No FITS files found in current directory"
        exit 1
    fi
fi

# Check if region file exists
if [ ! -z "$REGION_FILE" ] && [ ! -f "$REGION_FILE" ]; then
    echo "Warning: Region file '$REGION_FILE' not found, continuing without region file"
    REGION_COMMAND=""
else
    # Add the region file command
    REGION_COMMAND="-region $REGION_FILE"
fi

# Count the number of FITS files (for status display)
NUM_FILES=${#FITS_FILES[@]}
echo "Opening $NUM_FILES FITS files in DS9 with the following settings:"
echo "- Color map: $COLOR_MAP"
echo "- Scale: $SCALE"
echo "- Region file: ${REGION_FILE:-None}"

# Build the DS9 command with all the FITS files and settings
DS9_COMMAND="/Applications/SAOImageDS9.app/Contents/MacOS/ds9"

# Add all FITS files
for file in "${FITS_FILES[@]}"; do
    DS9_COMMAND+=" \"$file\""
done

# Add display settings and blink mode
DS9_COMMAND+=" -geometry 1024x768"
DS9_COMMAND+=" -zoom $ZOOM"
DS9_COMMAND+=" -scale mode minmax"
DS9_COMMAND+=" -scale scope global"
DS9_COMMAND+=" -scale linear"
DS9_COMMAND+=" -cmap $COLOR_MAP"
DS9_COMMAND+=" -mode region"  # Activate region mode
DS9_COMMAND+=" -match frame wcs"  # Match WCS coordinates across frames
DS9_COMMAND+=" -frame lock wcs"   # Lock frames by WCS
DS9_COMMAND+=" -lock colorbar"    # Lock colorbar across all frames
DS9_COMMAND+=" -lock scale"       # Lock scale across all frames
DS9_COMMAND+=" -blink"            # Set to blink mode immediately

# Add region file if it exists
if [ ! -z "$REGION_COMMAND" ]; then
    DS9_COMMAND+=" $REGION_COMMAND"
fi

# Output the command and execute it
echo "Running: $DS9_COMMAND"
eval $DS9_COMMAND

# No temporary files to clean up now

# Additional instructions printed after launching
echo ""
echo "DS9 has been launched. You can control the blink interval using:"
echo "- Frame → Blink Interval → [select speed]"
echo "- Or press 'b' and use the + and - keys to adjust blink speed"
echo "- Press 'space' to stop/start blinking"
echo ""
echo "To match frames better, you can try:"
echo "- Frame → Match → Frame → WCS"
echo "- Frame → Lock → Scale"
echo "- Frame → Lock → Colorbar"
echo "- Region → Load Region Template → Apply to all frames"
