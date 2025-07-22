#!/bin/bash

# ASKAP Time-Series Imaging Script
# This script creates time-segmented images from a measurement set (MS) file
# for the purpose of variability analysis.

# Default values
CASA_PATH="/Applications/CASA.app/Contents/MacOS/casa"
MAX_PARALLEL_JOBS=4
CLEANUP_LEVEL="minimal"  # Options: none, minimal, full

# Print usage information
usage() {
    echo "ASKAP Time-Series Imaging Script"
    echo "-------------------------------"
    echo "Usage: $0 <input_ms_file> [OPTIONS]"
    echo ""
    echo "Required Arguments:"
    echo "  <input_ms_file>     Path to the input MS file"
    echo ""
    echo "Options:"
    echo "  --start-time TIME   Initial observation start time (YYYY/MM/DD/HH:MM:SS)"
    echo "                      If not specified, auto-extracted from MS"
    echo "  --total-duration N  Total duration of observation in seconds" 
    echo "                      If not specified, auto-extracted from MS"
    echo "  --interval N        Time interval for each image in seconds (default: 30)"
    echo "  --casa-path PATH    Path to CASA executable (default: $CASA_PATH)"
    echo "  --parallel N        Maximum number of parallel jobs (default: $MAX_PARALLEL_JOBS)"
    echo "  --imsize SIZE       Image size in pixels (default: 4000)"
    echo "  --cell SIZE         Cell size (default: 2arcsec)"
    echo "  --robust VALUE      Robust parameter for Briggs weighting (default: 0.5)"
    echo "  --threshold VALUE   Clean threshold (default: 0.4mJy)"
    echo "  --phase-center POS  Phase center (default: auto-extract from MS)"
    echo "  --cleanup LEVEL     Cleanup level: none, minimal, full (default: $CLEANUP_LEVEL)"
    echo "  --help              Display this help and exit"
    echo ""
    echo "Examples:"
    echo "  # Auto-extract timing with default settings:"
    echo "  $0 scienceData.ms"
    echo ""
    echo "  # Auto-extract timing with custom settings:"
    echo "  $0 scienceData.ms --interval 10 --parallel 6 --cleanup minimal"
    echo ""
    echo "  # Manual specification of all parameters:"
    echo "  $0 scienceData.ms --start-time 2019/04/24/19:08:34 --total-duration 925 --interval 10"
    exit 1
}

# Parse command line arguments
if [ $# -lt 1 ]; then
    usage
fi

# Set the required parameters
ms_file="$1"
shift 1

# Default interval duration (can be overridden with --interval option)
interval_duration=30

# Flag to indicate if auto-extraction of timing info should be done
AUTO_EXTRACT_TIMING=true

# Default imaging parameters
imsize="4000"     # Image size
cell="2arcsec"    # Pixel size
weighting="briggs"
robust=0.5
stokes="I"
threshold="0.4mJy"
phasecenter="auto" # Auto-extract from MS by default

# Parse optional arguments
while [ $# -gt 0 ]; do
    case "$1" in
        --casa-path)
            CASA_PATH="$2"
            shift 2
            ;;
        --parallel)
            MAX_PARALLEL_JOBS="$2"
            shift 2
            ;;
        --imsize)
            imsize="$2"
            shift 2
            ;;
        --cell)
            cell="$2"
            shift 2
            ;;
        --robust)
            robust="$2"
            shift 2
            ;;
        --threshold)
            threshold="$2"
            shift 2
            ;;
        --phase-center)
            phasecenter="$2"
            shift 2
            ;;
        --cleanup)
            CLEANUP_LEVEL="$2"
            shift 2
            ;;
        --interval)
            interval_duration="$2"
            shift 2
            ;;
        --start-time)
            start_time="$2"
            AUTO_EXTRACT_TIMING=false
            shift 2
            ;;
        --total-duration)
            total_duration="$2"
            AUTO_EXTRACT_TIMING=false
            shift 2
            ;;
        --help)
            usage
            ;;
        *)
            echo "Unknown option: $1"
            usage
            ;;
    esac
done

# Validate inputs
if [ ! -d "$ms_file" ]; then
    echo "Error: MS file '$ms_file' not found or not a directory."
    exit 1
fi

if [ ! -x "$CASA_PATH" ]; then
    echo "Error: CASA executable not found or not executable at '$CASA_PATH'."
    echo "Use --casa-path to specify the correct path."
    exit 1
