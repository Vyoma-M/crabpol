"""
Mapmaking script to make Stokes IQU binned maps from Planck TOD with
pixel size of 1.5' and 80 pixels along one side.
"""

import os
from pathlib import Path
from typing import Optional, Sequence

import healpy as hp
import npipe_utils as utils
import numpy as np
from gettod import Get_TOD
from scipy.linalg import pinv


class MapMaker:
    def __init__(
        self,
        instrument: str = "HFI",
        data_path: Optional[str] = None,
        alpha: float = -0.28,
        coord: Optional[Sequence[float]] = None,
        coord_system: str = "galactic",
        withcc: bool = False,
        f_bg: Optional[np.ndarray] = None,
        bg_subtraction: bool = False,
        nside: int = 2048,
        npix: int = 80,
        pixel_size: float = 1.5,  # in arcminutes
        split: Optional[str] = None,
        tod_loader: Optional[Get_TOD] = None,
    ) -> None:
        self.data_path = data_path
        self.alpha = alpha
        self.instrument = instrument
        self.coord = coord
        self.coord_system = coord_system
        self.withcc = withcc
        self.f_bg = f_bg
        self.bg_subtraction = bg_subtraction
        self.nside = nside
        self.npix = npix
        self.split = split
        self.pixel_size = pixel_size  # in arcminutes
        self.planck_freq = {"LFI": [30, 40, 70], "HFI": [100, 143, 217, 353, 545, 857]}
        if self.data_path is None:
            self.data_path = utils.get_data_path(subfolder="data/")
        if coord is None and coord_system == "galactic":
            coord = [184.5574, -5.7843]  # galactic coord of tau-A
        elif coord is None and coord_system == "equatorial":
            coord = [83.63304, 22.01449]  # equatorial coord of tau-A
        if self.bg_subtraction and self.f_bg is None:
            if instrument == "LFI":
                f_bg = np.array(
                    [1.70065975e-03, 1.54363888e-03, 2.03856413e-04]
                )  # in K_CMB units
            elif instrument == "HFI":
                f_bg = np.array(
                    [9.50687754e-5, 1.89320788e-4, 6.29073416e-4, 6.16040430e-3]
                )  # in K_CMB units
            print(
                "Background flux for background subtraction not provided. Using default values of"
                "{} in K_CMB units for frequencies {}".format(
                    f_bg, self.planck_freq[instrument]
                )
            )
        if withcc:
            print(
                "Colour correction for SED with index {} will be applied".format(
                    self.alpha
                )
            )
        # Validate data path
        self._validate_data_path()

        # TOD loader: accept an injected loader or create one from same args
        if tod_loader is not None:
            self.tod_loader = tod_loader
        else:
            # construct Get_TOD using same configuration so behavior remains compatible
            self.tod_loader = Get_TOD(
                instrument=self.instrument,
                split=self.split,
                data_path=self.data_path,
                alpha=self.alpha,
                coord=self.coord,
                coord_system=self.coord_system,
                withcc=self.withcc,
                f_bg=self.f_bg,
                bg_subtraction=self.bg_subtraction,
            )

    def _validate_data_path(self):
        if not os.path.exists(self.data_path):
            raise FileNotFoundError(
                f"The specified data path {self.data_path} does not exist."
            )

    def _bin_tod_ongrid(self, freq, npix, pixel_size, split=None, instrument="HFI"):
        if os.path.exists(Path(__name__).resolve().parent / "maps"):
            path = Path(__name__).resolve().parent / "maps/"
        else:
            os.makedirs(Path(__name__).resolve().parent / "maps", exist_ok=True)
            path = Path(__name__).resolve().parent / "maps/"
        if split is not None:
            mapname = "{}GHz_{}pix_{}_grid.fits".format(freq, npix, split)
        else:
            mapname = "{}GHz_{}pix_grid.fits".format(freq, npix)

        # Get TOD & coordinates on a grid using injected TOD loader
        print("Extracting TOD for {}GHz freq channel".format(freq))
        x, y, xbinning, ybinning, signal, pixweights = self.tod_loader.tod_ongrid(
            coord=self.coord,
            freq=freq,
            npix=npix,
            pixsize=pixel_size,
            coord_system=self.coord_system,
            split=split,
        )
        print("Making map for {}GHz freq channel".format(freq))

        bmap = np.zeros((npix, npix, 3))
        for i in np.arange(npix):
            m = np.logical_and(x > xbinning[i], x < xbinning[i + 1])
            yx = y * m
            for j in np.arange(npix):
                m = np.logical_and(np.abs(yx) > ybinning[j], yx < ybinning[j + 1])
                PTP = pixweights[:, m] @ pixweights[:, m].T
                mp = pinv(PTP) @ pixweights[:, m] @ signal[m]
                bmap[j, i] = mp

        print("Made map for {}GHz freq channel. Writing map to file..".format(freq))
        utils.create_fits(path + mapname, bmap.T)
        print("Written map to file {}".format(path + mapname))
        return bmap

    def _bin_tod_healpix(self, freq, nside, nnz=3, instrument="HFI", split=None):
        if os.path.exists(Path(__name__).resolve().parent / "maps"):
            path = Path(__name__).resolve().parent / "maps/"
        else:
            os.makedirs(Path(__name__).resolve().parent / "maps", exist_ok=True)
            path = Path(__name__).resolve().parent / "maps/"
        if split is not None:
            mapname = "{}GHz_{}hpbinning_{}.fits".format(freq, nside, split)
        else:
            mapname = "{}GHz_{}hpbinning.fits".format(freq, nside)

        # Get TOD & coordinates using injected TOD loader
        print("Extracting TOD for {}GHz freq channel".format(freq))
        tod = self.tod_loader.tod(freq=freq, nside=nside, split=split)
        signal, pixels, pixweights = tod.signal, tod.pixels, tod.weights
        print("Making map for {}GHz freq channel".format(freq))

        isamp = 0
        imap = 0  # IQU
        bmap = np.zeros((12 * nside**2, nnz))  # binned map
        nmap = np.zeros((12 * nside**2, nnz))  # hits map
        nsamp = signal.shape[0]
        for isamp in range(nsamp):
            pix = pixels[isamp]
            if pix < 0:
                continue
            for imap in range(nnz):
                bmap[pix, imap] += signal[isamp] * pixweights.T[isamp, imap]
                nmap[pix, imap] += 1

        print("Made map for {}GHz freq channel. Writing map to file..".format(freq))
        hp.write_map(path + mapname, bmap.T, nest=True, overwrite=True)
        hp.write_map(path + "hits_" + mapname, nmap.T, nest=True, overwrite=True)
        print("Written map to file {}".format(path + mapname))
        return bmap
