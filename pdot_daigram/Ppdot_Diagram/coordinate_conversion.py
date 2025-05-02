import astropy.coordinates as coord
import astropy.units as u
import numpy as np

from astropy.coordinates import galactocentric_frame_defaults
from typing import Tuple

def evaluate_phi(x: float, y: float) -> float:
    """
        Calculating the polar angle phi in rad given the Cartesian cordinates x and y.

        Args:
            x (float): x coordinate in a Cartesian galactocentric frame.
            y (float): y coordinate in a Cartesian galactocentric frame.
           
        Returns:
            (float): phi angular coordinate computed from the x axis and growing 
            in counter-clockwise direction.
    """
         
    if (x > 0.) & (y > 0.):
        phi = np.arctan(y/x)
    elif (x < 0.) & (y > 0.):
        phi = np.arctan(y/x) + np.pi
    elif (x < 0.) & (y < 0.):
        phi = np.arctan(y/x) + np.pi
    else:
        phi = np.arctan(y/x) + 2.*np.pi
            
    return phi
    
def heliocentric_distance(x: float, y: float, z: float, sun_position: list) -> float:
    """
    Given the position of the star in the galactocentric frame, this function
    evaluates the distance from the Sun.

    Args:
        x (float): x coordinate in galactocentric frame in kpc.
        y (float): y coordinate in galactocentric frame in kpc.
        z (float): z coordinate in galactocentric frame in kpc.

    Returns:
        (float): ddistance from the Sun in kpc.
    """
    xsun = sun_position[0]
    ysun = sun_position[1]
    zsun = sun_position[2]

    dist = np.sqrt((x-xsun) ** 2 + (y-ysun) ** 2 + (z-zsun) ** 2)

    return dist

def speed_cartesian_to_cylindrical(
    v_x: float, v_y: float, v_z: float, phi: float
) -> Tuple[float, float, float]:
    """
        Calculating the galactocentric cylindrical v_r, v_phi and v_z velocity components
        from Cartesianl galactocentric components v_x, v_y and v_z.

        Args:
            v_x (float): x velocity component in a Cartesian galactocentric frame.
            v_y (float): y velocity component in a Cartesian galactocentric frame.
            v_z (float): z velocity component in a Cartesian galactocentric frame.
            phi (float): azimuthal angle [0, 2*pi] in cylindrical coordinates.

        Returns:
            (float, float, float): v_r, v_phi and v_z velocity components in a cylindrical
            galactocentric frame.
        """

    v_r = v_x * np.cos(phi) + v_y * np.sin(phi)
    v_phi = - v_x * np.sin(phi) + v_y * np.cos(phi)

    return v_r, v_phi, v_z