fi

# Extract timing information from MS if auto extraction is enabled
if [ "$AUTO_EXTRACT_TIMING" = true ]; then
    echo "Extracting timing information from measurement set..."
    
    # Create temporary script to extract time information (compatible with both Python 2 and 3)
    tmp_time_script=$(mktemp)
    cat > "$tmp_time_script" <<EOF
import sys
import numpy as np

try:
    # Use casatools or casacore depending on CASA version
    try:
        from casatools import table
        tb = table()
    except ImportError:
        from casacore.tables import table
        tb = table

    # Open the measurement set
    if callable(getattr(tb, 'open', None)):
        # CASA 6 style
        tb.open('$ms_file')
        times = tb.getcol('TIME')
        tb.close()
    else:
        # casacore style
        t = table('$ms_file')
        times = t.getcol('TIME')
        t.close()
    
    # Calculate timing information
    first_time = times[0]
    last_time = times[-1]
    duration = last_time - first_time
    num_timesteps = len(set(times))
    
    # Convert MJD seconds to ISO format
    try:
        from astropy.time import Time
        t = Time(first_time/86400.0, format='mjd')
        iso_date = t.iso
    except ImportError:
        # Fallback if astropy is not available
        import datetime
        # MJD starts at November 17, 1858
        base = datetime.datetime(1858, 11, 17)
        delta = datetime.timedelta(seconds=first_time)
        dt = base + delta
        iso_date = dt.strftime('%Y-%m-%d %H:%M:%S')
    
    # Format as YYYY/MM/DD/HH:MM:SS for the script
    year = iso_date[0:4]
    month = iso_date[5:7]
    day = iso_date[8:10]
    hour = iso_date[11:13]
    minute = iso_date[14:16]
    second = iso_date[17:19]
    
    formatted_date = "{}/{}/{}/{}:{}:{}".format(year, month, day, hour, minute, second)
    
    print("START_TIME={}".format(formatted_date))
    print("TOTAL_DURATION={}".format(int(np.ceil(duration))))
    print("NUM_TIMESTEPS={}".format(num_timesteps))
    
except Exception as e:
    if sys.version_info[0] >= 3:
        print("ERROR: Failed to extract timing information: {}".format(e), file=sys.stderr)
    else:
        sys.stderr.write("ERROR: Failed to extract timing information: {}\n".format(e))
    sys.exit(1)
EOF
    
    # Run the script and capture output
    timing_info=$("$CASA_PATH" --nologger --nogui -c "$tmp_time_script" 2>/dev/null)
    timing_status=$?
    
    # Clean up temporary script
    rm -f "$tmp_time_script"
    
    if [ $timing_status -ne 0 ]; then
        echo "Error: Failed to extract timing information from MS. Please specify --start-time and --total-duration manually."
        exit 1
    fi
    
    # Parse the output
    eval "$timing_info"
    
    # Set the variables from the extracted info
    start_time="$START_TIME"
    total_duration="$TOTAL_DURATION"
    
    echo "Successfully extracted timing information:"
    echo "  Start time: $start_time"
    echo "  Total duration: $total_duration seconds"
    echo "  Number of timesteps: $NUM_TIMESTEPS"
else
    # Validate manually provided timing information
    if [ -z "$start_time" ]; then
        echo "Error: Start time not specified. Use --start-time or enable auto extraction."
        exit 1
    fi
    
    if [ -z "$total_duration" ]; then
        echo "Error: Total duration not specified. Use --total-duration or enable auto extraction."
        exit 1
    fi
fi

# Validate parameters
if ! [[ "$total_duration" =~ ^[0-9]+$ ]] || [ "$total_duration" -le 0 ]; then
    echo "Error: Total duration must be a positive integer."
    exit 1
fi

if ! [[ "$interval_duration" =~ ^[0-9]+$ ]] || [ "$interval_duration" -le 0 ]; then
    echo "Error: Interval duration must be a positive integer."
    exit 1
fi

if [ "$interval_duration" -gt "$total_duration" ]; then
    echo "Error: Interval duration cannot be greater than total duration."
    exit 1
fi

# Check for valid cleanup level
if [[ ! "$CLEANUP_LEVEL" =~ ^(none|minimal|full)$ ]]; then
    echo "Error: Invalid cleanup level. Use 'none', 'minimal', or 'full'."
    exit 1
