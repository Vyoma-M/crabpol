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
    mapps = maps.copy()
    q=mapps[1]
    u=mapps[2]
    np.divide(mapps[1],mapps[0], out=q, where=mapps[0]!=0)
    np.divide(mapps[2],mapps[0], out=u, where=mapps[0]!=0)
    p = np.sqrt(q**2 + u**2)
    return p

def normQU_to_qu(maps):
    mapps = maps.copy()
    q=mapps[1]
    u=mapps[2]
    np.divide(mapps[1],mapps[0], out=q, where=mapps[0]!=0)
    np.divide(mapps[2],mapps[0], out=u, where=mapps[0]!=0)
    return q, u

def position_angle_pol(q, u, deg=True):
    a = 0.5 * np.arctan2(u, q)
    if deg:
        a = np.rad2deg(a)
    return a

def posanglepol_to_xy(pol_degree, pol_angle, deg=False):
    ang = pol_angle
    if deg:
        ang = np.radians(pol_angle)
    x = pol_degree * np.cos(ang)
    y = pol_degree * np.sin(ang)
    return x, y

def int_area(data, center, num_pix, factor=20, pixel_size=0.00072):
    x, y = np.indices((num_pix, num_pix))
    r = np.sqrt((x-center[0])**2 + (y-center[1])**2)
    r = r*pixel_size
    R = factor*pixel_size
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
    return 0.5 * (side + 1)

def gen_wcs(side, pixel_size, ra, dec):
    w = WCS(naxis=2)
    centpix = calc_centpix(side)
    w.wcs.crpix = [centpix, centpix]
    w.wcs.cdelt = [-pixel_size, pixel_size]
    c = SkyCoord(ra, dec)
    w.wcs.crval = [c.ra.deg, c.dec.deg]
    w.wcs.cunit = ['deg', 'deg']
    w.array_shape = side, side
    return w

def iram_wcs(side1=None, side2=None):
    path = "/home/vmura/npipe/data/Crab_IRAM"
    hdu = fits.open(path+'/crab_I_coadd28_reproj_nbl_ccentonly.fits')
    header = hdu[0].header
    hdu.close()
    # dist_obj = 2.0*units.kpc
    ra_obj = 0.8363139500000E+02  * units.deg#deg
    dec_obj = 0.2200769361111E+02 * units.deg #deg
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
    wcs_grid = gen_wcs(side, pixel_size, ra, dec) 
    xx0, xx1 = (-0.5, side-0.5)
    yy0, yy1 = (-0.5, side-0.5)
    nx, ny = [side, side]
    X, Y = np.meshgrid(np.linspace(xx0,xx1,nx,endpoint=True),
                      np.linspace(yy0,yy1,ny,endpoint=True))
    ra, dec = wcs_grid.wcs_pix2world(X, Y, 0)
    return ra, dec

def iram_plotpolvec(maps, wcs, plot_title, scale, figname, colormap='rainbow'):
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