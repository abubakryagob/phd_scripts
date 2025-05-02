import sys
from astropy.io import fits
import numpy as np
import astropy.stats as astats
import matplotlib.pyplot as plt

def load_data(event_file):
    with fits.open(event_file) as hdul:
        # Access the table data
        table = hdul[1].data
        print(table)
        

        # Replace with the actual column names
        time = table['TIME']
        flux = table['PI']  # or 'PHA' depending on your data

    # Remove repeated time values by averaging corresponding flux values
    unique_time = np.unique(time)
    averaged_flux = [np.mean(flux[time == t]) for t in unique_time]

    return unique_time, averaged_flux

def plot_light_curve(time, flux, blocks):
    plt.figure(figsize=(10, 5))
    plt.plot(time, flux, drawstyle='steps-mid', label='Original Light Curve')

    for block_start, block_end in zip(blocks[:-1], blocks[1:]):
        plt.axvspan(time[block_start], time[block_end], color='orange', alpha=0.3, label='Bayesian Block')

    plt.xlabel('Time')
    plt.ylabel('Energy (PI)')  # or 'PHA' depending on your data
    plt.title('X-ray Light Curve with Bayesian Blocks')
    plt.legend()
    plt.show()

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python script.py <event_file.fits>")
        sys.exit(1)

    event_file = sys.argv[1]
    time, flux = load_data(event_file)

    # Calculate Bayesian Blocks
    blocks = astats.bayesian_blocks(time, flux)

    # Plot the light curve with Bayesian Blocks
    plot_light_curve(time, flux, blocks)