def icrs_to_galactocentric(
    ra: float, 
    dec: float, 
    distance: float,
    pmra: float = None, 
    pmdec: float = None, 
    v_ls: float = None,
    )-> Tuple[float, float, float, float, float, float]:
    """
        Calculating the galactocentric coordinates x, y, z, v_x, v_y and v_z from the 
        ICRS (International Celestial Reference Frame) coordinates ra,
        dec, parallax and the proper motion pmra, pmdec, v_ls. This galactocentric coordinates
        refers to the galactocentric reference defined as a right-handed reference frame with 
        the Sun located at the coordinate point (x = 0 kpc, y = 8.3 kpc, z = 0.02 kpc).
        We use the astropy.coordinates package that allows automatic conversions
        between coordinate systems.

        Args:
            ra (float): ra coordinate in deg in ICRS reference frame.
            dec (float): dec coordinate in deg in ICRS reference frame.
            distance (float): distance from the solar system barycenter in kpc.
            pmra (float): proper motion component in ra in mas / yr in ICRS reference frame.
            pmdec (float): proper motion component in dec in mas / yr in ICRS reference frame.
            v_ls (float): line of sight velocity component in km / s in ICRS reference frame.

        Returns:
            (float, float, float, float, float, float): x, y, z, cartesian position
            in kpc and v_x, v_y and v_z velocity components in km / s in the 
            galactocentric reference frame.
        """
        
    # The galactocentric reference frame used is a right-handed
    # reference frame with the Sun located at the coordinate point (x = 0 kpc,
    # y = 8.3 kpc, z = 0.02 kpc).
    # The module astropy.coordinates.Galactocentric deals with galactocentric
    # coordinates but it is defined with the x, y, axes rotated of 90 degrees
    # clockwise respect to the galactocentric reference frame used in the simulation.
    # In this new frame the position of the Sun is (x = -8.3 kpc, y = 0 kpc, z = 0.02
    # kpc). We therefore need to convert the galactocentric coordinates used in astropy
    # into the galactocentric frame we want for the output. To do that we
    # apply the transformation (x_astropy-> -y_gal, y_astropy -> x_gal, z_astropy -> z_gal).
    
    # Set the astropy galactocentric frame with the parameter
    # values from astropy version 4.0.
    _ = galactocentric_frame_defaults.set("v4.0")
    
    if (pmra is not None) and (pmdec is not None) and (v_ls is not None):
        c = coord.SkyCoord(
            ra=ra * u.deg,
            dec=dec * u.deg,
            distance=distance * u.kpc,
            pm_ra_cosdec=pmra * u.mas / u.yr,
            pm_dec=pmdec * u.mas / u.yr,
            radial_velocity=v_ls * u.km / u.s,
        )
        
        galcen = c.transform_to(
            coord.Galactocentric(z_sun=0.02 * u.kpc, galcen_distance=8.3 * u.kpc)
        )
        
        x = galcen.y.value
        y = - galcen.x.value
        z = galcen.z.value
        
        v_x = galcen.v_y.value
        v_y = - galcen.v_x.value
        v_z = galcen.v_z.value
        
    else:
        c = coord.SkyCoord(
            ra=ra * u.deg,
            dec=dec * u.deg,
            distance=distance * u.kpc,
        )
        
        galcen = c.transform_to(
            coord.Galactocentric(z_sun=0.02 * u.kpc, galcen_distance=8.3 * u.kpc)
        )
        
        x = galcen.y.value 
        y = - galcen.x.value 
        z = galcen.z.value 
        
        v_x = None
        v_y = None
        v_z = None
        
    return x, y, z, v_x, v_y, v_z
    

def icrs_to_galactic(
    ra: float, 
    dec: float, 
    distance: float, 
    pmra: float = None, 
    pmdec: float = None, 
    v_ls: float = None,
    )-> Tuple[float, float, float, float, float, float]:
    """
        Calculating the galactic coordinates l, b, distance, v_l, v_b, v_ls from the 
        ICRS (International Celestial Reference Frame) coordinates ra,
        dec, parallax and the proper motion pmra, pmdec, v_ls. 
        We use the astropy.coordinates package that allows automatic conversions
        between coordinate systems. l is in the range [-180, 180] deg while b is in 
        the range [-90, 90] deg.

        Args:
            ra (float): ra coordinate in deg in ICRS reference frame.
            dec (float): dec coordinate in deg in ICRS reference frame.
            distance (float): distance from the solar system barycenter in kpc.
            pmra (float): proper motion component in ra in mas / yr in ICRS reference frame.
            pmdec (float): proper motion component in dec in mas / yr in ICRS reference frame.
            v_ls (float): line of sight velocity component in km / s in ICRS reference frame.

        Returns:
            (float, float, float, float, float, float): galactic longitude l, galactic latitude b
            in deg, distance in kpc, v_l, v_b proper motion components in mas / yr and line of 
            sight velocity v_ls in km/s.
        """
    
    if (pmra is not None) and (pmdec is not None) and (v_ls is not None):
        c = coord.SkyCoord(
            ra=ra * u.deg,
            dec=dec * u.deg,
            distance=distance * u.kpc,
            pm_ra_cosdec=pmra * u.mas / u.yr,
            pm_dec=pmdec * u.mas / u.yr,
            radial_velocity=v_ls * u.km / u.s,
        )
        
        galactic = c.transform_to(
            coord.Galactic()
        )
        
        l = galactic.l.value
        l[(l>180.) & (l<=360.)] = l[(l>180.) & (l<=360.)] - 360.
        b = galactic.b.value
        distance = galactic.distance.value
        
        pm_l_cosb = galactic.pm_l_cosb.value
        pm_b = galactic.pm_b.value
        radial_velocity = galactic.radial_velocity.value
        
    else:
        c = coord.SkyCoord(
            ra=ra * u.deg,
            dec=dec * u.deg,
            distance=distance * u.kpc,
        )
        
        galactic = c.transform_to(
            coord.Galactic()
        )
        
        l = galactic.l.value
        l[(l>180.) & (l<=360.)] = l[(l>180.) & (l<=360.)] - 360.
        b = galactic.b.value
        distance = galactic.distance.value
        
        pm_l_cosb = None
        pm_b = None
        radial_velocity = None
        
    return l, b, distance, pm_l_cosb, pm_b, radial_velocity
    
    
