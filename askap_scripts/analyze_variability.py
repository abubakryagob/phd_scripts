#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Variability Analysis for ZTF J1901+1458

This script analyzes the time-series FITS images created by the askap_small_images.sh 
script to look for any variability or transient emission from ZTF J1901+1458.

Note: If encountering numpy/accelerate errors on macOS, try:
    export VECLIB_MAXIMUM_THREADS=1
    before running this script.

Usage:
    python analyze_variability.py <path_to_fits_files> <source_ra> <source_dec> <aperture_radius> [--fits <fits_file1> <fits_file2> ...]

    - path_to_fits_files: Directory containing the time sequence FITS files
    - source_ra: Right ascension of source in degrees
    - source_dec: Declination of source in degrees
    - aperture_radius: Extraction aperture radius in pixels
    - --fits: Optional. Specific FITS files to analyze instead of all files in directory

Example:
    python analyze_variability.py . 285.3871 14.9691 5
    python analyze_variability.py . 285.3871 14.9691 5 --fits file1.fits file2.fits
"""

import os
import sys
import glob
import re
import numpy as np
import matplotlib.pyplot as plt
from astropy.io import fits
from astropy.stats import sigma_clipped_stats
from astropy.wcs import WCS
from astropy.coordinates import SkyCoord
import astropy.units as u
from scipy import stats

# Try to import photutils; if not available, we'll provide a simpler alternative
try:
    from photutils.aperture import CircularAperture, aperture_photometry
    HAS_PHOTUTILS = True
except ImportError:
    print("Warning: photutils package not found. Using simplified flux extraction.")
    HAS_PHOTUTILS = False


def get_ms_filename(filepath):
    """
    Get the name of the MS file associated with a FITS file.
    This helps identify which observation the data comes from.
    Prioritizes finding beam number patterns (e.g., beam02) in the filepath.
    
    Parameters:
    -----------
    filepath : str
        Path to the FITS file or directory
        
    Returns:
    --------
    str
        MS identifier, preferring beam number if available
    """
    # If it's a file, get its directory
    if os.path.isfile(filepath):
        directory = os.path.dirname(filepath)
        filename = os.path.basename(filepath)
        
        # Extract the full MS name from the filename
        # For filenames like "scienceData.SMARTIE_04.SB51657.SMARTIE_04.beam15_averaged_cal.leakage_duration-399sec_interval-10sec_t0000.fits"
        # We want "scienceData.SMARTIE_04.SB51657.SMARTIE_04.beam15_averaged_cal.leakage"
        ms_parts = filename.split('_duration')
        if len(ms_parts) > 1:
            return ms_parts[0]
        
        # Alternatively, try to match the entire pattern before the time index
        ms_pattern = re.search(r'^(.+?)_t\d+\.fits$', filename)
        if ms_pattern:
            return ms_pattern.group(1)
    else:
        directory = filepath
    
    # If no pattern found or it's a directory, just return directory name
    return os.path.basename(os.path.abspath(directory))

def extract_time_index(filename):
    """Extract the time index from the filename."""
    match = re.search(r'_t(\d+)\.fits$', filename)
    if match:
        return int(match.group(1))
    
    # Alternative pattern for the actual files
    match = re.search(r'interval-10sec_t(\d+)\.fits$', filename)
    if match:
        return int(match.group(1))
    return -1


def measure_flux(fits_file, ra_deg, dec_deg, aperture_radius_pix=5, annulus_inner=10, annulus_outer=15):
    """
    Measure the flux at the source position in a FITS image.
    
    Parameters:
    -----------
    fits_file : str
        Path to the FITS file
    ra_deg, dec_deg : float
        RA and Dec of the source in degrees
    aperture_radius_pix : float
        Radius of the aperture in pixels
    annulus_inner, annulus_outer : float
        Inner and outer radii of the background annulus in pixels
    
    Returns:
    --------
    flux : float
        Measured flux density in Jy
    noise : float
        Estimated noise level in Jy
    snr : float
        Signal-to-noise ratio
    """
    # Read the FITS file
    hdul = fits.open(fits_file)
    data = hdul[0].data.squeeze()  # Remove single dimensions
    header = hdul[0].header
    wcs = WCS(header, naxis=2)
    
    # Convert RA/Dec to pixel coordinates
    source_coord = SkyCoord(ra_deg, dec_deg, unit='deg')
    # Handle different versions of astropy
    try:
        x, y = wcs.world_to_pixel(source_coord)  # newer versions
    except AttributeError:
        x, y = wcs.wcs_world2pix(source_coord.ra.deg, source_coord.dec.deg, 0)  # older versions
    
    # Calculate aperture area (πr²)
    aperture_area = np.pi * aperture_radius_pix**2
    
    # Use different methods depending on whether photutils is available
    if HAS_PHOTUTILS:
        # Create aperture at source position
        position = np.array([[x, y]])
        aperture = CircularAperture(position, r=aperture_radius_pix)
        
        # Measure flux in the aperture
        phot_table = aperture_photometry(data, aperture)
        source_flux = phot_table['aperture_sum'][0]
    else:
        # Manual aperture photometry
        x_int, y_int = int(round(x)), int(round(y))
        
        # Check if coordinates are within image bounds
        if (y_int < 0 or y_int >= data.shape[0] or 
            x_int < 0 or x_int >= data.shape[1]):
            print("Warning: Source position ({}, {}) outside image bounds for {}".format(x_int, y_int, fits_file))
            return 0.0, 1.0, 0.0  # Return zero flux, unit error, zero SNR
        
        # Extract a box around the target position
        box_size = int(aperture_radius_pix * 2) + 1
        y_min = max(0, y_int - box_size)
        y_max = min(data.shape[0], y_int + box_size + 1)
        x_min = max(0, x_int - box_size)
        x_max = min(data.shape[1], x_int + box_size + 1)
        
        # Create a grid of pixel coordinates
        y_coords, x_coords = np.ogrid[y_min:y_max, x_min:x_max]
        
        # Calculate distance from source position for each pixel
        distances = np.sqrt((x_coords - x)**2 + (y_coords - y)**2)
        
        # Create mask for pixels within the aperture
        aperture_mask = distances <= aperture_radius_pix
        
        # Sum the flux in the aperture
        source_flux = np.sum(data[y_min:y_max, x_min:x_max][aperture_mask])
        aperture_area = np.sum(aperture_mask)  # Actual number of pixels in aperture
    
    # Estimate background and noise
    # Use sigma-clipped stats from a region around the source position
    y_min = max(0, int(y) - 50)
    y_max = min(data.shape[0], int(y) + 50)
    x_min = max(0, int(x) - 50)
    x_max = min(data.shape[1], int(x) + 50)
    
    region = data[y_min:y_max, x_min:x_max]
    mean_bkg, median_bkg, std_bkg = sigma_clipped_stats(region, sigma=3.0)
    
    # Background-subtracted flux (per pixel × number of pixels in aperture)
    bkg_sum = median_bkg * aperture_area
    net_flux = source_flux - bkg_sum
    
    # Calculate the beam area in pixels (if beam information is in the header)
    try:
        bmaj = header['BMAJ'] * 3600  # convert from degrees to arcsec
        bmin = header['BMIN'] * 3600
        pixel_scale = abs(header['CDELT1']) * 3600  # arcsec per pixel
        beam_area_pix = (bmaj * bmin * np.pi / (4 * np.log(2))) / (pixel_scale**2)
        
        # Convert from Jy/beam to Jy
        net_flux = net_flux / beam_area_pix
    except KeyError:
        # If beam information is not available, just report in image units
        print("Warning: Beam information not found in header for {}".format(fits_file))
    
    # Calculate the noise (error) based on the background standard deviation
    noise = std_bkg * np.sqrt(aperture_area)
    if 'beam_area_pix' in locals():
        noise = noise / beam_area_pix
    
    # Calculate SNR
    snr = net_flux / noise if noise > 0 else 0
    
    hdul.close()
    
    return net_flux, noise, snr


def calculate_variability_metrics(fluxes, errors):
    """
    Calculate variability metrics from a time series of flux measurements.
    
    Parameters:
    -----------
    fluxes : array-like
        Array of flux density measurements
    errors : array-like
        Array of flux density measurement errors
    
    Returns:
    --------
    metrics : dict
        Dictionary containing variability metrics
    """
    metrics = {}
    
    # Modulation index (fractional variation)
    if np.mean(fluxes) != 0:
        metrics['mod_index'] = np.std(fluxes) / np.mean(fluxes)
    else:
        metrics['mod_index'] = np.nan
    
    # Reduced chi-square (chi^2/nu) - test against a constant flux hypothesis
    if len(fluxes) > 1:
        mean_flux = np.mean(fluxes)
        chi_square = np.sum(((fluxes - mean_flux) / errors)**2)
        dof = len(fluxes) - 1  # degrees of freedom
        metrics['reduced_chi_square'] = chi_square / dof
        
        # P-value from chi-square distribution
        metrics['p_value'] = 1 - stats.chi2.cdf(chi_square, dof)
    else:
        metrics['reduced_chi_square'] = np.nan
        metrics['p_value'] = np.nan
    
    return metrics


def plot_light_curve(time_indices, fluxes, errors, metrics, fits_files=None, output_file=None):
    """
    Plot the light curve of the source.
    
    Parameters:
    -----------
    time_indices : array-like
        Array of time indices
    fluxes : array-like
        Array of flux density measurements in Jy
    errors : array-like
        Array of flux density measurement errors in Jy
    metrics : dict
        Dictionary containing variability metrics
    fits_files : list, optional
        List of FITS files used for analysis (to determine MS filename)
    output_file : str, optional
        Path to save the plot
    """
    fig, ax = plt.subplots(figsize=(10, 6))
    
    # Plot the light curve
    ax.errorbar(time_indices, fluxes * 1e3, yerr=errors * 1e3, fmt='o', color='blue', 
                capsize=3, ecolor='black', markersize=4, label='Flux measurements')
    
    # Plot a horizontal line at zero flux
    ax.axhline(y=0, color='gray', linestyle='-', alpha=0.7)
    
    # Add a horizontal line at the mean flux
    mean_flux = np.mean(fluxes) * 1e3
    ax.axhline(y=mean_flux, color='red', linestyle='--', alpha=0.7, 
               label='Mean flux: {:.2f} mJy'.format(mean_flux))
    
    # Get the MS filename for the title if not already provided in the output_file
    if fits_files:
        if output_file and '_' in output_file:
            # Try to extract MS name from output filename
            ms_name_match = re.search(r'ZTF_J1901_([^_]+)_light_curve', output_file)
            if ms_name_match:
                ms_name = ms_name_match.group(1)
            else:
                # Get MS name from first FITS file
                ms_name = get_ms_filename(fits_files[0])
        else:
            # Get MS name from first FITS file
            ms_name = get_ms_filename(fits_files[0])
    else:
        ms_name = "unknown"
    
    # Formatting
    ax.set_xlabel('Time index (10-second intervals)')
    ax.set_ylabel('Flux Density (mJy)')
    # Set main title
    ax.set_title('ZTF J1901+1458 Variability Analysis', fontsize=12)
    # Add smaller subtitle below title
    ax.text(0.5, 1.00, ms_name, transform=ax.transAxes,
        fontsize=8, ha='center', va='top')
    
    # Add text box with variability metrics
    textstr = '\n'.join((
        'Modulation index: {:.3f}'.format(metrics["mod_index"]),
        'Reduced chi^2: {:.3f}'.format(metrics["reduced_chi_square"]),
        'p-value: {:.3e}'.format(metrics["p_value"]),
        'Mean SNR: {:.2f}'.format(np.mean(fluxes/errors))
    ))
    
    props = dict(boxstyle='round', facecolor='wheat', alpha=0.5)
    ax.text(0.05, 0.95, textstr, transform=ax.transAxes, fontsize=10,
            verticalalignment='top', bbox=props)
    
    ax.grid(True, alpha=0.3)
    ax.legend(loc='upper right')
    
    plt.tight_layout()
    
    if output_file:
        plt.savefig(output_file, dpi=300)
        print("Light curve saved to {}".format(output_file))
    else:
        plt.show()


def process_files_by_ms(fits_files, source_ra, source_dec, aperture_radius):
    """
    Process a list of FITS files, grouping them by their MS sources.
    
    Parameters:
    -----------
    fits_files : list
        List of FITS file paths
    source_ra, source_dec : float
        RA and Dec of the source in degrees
    aperture_radius : float
        Radius of the aperture in pixels
    """
    # Group FITS files by their associated MS
    ms_groups = {}
    for fits_file in fits_files:
        ms_name = get_ms_filename(fits_file)
        if ms_name not in ms_groups:
            ms_groups[ms_name] = []
        ms_groups[ms_name].append(fits_file)
    
    # Process each group separately
    print("Found {} different MS sources in the data.".format(len(ms_groups)))
    
    for ms_name, ms_fits_files in ms_groups.items():
        ms_fits_files = sorted(ms_fits_files, key=extract_time_index)
        print("\nProcessing {} FITS files from MS: {}".format(len(ms_fits_files), ms_name))
        
        # Extract time indices from filenames
        time_indices = [extract_time_index(f) for f in ms_fits_files]
        
        # Measure flux at source position for each image
        fluxes = []
        errors = []
        snrs = []
        
        for i, fits_file in enumerate(ms_fits_files):
            print("Processing {} ({}/{})...".format(os.path.basename(fits_file), i+1, len(ms_fits_files)))
            flux, error, snr = measure_flux(fits_file, source_ra, source_dec, aperture_radius)
            fluxes.append(flux)
            errors.append(error)
            snrs.append(snr)
        
        # Convert to numpy arrays
        time_indices = np.array(time_indices)
        fluxes = np.array(fluxes)
        errors = np.array(errors)
        snrs = np.array(snrs)
        
        # Calculate variability metrics
        metrics = calculate_variability_metrics(fluxes, errors)
        
        # Print results for this MS
        print("\nVariability Analysis Results for {}:".format(ms_name))
        print("----------------------------")
        print("Number of time samples: {}".format(len(fluxes)))
        print("Mean flux: {:.6f} Jy".format(np.mean(fluxes)))
        print("Std. deviation: {:.6f} Jy".format(np.std(fluxes)))
        print("Modulation index: {:.3f}".format(metrics['mod_index']))
        print("Reduced chi^2 (constant flux test): {:.3f}".format(metrics['reduced_chi_square']))
        print("p-value: {:.3e}".format(metrics['p_value']))
        
        # Significance of variability
        if metrics['p_value'] < 0.05:
            print("\nThe source shows statistically significant variability (p < 0.05).")
        else:
            print("\nNo statistically significant variability detected.")
        
        # Save results to a file with MS name
        results_file = "variability_results_{}.txt".format(ms_name)
        with open(results_file, "w") as f:
            f.write("Variability Analysis Results for ZTF J1901+1458 - {}\n".format(ms_name))
            f.write("=============================================\n")
            f.write("Number of time samples: {}\n".format(len(fluxes)))
            f.write("Mean flux: {:.6f} Jy\n".format(np.mean(fluxes)))
            f.write("Std. deviation: {:.6f} Jy\n".format(np.std(fluxes)))
            f.write("Modulation index: {:.3f}\n".format(metrics['mod_index']))
            f.write("Reduced chi^2 (constant flux test): {:.3f}\n".format(metrics['reduced_chi_square']))
            f.write("p-value: {:.3e}\n".format(metrics['p_value']))
            
            if metrics['p_value'] < 0.05:
                f.write("\nThe source shows statistically significant variability (p < 0.05).\n")
            else:
                f.write("\nNo statistically significant variability detected.\n")
        
        print("\nResults saved to {}".format(results_file))
        
        # Plot the light curve with MS name
        light_curve_file = "ZTF_J1901_{}_light_curve.png".format(ms_name)
        plot_light_curve(time_indices, fluxes, errors, metrics, ms_fits_files, light_curve_file)
        
        # Save the flux measurements to a CSV file with MS name
        data_file = "ZTF_J1901_{}_flux_data.csv".format(ms_name)
        with open(data_file, "w") as f:
            f.write("time_index,flux_jy,error_jy,snr\n")
            for t, flux, error, snr in zip(time_indices, fluxes, errors, snrs):
                f.write("{},{},{},{}\n".format(t, flux, error, snr))
        
        print("Flux measurements saved to {}".format(data_file))


def main():
    """Main function to run the variability analysis."""
    # Check for minimum required arguments
    if len(sys.argv) < 5:
        print("Usage: python analyze_variability.py <path_to_fits_files> <source_ra> <source_dec> <aperture_radius> [--fits <fits_file1> <fits_file2> ...]")
        sys.exit(1)
    
    fits_dir = sys.argv[1]
    source_ra = float(sys.argv[2])
    source_dec = float(sys.argv[3])
    aperture_radius = float(sys.argv[4])
    
    # Check if specific FITS files are provided
    specific_fits = []
    if len(sys.argv) > 5 and sys.argv[5] == "--fits":
        specific_fits = sys.argv[6:]
        print("Using {} specific FITS files provided as arguments".format(len(specific_fits)))
        # Convert relative paths to absolute if needed
        fits_files = []
        for f in specific_fits:
            if not os.path.isabs(f):
                fits_files.append(os.path.join(fits_dir, f))
            else:
                fits_files.append(f)
    else:
        # Find all FITS files in the directory
        fits_pattern = os.path.join(fits_dir, "*.fits")
        fits_files = sorted(glob.glob(fits_pattern))
    
    if not fits_files:
        print("No FITS files found matching pattern {}".format(fits_pattern))
        sys.exit(1)
    
    print("Found {} FITS files.".format(len(fits_files)))
    
    # Process all files, grouped by their MS source
    process_files_by_ms(fits_files, source_ra, source_dec, aperture_radius)


if __name__ == "__main__":
    main()
