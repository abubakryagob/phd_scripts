#!/bin/bash

# Check if the required arguments are provided
if [ $# -ne 4 ]; then
  echo "Usage: $0 <input_ms_file> <start_time> <total_duration> <interval_duration>"
  echo "Example: $0 scienceData.ms 2019/04/24/19:08:34 925 10"
  exit 1
fi

# Set the input MS file and other parameters
ms_file="$1"
start_time="$2" # Initial observation start time
total_duration="$3" # Total duration of observation in seconds
interval_duration="$4"  # 10-second intervals
imsize="4000"   # Image size
cell="2arcsec"     # Pixel size
weighting="briggs"
robust=0.5
stokes="I"
threshold="0.4mJy" #e.g. 0.8mJy for VLA data
phasecenter="J2000 19h01m32.9 14d58m08.7"  # Phase center based on the MS header


# Function to add seconds to a given datetime string (formatted as YYYY/MM/DD/HH:MM:SS)
add_seconds_to_datetime() {
    local datetime_str=$1
    local seconds_to_add=$2
    date -j -f "%Y/%m/%d/%H:%M:%S" -v+${seconds_to_add}S "$datetime_str" "+%Y/%m/%d/%H:%M:%S"
}

# CASA commands to be executed for each interval
for ((i=0; i<total_duration; i+=interval_duration)); do
    start_seconds=$i
    end_seconds=$((start_seconds + interval_duration))
    
    # Calculate start and end times for this interval
    start_timerange=$(add_seconds_to_datetime "$start_time" "$start_seconds")
    end_timerange=$(add_seconds_to_datetime "$start_time" "$end_seconds")
    
    timerange="${start_timerange}~${end_timerange}"
    
    imagename="${ms_file%.ms}_duration-${total_duration}sec_interval-${interval_duration}sec_t$(printf "%04d" $((i/interval_duration)))"  # Similar to cyga-t0000 in WSClean
    
    casa_commands=$(cat <<EOF
print("Running tclean for time interval: ${timerange}...")
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

EOF
    )
    
    # Run CASA with the constructed commands
    /Applications/CASA.app/Contents/MacOS/casa --nologger --nogui -c "$casa_commands"
    
    # Delete unnecessary files but keep .image and .fits
    rm -rf ${imagename}.psf ${imagename}.pb ${imagename}.sumwt ${imagename}.residual ${imagename}.model 
done
