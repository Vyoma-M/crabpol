""" This module contains utility functions for IXPE data analysis, including functions 
to calculate polarization degree, position angle, and to overplot polarization vectors on 
visualised maps. It also includes functions to calculate total flux over specific areas of the data and 
to generate WCS for IRAM data. The functions are designed to work with Stokes parameter maps and to facilitate
the visualization of polarization properties in astronomical data.
"""
import numpy as np
from matplotlib import pyplot as plt
from astropy.io import fits
from astropy.wcs import WCS
from astropy import units
from astropy.coordinates import SkyCoord

def pol_degree(maps):
    """Calculate the polarization degree from the Stokes parameter maps."""
    mapps = maps.copy()
    q=mapps[1]
    u=mapps[2]
    np.divide(mapps[1],mapps[0], out=q, where=mapps[0]!=0)
    np.divide(mapps[2],mapps[0], out=u, where=mapps[0]!=0)
    p = np.sqrt(q**2 + u**2)
    return p

def normQU_to_qu(maps):
    """Calculate the normalized Stokes parameters q and u from the Stokes parameter maps."""
    mapps = maps.copy()
    q=mapps[1]
    u=mapps[2]
    np.divide(mapps[1],mapps[0], out=q, where=mapps[0]!=0)
    np.divide(mapps[2],mapps[0], out=u, where=mapps[0]!=0)
    return q, u

def position_angle_pol(q, u, deg=True):
    """Calculate the position angle of polarization from the Stokes parameters q and u. Select deg=True to return the angle in degrees, or deg=False to return the angle in radians."""
    a = 0.5 * np.arctan2(u, q)
    if deg:
        a = np.rad2deg(a)
    return a

def posanglepol_to_xy(pol_degree, pol_angle, deg=False):
    """Convert the polarization degree and position angle to x and y components for plotting. Select deg=True if the input position angle is in degrees, or deg=False if the input position angle is in radians."""
    ang = pol_angle
    if deg:
        ang = np.radians(pol_angle)
    x = pol_degree * np.cos(ang)
    y = pol_degree * np.sin(ang)
    return x, y

def int_area(data, center, num_pix, extent=20, pixel_size=0.00072):
    """Calculate the total flux over a circular area from central pixel of the map. The radius of the circular area is determined by the extent and pixel size parameters."""
    x, y = np.indices((num_pix, num_pix))
    r = np.sqrt((x-center[0])**2 + (y-center[1])**2)
    r = r*pixel_size
    R = extent*pixel_size
    maparea = np.copy(data)
    for i in np.arange(num_pix):
        for j in np.arange(num_pix):
            if (r[i,j]>R):
                maparea[:,i,j]=0.0
    return maparea

def overlay_reg_arrows(center, maps, **kwargs):
    x, y = calculate_sky_grid(center)
    pd = pol_degree(maps)
    q, u = normQU_to_qu(maps)
    pa = position_angle_pol(q,u)
    dx, dy = posanglepol_to_xy(pd, pa, deg=True)
    plot_arrows((x, y), (dx, dy))

def sum_area(region):
    """Calculate the total flux over a specific area of the data, defined by the region parameter. The region parameter is expected to be a boolean mask that identifies the area of interest in the data."""
    mask = region[0]>0.
    I = np.sum(region[0][mask])
    Q = np.sum(region[1][mask])
    U = np.sum(region[2][mask])
    if I==0:
        q = Q
        u = U
    elif I!=0:
        q = Q/I
        u = U/I
    p = np.sqrt(q**2 + u**2)
    a = position_angle_pol(q, u, deg=True)
    return p, a

def plot_reg_arrows(x, y, dx, dy, scale):
    kwargs.setdefault('color', 'black')
    kwargs.setdefault('alpha', 1.0)
    kwargs.setdefault('width', 0.003)
    kwargs.setdefault('headlength', 0.)
    kwargs.setdefault('headwidth', 1.)
    kwargs.setdefault('pivot', 'middle')
    kwargs.setdefault('scale', scale)
    plt.gca().quiver(x, y, dx, dy, **kwargs)
    plt.axis([xmin, xmax, ymin, ymax])
    
def calc_centpix(side):
    """Calculate the central pixel for a given side length of the map."""
    return 0.5 * (side + 1)