fi

# Extract phase center from MS if set to auto
if [ "$phasecenter" == "auto" ]; then
    echo "Extracting phase center from MS metadata..."
    # Create a temporary script to extract phase center (compatible with both Python 2 and 3)
    tmp_script=$(mktemp)
    cat > "$tmp_script" <<EOF
import sys
from casacore.tables import table
try:
    with table('$ms_file/FIELD', readonly=True) as t:
        if t.nrows() > 0:
            direction = t.getcol('PHASE_DIR')[0][0]
            ra_rad, dec_rad = direction
            ra_deg = ra_rad * 180.0 / 3.14159265358979
            dec_deg = dec_rad * 180.0 / 3.14159265358979
            ra_hms = ra_deg / 15.0  # Convert to hours
            ra_h = int(ra_hms)
            ra_m = int((ra_hms - ra_h) * 60)
            ra_s = ((ra_hms - ra_h) * 60 - ra_m) * 60
            dec_d = int(dec_deg)
            dec_m = int(abs((dec_deg - dec_d) * 60))
            dec_s = abs((abs(dec_deg) - abs(dec_d) - dec_m/60.0) * 3600)
            # Use Python 2 and 3 compatible string formatting
            print("J2000 {0:02d}h{1:02d}m{2:.2f}s {3:+03d}d{4:02d}m{5:.2f}s".format(
                ra_h, ra_m, ra_s, dec_d, dec_m, dec_s))
        else:
            print("No field data found")
            sys.exit(1)
except Exception as e:
    print("Error extracting phase center: {}".format(e))
    sys.exit(1)
EOF
    phasecenter=$(python "$tmp_script")
    if [ $? -ne 0 ]; then
        echo "Failed to extract phase center automatically. Please specify with --phase-center."
        echo "Using default phase center: J2000 19h01m32.9s +14d58m08.7s"
        phasecenter="J2000 19h01m32.9s +14d58m08.7s"
    else
        echo "Using phase center: $phasecenter"
    fi
    rm -f "$tmp_script"
fi