def galactocentric_to_galactic(
    x: float, 
    y: float, 
    z: float, 
    v_x: float = None, 
    v_y: float = None, 
    v_z: float = None,
    )-> Tuple[float, float, float, float, float, float]:
    """
        Calculating the galactic coordinates l, b, distance, v_l, v_b, v_ls from the 
        galactocentric coordinates x, y, z and velocity v_x, v_y, v_z. 
        The galactocentric coordinates refers to the galactocentric reference frame
        defined as a right-handed reference frame with the Sun located at the coordinate
        point (x = 0 kpc, y = 8.3 kpc, z = 0.02 kpc).
        We use the astropy.coordinates package that allows automatic conversions
        between coordinate systems. l is in the range [-180, 180] deg while b is in 
        the range [-90, 90] deg.

        Args:
            x (float): x coordinate in kpc in the galactocentric reference frame.
            y (float): y coordinate in kpc in the galactocentric reference frame.
            z (float): z coordinate in kpc in the galactocentric reference frame.
            v_x (float): x component of the velocity in km/s in galactocentric reference frame.
            v_y (float): y component of the velocity in km/s in galactocentric reference frame.
            v_z (float): z component of the velocity in km/s in galactocentric reference frame.

        Returns:
            (float, float, float, float, float, float): galactic longitude l, galactic latitude b
            in deg, distance in kpc, v_l, v_b proper motion components in mas / yr and line of 
            sight velocity v_ls in km/s.
        """
    
    # The galactocentric reference frame used for the iinput is a right-handed
    # reference frame with the Sun located at the coordinate point (x = 0 kpc,
    # y = 8.3 kpc, z = 0.02 kpc).
    # The module astropy.coordinates.Galactocentric deals with galactocentric
    # coordinates but it is defined with the x, y, axes rotated of 90 degrees
    # clockwise respect to the galactocentric reference frame used in the simulation.
    # In this new frame the position of the Sun is (x = -8.3 kpc, y = 0 kpc, z = 0.02
    # kpc). We therefore need to convert the galactocentric coordinates we used
    # into the galactocentric frame defined in astropy. To do that we
    # apply the transformation (x_gal -> y_astropy, y_gal -> -x_astropy, z_gal -> z_astropy).
    
    # Set the astropy galactocentric frame with the parameter
    # values from astropy version 4.0.
    _ = galactocentric_frame_defaults.set("v4.0")
    
    if (v_x is not None) and (v_y is not None) and (v_z is not None):
        c = coord.Galactocentric(
            x=-y * u.kpc,
            y=x * u.kpc,
            z=z * u.kpc,
            v_x=-v_y * u.km / u.s,
            v_y=v_x * u.km / u.s,
            v_z=-v_z * u.km / u.s,
            z_sun=0.02 * u.kpc, galcen_distance=8.3 * u.kpc
        )
        
        galactic = c.transform_to(
            coord.Galactic()
        )
        
        l = galactic.l.value
        l[(l>180.) & (l<=360.)] = l[(l>180.) & (l<=360.)] - 360.
        b = galactic.b.value
        distance = galactic.distance.value
        
        pm_l_cosb = galactic.pm_l_cosb.value
        pm_b = galactic.pm_b.value
        radial_velocity = galactic.radial_velocity.value
        
    else:
        c = coord.Galactocentric(
            x=-y * u.kpc,
            y=x * u.kpc,
            z=z * u.kpc,
            z_sun=0.02 * u.kpc, galcen_distance=8.3 * u.kpc
        )
        
        
        galactic = c.transform_to(
            coord.Galactic()
        )
        
        l = galactic.l.value
        l[(l>180.) & (l<=360.)] = l[(l>180.) & (l<=360.)] - 360.
        b = galactic.b.value
        distance = galactic.distance.value
        
        pm_l_cosb = None
        pm_b = None
        radial_velocity = None
        
    return l, b, distance, pm_l_cosb, pm_b, radial_velocity
    
