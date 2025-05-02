import numpy as np
import astropy.units as u
from astropy.io import fits
from astropy.table import Table
from stingray import Lightcurve, Powerspectrum, Crossspectrum
from stingray.utils import assign_value_if_none
from xspec import *
import matplotlib.pyplot as plt

# Define the pulse phase interval
phase_interval = [0.0, 0.1]

# Open the X-ray data file
hdulist = fits.open('PNclean_bary_0882184001.fits')

# Extract the event table
event_table = Table(hdulist['EVENTS'].data)

# Filter the events based on the pulse phase interval
filtered_table = event_table[(event_table['PULSE_PHASE'] > phase_interval[0]) & (event_table['PULSE_PHASE'] < phase_interval[1])]

# Define the time bins and generate the lightcurve
time_bins = np.arange(filtered_table['TIME'].min(), filtered_table['TIME'].max(), 1000)
lc = Lightcurve(filtered_table['TIME'], gti=[[filtered_table['TIME'].min(), filtered_table['TIME'].max()]], bin_time=1000)

# Compute the power spectrum and extract the frequencies
ps = Powerspectrum(lc, norm='leahy')
freqs = ps.freq

# Compute the phase-resolved cross-spectrum
cross_spec = Crossspectrum(lc, lc, norm='leahy')

# Define the XSPEC model and fit the phase-resolved spectrum
AllModels.initpackage("xmm-newton")
AllModels.setEnergies(".01 10.0")
AllData.clear()
AllData.ignore("**-0.5 10.0-**")
AllData.ignore("bad")
AllData.background = 0.0
AllData.response = "rmf.fits"
AllData.response.arf = "arf.fits"
pha = "spectrum.fits"
s = Spectrum(pha)
s.response = AllData.response
s.response.arf = AllData.response.arf
m = Model("nsatmos")
m.nH = 0.2
m.T = 0.5
m.R = 10.0
Fit.perform()

# Extract the fitted parameters
nH = m.nH.values[0]
T = m.T.values[0]
R = m.R.values[0]

# Generate the phase-resolved spectrum and plot it
s = Spectrum(pha)
s.response = AllData.response
s.response.arf = AllData.response.arf
s.ignore("**-0.5 10.0-**")
s.notice("2.0-10.0")
s.phabs.nH = nH
s.nsatmos.T = T
s.nsatmos.R = R
AllModels.show()
Plot.device = "/null"
Plot.xAxis = "keV"
Plot.yAxis = "keV/s/cm**2"
Plot("data")
Plot.device = "/xs"
Plot.xAxis = "keV"
Plot.yAxis = "keV/s/cm**2"
Plot("eeufspec")

# Close the input file
hdulist.close()