# Function to add seconds to a given datetime string (formatted as YYYY/MM/DD/HH:MM:SS)
add_seconds_to_datetime() {
    local datetime_str=$1
    local seconds_to_add=$2
    
    # Check if we're on macOS (uses -j -f and -v) or Linux (uses -d)
    if [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS version
        date -j -f "%Y/%m/%d/%H:%M:%S" -v+${seconds_to_add}S "$datetime_str" "+%Y/%m/%d/%H:%M:%S"
    else
        # Linux version
        date -d "$datetime_str +$seconds_to_add seconds" "+%Y/%m/%d/%H:%M:%S"
    fi
}

# Create a directory for logs
log_dir="./logs_$(date +%Y%m%d_%H%M%S)"
mkdir -p "$log_dir"
echo "Log files will be stored in: $log_dir"

# Function to process a single time interval
process_interval() {
    local i=$1
    local start_seconds=$i
    local end_seconds=$((start_seconds + interval_duration))
    
    # Calculate start and end times for this interval
    local start_timerange=$(add_seconds_to_datetime "$start_time" "$start_seconds")
    local end_timerange=$(add_seconds_to_datetime "$start_time" "$end_seconds")
    local timerange="${start_timerange}~${end_timerange}"
    
    local imagename="${ms_file%.ms}_duration-${total_duration}sec_interval-${interval_duration}sec_t$(printf "%04d" $((i/interval_duration)))"
    local log_file="$log_dir/interval_$(printf "%04d" $((i/interval_duration))).log"
    
    echo "[$(date +%H:%M:%S)] Processing interval $((i/interval_duration+1))/$((total_duration/interval_duration)) (${timerange})"
    
    # Create CASA script file for this interval
    local casa_script="${log_dir}/casa_script_$(printf "%04d" $((i/interval_duration))).py"
    cat > "$casa_script" <<EOF
print("Running tclean for time interval: ${timerange}...")
try:
    tclean(
        vis='$ms_file',
        imagename='$imagename',
        imsize=[${imsize}],
        cell=['${cell}'],
        weighting='${weighting}',
        robust=${robust},
        stokes='${stokes}',
        niter=0,                   # Number of cleaning iterations
        threshold='${threshold}',
        interactive=False,
        timerange='${timerange}',
        gridder='standard',
        datacolumn='corrected',
        phasecenter='${phasecenter}',
        savemodel='none'
    )
    print("tclean imaging completed for time interval: ${timerange}.")
    
    print("Converting CASA image to FITS format...")
    exportfits(
        imagename='${imagename}.image',
        fitsimage='${imagename}.fits',
        overwrite=True
    )
    print("FITS image created: ${imagename}.fits")
    
    # Cleanup based on selected level
    if '$CLEANUP_LEVEL' == 'minimal':
        import os
        import shutil
        os.system('rm -rf ${imagename}.psf ${imagename}.pb ${imagename}.sumwt ${imagename}.residual ${imagename}.model')
    elif '$CLEANUP_LEVEL' == 'full':
        import os
        import shutil
        os.system('rm -rf ${imagename}.psf ${imagename}.pb ${imagename}.sumwt ${imagename}.residual ${imagename}.model ${imagename}.image')
    
    print("Processing complete for interval: ${timerange}")
    
except Exception as e:
    print("ERROR processing interval ${timerange}: " + str(e))
    sys.exit(1)
EOF
    
    # Run CASA with the script
    "$CASA_PATH" --nologger --nogui -c "$casa_script" > "$log_file" 2>&1
    local status=$?
    
    if [ $status -eq 0 ]; then
        echo "[$(date +%H:%M:%S)] ✓ Successfully completed interval $((i/interval_duration+1))/$((total_duration/interval_duration))"
    else
        echo "[$(date +%H:%M:%S)] ✗ Failed to process interval $((i/interval_duration+1))/$((total_duration/interval_duration)). See $log_file for details."
    fi
    
    return $status
}

# Calculate total number of intervals
total_intervals=$((total_duration / interval_duration))
echo "Processing $total_intervals intervals of $interval_duration seconds each"
echo "Starting time: $start_time"
echo "Phase center: $phasecenter"
echo "Image size: ${imsize}px, Cell: ${cell}, Weighting: ${weighting} (robust=$robust)"

# Process intervals in parallel with limited concurrency
echo "[$(date +%H:%M:%S)] Starting processing with max $MAX_PARALLEL_JOBS parallel jobs..."

# Track running jobs and their PIDs
declare -a job_pids=()
declare -a job_intervals=()
failed_intervals=0

# Process all intervals
for ((i=0; i<total_duration; i+=interval_duration)); do
    # Wait if we already have max jobs running
    while [ ${#job_pids[@]} -ge $MAX_PARALLEL_JOBS ]; do
        for j in "${!job_pids[@]}"; do
            if ! kill -0 ${job_pids[$j]} 2>/dev/null; then
                # Check if the job completed successfully
                wait ${job_pids[$j]}
                status=$?
                if [ $status -ne 0 ]; then
                    echo "[$(date +%H:%M:%S)] ⚠️ Interval ${job_intervals[$j]} failed with status $status"
                    ((failed_intervals++))
                fi
                
                # Remove this job from the tracking arrays
                unset job_pids[$j]
                unset job_intervals[$j]
                job_pids=("${job_pids[@]}")  # Reindex array
                job_intervals=("${job_intervals[@]}")  # Reindex array
                break
            fi
        done
        # Short sleep to prevent CPU thrashing
        sleep 0.5
    done
    
    # Start a new job
    process_interval $i &
    job_pid=$!
    job_pids+=($job_pid)
    job_intervals+=($((i/interval_duration+1)))
done

# Wait for remaining jobs to complete
echo "[$(date +%H:%M:%S)] All intervals submitted, waiting for remaining jobs to complete..."
for j in "${!job_pids[@]}"; do
    wait ${job_pids[$j]}
    status=$?
    if [ $status -ne 0 ]; then
        echo "[$(date +%H:%M:%S)] ⚠️ Interval ${job_intervals[$j]} failed with status $status"
        ((failed_intervals++))
    fi
done

# Final summary
echo ""
echo "=== Processing Summary ==="
echo "Total intervals: $total_intervals"
echo "Failed intervals: $failed_intervals"
echo "Successful intervals: $((total_intervals - failed_intervals))"
echo "Log directory: $log_dir"
echo ""

if [ $failed_intervals -eq 0 ]; then
    echo "✅ All intervals processed successfully!"
else
    echo "⚠️ $failed_intervals intervals failed. Check logs for details."
    exit 1
fi
