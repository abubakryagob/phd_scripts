#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
A script to be run within CASA to derive optimal tclean parameters from a Measurement Set.
"""
import os
import sys
import math

# This script is designed to be run from within CASA.
# The CASA environment provides the necessary tools like 'msmd', 'imstat', etc.
# Example execution:
# /Applications/CASA.app/Contents/MacOS/casa --nologger --nogui -c "exec(open('verify_params.py').read())" /path/to/your/ms_file.ms

def calculate_max_baseline_from_antennas(ms_path):
    """
    Calculate the maximum baseline from antenna positions in the measurement set.
    This function can be used for telescopes other than ASKAP where the configuration is unknown.
    
    Args:
        ms_path (str): Path to the measurement set
        
    Returns:
        float: Maximum baseline distance in meters, or 0 if calculation fails
    """
    import math
    
    try:
        msmd.open(ms_path)
        ant_positions = msmd.antennaposition()
        msmd.close()
        
        max_baseline = 0
        n_antennas = len(ant_positions)
        
        if n_antennas > 1:
            for i in range(n_antennas):
                for j in range(i + 1, n_antennas):
                    pos1 = ant_positions[i]
                    pos2 = ant_positions[j]
                    # Calculate 3D distance between antennas
                    dist = math.sqrt((pos1[0] - pos2[0])**2 + (pos1[1] - pos2[1])**2 + (pos1[2] - pos2[2])**2)
                    if dist > max_baseline:
                        max_baseline = dist
        
        return max_baseline
        
    except Exception as e:
        print(f"Warning: Could not calculate baseline from antenna positions: {e}")
        return 0

def get_tclean_recommendations(ms_path, auto_run=False):
    """
    Analyzes a Measurement Set and provides tclean parameter recommendations.
    
    Args:
        ms_path (str): Path to the measurement set
        auto_run (bool): If True, automatically run tclean with recommended parameters
    """
    import os
    import sys
    import math
    
    if not os.path.exists(ms_path):
        print(f"Error: Measurement Set not found at '{ms_path}'")
        return

    print(f"--- Analyzing Measurement Set: {os.path.basename(ms_path)} ---")

    try:
        # --------------------------------------------------------------------
        # 1. Get Observation Metadata using msmd tool
        # --------------------------------------------------------------------
        msmd.open(ms_path)
        center_freq_hz = msmd.meanfreq(0)
        msmd.close()
        
        # For ASKAP, use known parameters
        dish_diameter = 12.0  # ASKAP standard dish diameter in meters
        max_baseline = 6000.0  # ASKAP maximum baseline ~6 km
        
        # Alternative: For unknown telescopes, calculate from antenna positions
        # max_baseline = calculate_max_baseline_from_antennas(ms_path)
        # if max_baseline == 0:
        #     print("Warning: Could not determine baseline, using default 6km")
        #     max_baseline = 6000.0

        # --------------------------------------------------------------------
        # 2. Calculate Theoretical Image Parameters
        # --------------------------------------------------------------------
        c = 299792458.0  # Speed of light in m/s
        wavelength = c / center_freq_hz

        # Synthesized beam resolution (~ lambda / B_max)
        synth_beam_rad = wavelength / max_baseline
        synth_beam_arcsec = math.degrees(synth_beam_rad) * 3600

        # Primary beam FoV (~ lambda / D)
        primary_beam_rad = wavelength / dish_diameter
        primary_beam_arcsec = math.degrees(primary_beam_rad) * 3600

        # --------------------------------------------------------------------
        # 3. Recommend Cell and Image Size (using actual beam from data)
        # --------------------------------------------------------------------
        # Get the actual synthesized beam from the measurement set
        print("Getting actual beam information from the data...")
        
        # Create a quick test image to determine the actual synthesized beam
        test_image_name = os.path.basename(ms_path) + '.beamtest'
        
        try:
            tclean(
                vis=ms_path,
                imagename=test_image_name,
                imsize=128, # Very small image just to get beam info
                cell='2.0arcsec', # Temporary cell size
                specmode='mfs',
                gridder='standard',
                weighting='natural',
                niter=0, # Dirty image only
                calcres=False,
                calcpsf=True # We need the PSF to get beam info
            )
            
            # Get the actual beam from the image header
            beam_info = imhead(imagename=test_image_name + '.psf', mode='summary')
            if 'beammajor' in beam_info and 'beamminor' in beam_info:
                actual_beam_major = beam_info['beammajor']['value']  # in arcsec
                actual_beam_minor = beam_info['beamminor']['value']  # in arcsec
                print(f"Actual synthesized beam: {actual_beam_major:.2f}\" x {actual_beam_minor:.2f}\"")
                
                # Use the minor axis for cell size calculation (most conservative)
                synth_beam_arcsec = actual_beam_minor
            else:
                print("Warning: Could not determine beam from data, using theoretical calculation")
                # Fallback to theoretical calculation
                synth_beam_rad = wavelength / max_baseline
                synth_beam_arcsec = math.degrees(synth_beam_rad) * 3600
                
        except Exception as e:
            print(f"Warning: Could not create test image for beam determination: {e}")
            # Fallback to theoretical calculation
            synth_beam_rad = wavelength / max_baseline
            synth_beam_arcsec = math.degrees(synth_beam_rad) * 3600
            
        finally:
            # Clean up test image
            os.system(f'rm -rf {test_image_name}.*')
        
        # Rule of thumb: 3-5 pixels across the synthesized beam (using 4 as compromise)
        recommended_cell_arcsec = synth_beam_arcsec / 4.0
        
        # Image size to cover the primary beam
        recommended_imsize = int(primary_beam_arcsec / recommended_cell_arcsec)
        # Ensure it's an even number
        if recommended_imsize % 2 != 0:
            recommended_imsize += 1

        print("\n--- Telescope & Observation Derived Parameters ---")
        print(f"Center Frequency: {center_freq_hz / 1e6:.2f} MHz")
        print(f"Max Baseline: {max_baseline / 1000:.2f} km")
        print(f"Primary Beam (FoV): {primary_beam_arcsec / 60:.2f} arcmin")
        print(f"Theoretical Resolution: {synth_beam_arcsec:.2f} arcsec")

        # --------------------------------------------------------------------
        # 4. Recommend Gridder
        # --------------------------------------------------------------------
        # For ASKAP data, use standard gridder (awproject has telescope recognition issues)
        recommended_gridder = 'standard'

        # --------------------------------------------------------------------
        # 5. Recommend Threshold by making a temporary dirty image
        # --------------------------------------------------------------------
        print("\n--- Generating temporary dirty image for noise estimation ---")
        dirty_image_name = os.path.basename(ms_path) + '.quickdirty'
        
        tclean(
            vis=ms_path,
            imagename=dirty_image_name,
            imsize=512, # Small image is sufficient for noise estimate
            cell=f'{recommended_cell_arcsec:.2f}arcsec',
            specmode='mfs',
            gridder='standard', # Standard is faster for a quick noise check
            weighting='natural',
            niter=0 # Makes a dirty image
        )
        
        image_stats = imstat(imagename=dirty_image_name + '.image')
        rms_jy = image_stats['rms'][0] if image_stats and 'rms' in image_stats else 0
        
        # Clean up temporary images
        os.system(f'rm -rf {dirty_image_name}.*')

        recommended_threshold_mjy = 5 * rms_jy * 1000 # 5-sigma threshold in mJy

        # --------------------------------------------------------------------
        # 6. Final Recommendations
        # --------------------------------------------------------------------
        print("\n=================================================")
        print("    Recommended tclean Parameters")
        print("=================================================")
        print(f"imsize = {recommended_imsize}")
        print(f"cell = '{recommended_cell_arcsec:.2f}arcsec'")
        print(f"gridder = '{recommended_gridder}'")
        print(f"threshold = '{recommended_threshold_mjy:.2f}mJy'")
        print("weighting = 'natural'")
        print("specmode = 'mfs'")
        print("deconvolver = 'hogbom'")
        print("=================================================")
        
        # Return the recommended parameters for potential automation
        params = {
            'imsize': recommended_imsize,
            'cell': f'{recommended_cell_arcsec:.2f}arcsec',
            'gridder': recommended_gridder,
            'threshold': f'{recommended_threshold_mjy:.2f}mJy',
            'niter': 10000  # Default niter value
        }
        
        # Optionally run tclean automatically
        if auto_run:
            print("\n=== Starting Automated tclean ===")
            
            # Run the tclean script directly with subprocess
            import subprocess
            import os
            
            script_dir = "/Users/abubakribrahim/Desktop/observations/ASKAP/ZTFJ1901_new_data/my_scripts"
            bin_dir = "/Users/abubakribrahim/Desktop/observations/ASKAP/ZTFJ1901_new_data/bin"
            
            # Try both locations for the tclean script
            script_path = os.path.join(script_dir, "tclean_clean_image.sh")
            if not os.path.exists(script_path):
                script_path = os.path.join(bin_dir, "tclean_clean_image.sh")
            
            if not os.path.exists(script_path):
                print(f"Error: tclean script not found in {script_dir} or {bin_dir}")
            else:
                # Build the command
                cmd = [
                    script_path,
                    ms_path,
                    str(params['imsize']),
                    params['cell'],
                    str(params['niter']),
                    params['threshold']
                ]
                
                print(f"Command: {' '.join(cmd)}")
                print("This may take several minutes...")
                
                try:
                    # Run the script
                    result = subprocess.run(cmd, capture_output=True, text=True, timeout=3600)  # 1 hour timeout
                    
                    if result.returncode == 0:
                        print("✓ tclean completed successfully!")
                        if result.stdout:
                            print("Output:", result.stdout[-1000:])  # Show last 1000 chars
                    else:
                        print("✗ tclean failed!")
                        print("Error:", result.stderr)
                        if result.stdout:
                            print("Output:", result.stdout[-1000:])
                        
                except subprocess.TimeoutExpired:
                    print("✗ tclean timed out after 1 hour")
                except Exception as e:
                    print(f"✗ Error running tclean: {e}")
        
        return params

    except Exception as e:
        print(f"\nAn error occurred during analysis: {e}")
        print("Please ensure you are running this script inside a CASA environment.")
        return None
    finally:
        # Ensure msmd is closed if an error occurs
        try:
            if msmd.isopen():
                msmd.close()
        except:
            pass

if __name__ == "__main__":
    # The script expects to be run from within CASA, which sets up sys.argv differently.
    # When using `casa -c script.py arg1`, arg1 is at sys.argv[-1]
    import sys
    if len(sys.argv) < 2:
        print("Usage:")
        print("  Analysis only: casa --nologger --nogui -c verify_params.py <path_to_ms_file>")
        print("  Analysis + Auto-run tclean: casa --nologger --nogui -c verify_params.py <path_to_ms_file> --auto")
    else:
        ms_file_path = sys.argv[-1]
        auto_run = False
        
        # Check if --auto flag is present
        if len(sys.argv) >= 3 and '--auto' in sys.argv:
            auto_run = True
            # Remove --auto from arguments to get the MS file
            ms_file_path = [arg for arg in sys.argv[1:] if arg != '--auto'][-1]
        
        get_tclean_recommendations(ms_file_path, auto_run=auto_run)

