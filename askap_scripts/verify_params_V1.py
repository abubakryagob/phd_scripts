import os
import sys

# --- Argument Parsing ---
if len(sys.argv) < 2:
    print("Usage: casa --nologger --nogui -c verify_params.py <path_to_dirty_image>")
    sys.exit(1)

image_path = sys.argv[1]

if not os.path.exists(image_path):
    print(f"Error: Image not found at '{image_path}'")
    sys.exit(1)

# --- Verification Step 1: Check beam and cell size ---
print("--- Running imhead to get beam and cell size ---")
try:
    header_summary = imhead(imagename=image_path, mode='summary')

    # Extract key values for analysis
    if header_summary:
        beam_major = header_summary['beammajor']['value']
        beam_minor = header_summary['beamminor']['value']
        cell_size_ra = abs(header_summary['cdelt1']['value']) * 3600  # convert from deg to arcsec
        
        print(f"Synthesized Beam Major Axis: {beam_major:.2f} arcsec")
        print(f"Synthesized Beam Minor Axis: {beam_minor:.2f} arcsec")
        print(f"Current Cell Size: {cell_size_ra:.2f} arcsec")

        # Recommendation for cell size: 3-5 pixels across the beam FWHM
        recommended_cell_max = beam_minor / 3.0
        recommended_cell_min = beam_minor / 5.0
        print(f"Recommended Cell Size Range: {recommended_cell_min:.2f} to {recommended_cell_max:.2f} arcsec")
        if recommended_cell_min <= cell_size_ra <= recommended_cell_max:
            print("VERIFICATION: The current cell size is appropriate.")
        else:
            print("RECOMMENDATION: Consider adjusting the cell size to be within the recommended range.")
except Exception as e:
    print(f"Error running imhead: {e}")


# --- Verification Step 2: Determine the cleaning threshold and other stats ---
print("\n--- Running imstat for detailed image statistics ---")
try:
    image_stats = imstat(imagename=image_path)

    if image_stats:
        # All values are in Jy/beam, so we convert to mJy/beam by multiplying by 1000
        rms = image_stats['rms'][0] * 1000
        mean = image_stats['mean'][0] * 1000
        max_val = image_stats['max'][0] * 1000
        min_val = image_stats['min'][0] * 1000
        flux = image_stats.get('flux', [0])[0] * 1000 # Flux might not always be present

        print(f"Image RMS noise: {rms:.2f} mJy/beam")
        print(f"Mean pixel value: {mean:.2f} mJy/beam")
        print(f"Maximum pixel value: {max_val:.2f} mJy/beam")
        print(f"Minimum pixel value: {min_val:.2f} mJy/beam")
        print(f"Total Flux: {flux:.2f} mJy")

        # Recommendation for threshold: 3-5 times the RMS
        threshold_3sigma = 3 * rms
        threshold_5sigma = 5 * rms
        print(f"\nRecommended Cleaning Threshold (3-5 sigma): {threshold_3sigma:.2f} to {threshold_5sigma:.2f} mJy")
        print("VERIFICATION: The planned threshold should be compared to this range.")
    else:
        print("Could not retrieve statistics from image.")
except Exception as e:
    print(f"Error running imstat: {e}")

