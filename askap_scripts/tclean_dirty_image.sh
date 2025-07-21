#!/bin/bash

# Check if input argument is provided
if [ -z "$1" ]; then
  echo "Usage: $0 <input_ms_file>"
  exit 1
fi

# Set the input MS file
# Set the input MS file and other arguments
ms_file="$1"
imsize="$2"
cell="$3"

base_name="${ms_file%.ms}"


# Define the output names based on the input file name
#model_image="${base_name}.model"
output_image="${base_name}.Dirty_Fixed-position_PhasedC_${imsize}_${cell}"

# CASA commands to be executed
casa_commands=$(cat <<EOF
# Step 1: Extract the Bright Source using uvmodelfit
print("Running uvmodelfit to create a model of the bright source...")
#uvmodelfit(vis='$ms_file', model='$model_image', niter=10000)

# Step 2: Subtract the Bright Source Model using uvsub
print("Running uvsub to subtract the bright source model from the visibility data...")
#uvsub(vis='$ms_file', model='$model_image')

# List obs
print("Running listobs to get the inforamation about the visibility data...")
listobs(vis='$ms_file', listfile='listobs.txt')


# Step 3: Image the Remaining Data using tclean
print("Running tclean to image the remaining data...")
tclean(
    vis='$ms_file',
    selectdata=True,
    field='',
    spw='',
    timerange='',
    uvrange='',
    antenna='',
    scan='',
    observation='',
    intent='',
    datacolumn='corrected',
    imagename='$output_image',
    imsize=$imsize,
    cell='$cell',
    phasecenter='J2000 19h01m32.9 14d58m08.7',
    stokes='I',
    projection='SIN',
    startmodel='',
    specmode='mfs',
    reffreq='',
    gridder='standard',
    vptable='',
    pblimit=0.2,
    deconvolver='hogbom',
    restoration=True,
    restoringbeam=[],
    pbcor=False,
    outlierfile='',
    weighting='natural',
    uvtaper=[],
    niter=0,
    gain=0.1,
    threshold='',
    nsigma=0.0,
    cycleniter=-1,
    cyclefactor=1.0,
    minpsffraction=0.05,
    maxpsffraction=0.8,
    interactive=False,
    fullsummary=False,
    nmajor=-1,
    usemask='user',
    mask='',
    pbmask=0.0,
    fastnoise=True,
    restart=True,
    savemodel='none',
    calcres=True,
    calcpsf=True,
    psfcutoff=0.35,
    parallel=False
)
print("Imaging completed.")
EOF
)

# Run CASA with the constructed commands
/Applications/CASA.app/Contents/MacOS/casa --nologger --nogui -c "$casa_commands"