def gen_wcs(side, pixel_size, ra, dec):
    """Generate a WCS object for a given side length of the map, pixel size, and central coordinates (ra, dec). The WCS object can be used to convert between pixel coordinates and sky coordinates."""
    w = WCS(naxis=2)
    centpix = calc_centpix(side)
    w.wcs.crpix = [centpix, centpix]
    w.wcs.cdelt = [-pixel_size, pixel_size]
    c = SkyCoord(ra, dec)
    w.wcs.crval = [c.ra.deg, c.dec.deg]
    w.wcs.cunit = ['deg', 'deg']
    w.array_shape = side, side
    return w

def iram_wcs(path_to_file, ra_obj = 0.8363139500000E+02, dec_obj = 0.2200769361111E+02, side1=None, side2=None):
    """Generate a WCS object for IRAM data using the header information from a FITS file. The WCS object can be used to convert between pixel coordinates and sky coordinates. The side1 and side2 parameters can be used to adjust the reference pixel coordinate if the map is not square.
    ra_obj and dec_obj are the RA and Dec of the reference pixel in degrees, which can be adjusted as needed. The function reads the header of the specified FITS file to obtain the pixel size and other necessary information for generating the WCS object."""
    hdu = fits.open(path_to_file)
    header = hdu[0].header
    hdu.close()
    # dist_obj = 2.0*units.kpc
    ra_obj *= units.deg  # deg
    dec_obj *= units.deg  # deg
    cdelt1 = ((header['CDELT1']))
    cdelt2 = ((header['CDELT2']))
    w3 = WCS(naxis=2)
    # reference pixel coordinate
    w3.wcs.crpix = [25, 20]
    if side1 is not None or side2 is not None:
        w3.wcs.crpix = [(25*2-side2)/2, (20*2-side1)/2]
    # sizes of the pixel in degrees
    w3.wcs.cdelt = [cdelt1, cdelt2]
    # converting ra and dec into degrees
    c = SkyCoord(ra_obj, dec_obj)
    w3.wcs.crval = [c.ra.deg, c.dec.deg]
    # the units of the axes are in degrees
    w3.wcs.cunit = ['deg', 'deg']
    return w3

def calculate_sky_grid(side, pixel_size, ra, dec):
    """Calculate the sky coordinates (RA, Dec) for a grid of pixels based on the side length of the map, pixel size, and central coordinates (ra, dec). The function generates a WCS object using the gen_wcs function and then uses it to convert pixel coordinates to sky coordinates."""
    wcs_grid = gen_wcs(side, pixel_size, ra, dec) 
    xx0, xx1 = (-0.5, side-0.5)
    yy0, yy1 = (-0.5, side-0.5)
    nx, ny = [side, side]
    X, Y = np.meshgrid(np.linspace(xx0,xx1,nx,endpoint=True),
                      np.linspace(yy0,yy1,ny,endpoint=True))
    ra, dec = wcs_grid.wcs_pix2world(X, Y, 0)
    return ra, dec

def iram_plotpolvec(maps, wcs, plot_title, scale, figname, colormap='rainbow'):
    """Plot polarization vectors on a visualized map using the Stokes parameter maps and WCS information. The function calculates the polarization degree and position angle from the Stokes parameters, converts them to x and y components for plotting, and then uses quiver to plot the vectors on the map. The plot is saved to a file specified by figname."""
    fig = plt.figure(figsize=(12,4))
    i_plot = fig.add_subplot(111, projection=wcs)
    plt.imshow(maps[0], origin='lower', cmap=colormap)
    plt.colorbar(label='Stokes I')
    plt.tick_params(axis='both', direction='in', which='both')
    plt.xlabel('RA [degrees]')
    plt.ylabel('Dec [degrees]')
    plt.title(plot_title)
    # ranges of the axis
    xx0, xx1 = i_plot.get_xlim()
    yy0, yy1 = i_plot.get_ylim()
    nx = maps[0].shape[1]
    ny = maps[0].shape[0]
    X, Y = np.meshgrid(np.linspace(xx0,xx1,nx,endpoint=True),
                      np.linspace(yy0,yy1,ny,endpoint=True))
    mask = maps[0] < 0.02
    a = position_angle_pol(maps[1], maps[2], deg=True)
    p = np.sqrt(maps[1]**2+maps[2]**2)
    p[mask] = 0
    a[mask] = 0
    dx, dy = posanglepol_to_xy(p, a, deg=True)
    plot_reg_arrows((X, Y), (dx,dy), scale)
    plt.savefig(figname, bbox_inches='tight')