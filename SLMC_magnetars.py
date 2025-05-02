import numpy as np
import matplotlib.pyplot as plt
from astropy import units as u
from astropy.coordinates import SkyCoord, Galactic
from astropy.visualization import astropy_mpl_style
plt.style.use(astropy_mpl_style)

# Define coordinates of the Magellanic clouds in Galactic coordinates
magellanic_clouds = {
    'Large Magellanic Cloud (LMC)': SkyCoord(l=280.4652*u.deg, b=-32.8884*u.deg, frame='galactic'),
    'Small Magellanic Cloud (SMC)': SkyCoord(l=302.7317*u.deg, b=-44.3298*u.deg, frame='galactic')
}

# Define coordinates of the magnetars in J2000 equatorial coordinates
magnetars = {
    'SGR 0501+4516': SkyCoord(ra='05h01m06.76s', dec='+45d16m33.92s', frame='icrs'),
    'CXOU J010043.1−721134': SkyCoord(ra='01h00m43.14s', dec='-72d11m33.8s', frame='icrs'),
    '4XMM J045626.3–694723': SkyCoord(ra='04h56m26.36s', dec='-69d47m23.1s', frame='icrs')
}

# Transform magnetar coordinates to Galactic coordinates
for name, coord in magnetars.items():
    galactic_coord = coord.galactic
    magnetars[name] = galactic_coord

# Plot the Magellanic clouds and magnetars
fig = plt.figure(figsize=(10, 8))
ax = fig.add_subplot(111, projection='mollweide')
ax.grid(True)

for name, coord in magellanic_clouds.items():
    ax.plot(coord.l.wrap_at(180*u.deg).radian, coord.b.radian, 'o', markersize=10, label=name)

for name, coord in magnetars.items():
    ax.plot(coord.l.wrap_at(180*u.deg).radian, coord.b.radian, '*', markersize=15, label=name)

ax.legend(loc='upper right')
ax.set_title('Projection of Magellanic Clouds and Magnetars in Galactic Coordinates')
plt.show()