def galactic_to_galactocentric(
    l_gal: float, 
    b_gal: float, 
    dist: float, 
    v_l: float = None, 
    v_b: float = None, 
    v_ls: float = None,
    )-> Tuple[float, float, float, float, float, float]:
    """
        Calculating the galactocentric coordinates x, y, z, v_x, v_y and v_z from the 
        galactic coordinates longitude l, latitude b in deg, distance from the Sun and the proper 
        motion v_l, v_b in mas/yr and line of sight velocity v_ls in km/s. This galactocentric coordinates
        refers to the galactocentric reference defined as a right-handed reference frame with 
        the Sun located at the coordinate point (x = 0 kpc, y = 8.3 kpc, z = 0.02 kpc).
        We use the astropy.coordinates package that allows automatic conversions
        between coordinate systems.

        Args:
            l (float): galactic longitude in deg in the range [0, 360] deg.
            b (float): galactic latitude in deg in the range [-90, 90] deg..
            distance (float): distance from the solar system barycenter in kpc.
            v_l (float): proper motion component in l in mas / yr.
            v_b (float): proper motion component in b in mas / yr.
            v_ls (float): line of sight velocity component in km / s in ICRS reference frame.

        Returns:
            (float, float, float, float, float, float): x, y, z, cartesian position
            in kpc and v_x, v_y and v_z velocity components in km / s in the 
            galactocentric reference frame.
        """
    
    # The galactocentric reference frame used for the input is a right-handed
    # reference frame with the Sun located at the coordinate point (x = 0 kpc,
    # y = 8.3 kpc, z = 0.02 kpc).
    # The module astropy.coordinates.Galactocentric deals with galactocentric
    # coordinates but it is defined with the x, y, axes rotated of 90 degrees
    # clockwise respect to the galactocentric reference frame used in the simulation.
    # In this new frame the position of the Sun is (x = -8.3 kpc, y = 0 kpc, z = 0.02
    # kpc). We therefore need to convert the galactocentric coordinates we used
    # into the galactocentric frame defined in astropy. To do that we
    # apply the transformation (x_gal -> y_astropy, y_gal -> -x_astropy, z_gal -> z_astropy).
    
    # Set the astropy galactocentric frame with the parameter
    # values from astropy version 4.0.
    _ = galactocentric_frame_defaults.set("v4.0")
    
    if (v_l is not None) and (v_b is not None) and (v_ls is not None):
        c = coord.Galactic(
            l=l_gal * u.deg,
            b=b_gal* u.deg,
            distance=dist * u.kpc,
            pm_l_cosb=v_l * u.mas / u.yr,
            pm_b=v_b * u.mas / u.yr,
            radial_velocity=v_ls * u.km / u.s,
        )
        
        galcen = c.transform_to(
            coord.Galactocentric(z_sun=0.02 * u.kpc, galcen_distance=8.3 * u.kpc)
        )
        
        x = galcen.y.value
        y = - galcen.x.value
        z = galcen.z.value
        
        v_x = galcen.v_y.value
        v_y = - galcen.v_x.value
        v_z = galcen.v_z.value
        
    else:
        c = coord.Galactic(
            l=l_gal * u.deg,
            b=b_gal* u.deg,
            distance=dist * u.kpc,
        )
        
        
        galcen = c.transform_to(
            coord.Galactocentric(z_sun=0.02 * u.kpc, galcen_distance=8.3 * u.kpc)
        )
        
        x = galcen.y.value
        y = - galcen.x.value
        z = galcen.z.value
        
        v_x = None
        v_y = None
        v_z = None
        
    return x, y, z, v_x, v_y, v_z

