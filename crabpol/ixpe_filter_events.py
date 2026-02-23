"""
This module contains a class to filter the events within the specified energy range and create a new fits 
file with only the relevant columns for polarization analysis. The class takes in the path to the 
events file, the path to the response files, and the desired energy range for filtering. It 
uses the functions from the ixpe_instrument module to convert the PI values to energy, and 
to get the effective area and modulation factor for the filtered events. The filtered events 
are then saved to a new fits file in the specified data directory.
"""

import numpy as np
from astropy.io import fits
import ixpe_instrument as instrument

class FilterEvents:
    """
    A class to filter the events within the specified energy range and create a new fits file with only the relevant columns for polarization analysis.
    The columns extracted are: PI, energy, X, Y, Q, U, W_MOM, effective area (Aeff), and modulation factor (Modf).
    Parameters:
-----------
events_path: str
    The path to the events file (in fits format) to be filtered.
resp_path: str
    The path to the directory where the response files from CalDB were unpacked.
data_dir: str
    The directory where the filtered events file will be saved.
detector: str
    The detector to use (d1, d2, or d3).
caldb_version: str
    The CalDB version to use (e.g., '20170101').
recon_version: str
    The reconstruction version refers to the response matrix associated with the event reconstruction method used (eg. 'alpha075_02').
min_energy: float
    The minimum energy (in keV) for filtering the events.
max_energy: float
    The maximum energy (in keV) for filtering the events.
    Methods:
    --------
    filter_events():
        Filters the events based on the specified energy range and saves the filtered events to a new fits file in the specified data directory.
    """
    def __init__(
        self,
        events_path,
        resp_path,
        data_dir,
        detector="d1",
        caldb_version="20170101",
        recon_version="alpha075_02",
        min_energy=2.0,
        max_energy=8.0,
    ):
        self.events_path = events_path
        self.resp_path = resp_path
        self.data_dir = data_dir
        self.detector = detector
        self.caldb_version = caldb_version
        self.recon_version = recon_version
        self.min_energy = min_energy
        self.max_energy = max_energy

    def filter_events(self):
        hdul = fits.open(self.events_path)
        PI = hdul[1].data["PI"]
        Q = hdul[1].data["Q"]
        U = hdul[1].data["U"]
        X = hdul[1].data["X"]
        Y = hdul[1].data["Y"]
        wmom = hdul[1].data["W_MOM"]
        hdul.close()

        es = instrument.chan_to_e(
            PI,
            resp_path=self.resp_path,
            detector=self.detector,
            caldb_version=self.caldb_version,
            recon_version=self.recon_version,
        )
        aeff = instrument.e_to_aeff(
            es,
            resp_path=self.resp_path,
            detector=self.detector,
            caldb_version=self.caldb_version,
            recon_version=self.recon_version,
        )
        modf = instrument.e_to_modf(
            es,
            resp_path=self.resp_path,
            detector=self.detector,
            caldb_version=self.caldb_version,
            recon_version=self.recon_version,
        )
        es = np.array(es)
        aeff = np.array(aeff)
        modf = np.array(modf)

        mask = np.logical_and(es >= self.min_energy, es <= self.max_energy)
        energy = es[mask]
        eff = aeff[mask[:, 0]]
        mod = modf[mask[:, 0]]
        qmasked = Q[mask[:, 0]]
        umasked = U[mask[:, 0]]
        xmasked = X[mask[:, 0]]
        ymasked = Y[mask[:, 0]]
        wmommasked = wmom[mask[:, 0]]
        PImasked = PI[mask[:, 0]]

        c1 = fits.Column(name="PI", array=PImasked, format="J")
        c2 = fits.Column(name="E", array=energy, format="E")
        c3 = fits.Column(name="X", array=xmasked, format="E")
        c4 = fits.Column(name="Y", array=ymasked, format="E")
        c5 = fits.Column(name="Q", array=qmasked, format="D")
        c6 = fits.Column(name="U", array=umasked, format="D")
        c7 = fits.Column(name="W_MOM", array=wmommasked, format="E")
        c8 = fits.Column(name="Aeff", array=eff, format="E")
        c9 = fits.Column(name="Modf", array=mod, format="E")
        cols = fits.ColDefs([c1, c2, c3, c4, c5, c6, c7, c8, c9])
        hdu = fits.BinTableHDU.from_columns(cols)
        hdu.writeto(
            self.data_dir
            + "/filtered_{}_{}.fits".format(self.detector, self.recon_version),
            overwrite=True,
        )
