"""
This module contains functions to
1) Access the response matrix file to convert between the Pulse Interval (PI) and incident photon energy
2) Access the ancillary response file to get the effective area (or spectral response) and modulation
factor for a given energy
"""

import numpy as np
from astropy.io import fits
import os


def chan_to_e(
    channel,
    resp_path,
    detector="d1",
    caldb_version="20170101",
    recon_version="alpha075_02",
):
    """
    Convert from Pulse Interval (PI) to energy using the response matrix file from CalDB.
    Parameters:
    -----------
    channel: int or list of ints
        The PI channel(s) to convert to energy.
    resp_path: str
        The path to the directory where the response files from CalDB were unpacked.
    detector: str
        The detector to use (d1, d2, or d3).
    caldb_version: str
        The CalDB version to use (e.g., '20170101').
    recon_version: str
        The reconstruction version refers to the response matrix
        associated with the event reconstruction method used (eg. 'alpha075_02').
    Returns:
    --------
    energy: float or list of floats
        The incident photon energy corresponding to the input PI channel(s).
    """
    rmf_path = os.path.join(
        resp_path,
        "/data/ixpe/gpd/cpf/rmf/ixpe_{}_{}_{}.rmf".format(
            detector, caldb_version, recon_version
        ),
    )
    hdul = fits.open(rmf_path)
    emin = hdul[2].data["E_MIN"]
    emax = hdul[2].data["E_MAX"]
    chan = hdul[2].data["CHANNEL"]
    echan = (emin + emax) / 2.0
    if len(channel) > 0:
        e = []
        for i in channel:
            (k,) = np.where(chan == i)
            e.append(echan[k])
        return e
    else:
        return echan[chan == channel]


def e_to_aeff(
    energy,
    resp_path,
    detector="d1",
    caldb_version="20170101",
    recon_version="alpha075_02",
):
    """
    Collect the effective area (or spectral response) for a given incident photon energy using the ancillary response file from CalDB.
    Parameters:
    -----------
    energy: float or list of floats
        The incident photon energy (in keV) to get the effective area for.
    resp_path: str
        The path to the directory where the response files from CalDB were unpacked.
    detector: str
        The detector to use (d1, d2, or d3).
    caldb_version: str
        The CalDB version to use (e.g., '20170101').
    recon_version: str
        The reconstruction version refers to the response matrix associated with the event reconstruction method used (eg. 'alpha075_02').
    Returns:
    --------
    aeff: float or list of floats
        The effective area (or spectral response) corresponding to the input energy(ies).
    """
    arf_path = os.path.join(
        resp_path,
        "/data/ixpe/gpd/cpf/arf/ixpe_{}_{}_{}.arf".format(
            detector, caldb_version, recon_version
        ),
    )
    hdul = fits.open(arf_path)
    E_low = hdul[1].data["ENERG_LO"]
    E_High = hdul[1].data["ENERG_HI"]
    aeff = hdul[1].data["SPECRESP"]
    hdul.close()
    echan = (E_low + E_High) / 2.0
    if len(energy) > 0:
        af = []
        for i in energy:
            (k,) = np.where(echan == i)
            af.append(aeff[k])
        return af
    else:
        return aeff[echan == energy]


def e_to_modf(
    energy,
    resp_path,
    detector="d1",
    caldb_version="20170101",
    recon_version="alpha075_02",
):
    """
    Collect the modulation factor for a given incident photon energy using the modulation factor file from CalDB.
    Parameters:
    -----------
    energy: float or list of floats
        The incident photon energy (in keV) to get the modulation factor for.
    resp_path: str
        The path to the directory where the response files from CalDB were unpacked.
    detector: str
        The detector to use (d1, d2, or d3).
    caldb_version: str
        The CalDB version to use (e.g., '20170101').
    recon_version: str
        The reconstruction version refers to the response matrix associated with the event reconstruction method used (eg. 'alpha075_02').
    Returns:
    --------
    modf: float or list of floats
        The modulation factor corresponding to the input energy(ies).
    """
    modf_path = os.path.join(
        resp_path,
        "/data/ixpe/gpd/cpf/modfact/ixpe_{}_{}_mfact_{}.fits".format(
            detector, caldb_version, recon_version
        ),
    )
    hdul = fits.open(modf_path)
    E_low = hdul[1].data["ENERG_LO"]
    E_High = hdul[1].data["ENERG_HI"]
    modf = hdul[1].data["SPECRESP"]
    hdul.close()
    echan = (E_low + E_High) / 2.0
    if len(energy) > 0:
        mf = []
        for i in energy:
            (k,) = np.where(echan == i)
            mf.append(modf[k])
        return mf
    else:
        return modf[echan == energy]
