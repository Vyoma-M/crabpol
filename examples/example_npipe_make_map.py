"""Example script to make a binned map in HEALPix pixelization scheme
from destriped NPIPE TOD using MapMaker."""
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__).removesuffix("/examples"), "/tau-A"))

from ..tauA.gettod import Get_TOD, GetTODConfig
from ..tauA.mapmaker import MapMaker

#Fix: 1) Configure (replace with your actual data path containing M1/ and PR2-3/)
cfg = GetTODConfig(
    instrument="HFI",
    data_path=None,
    freq=100,
    nside=2048,
    withcc=True,
    bg_subtraction=True,
)

# 2) Create a TOD loader
tod_loader = Get_TOD(config=cfg)

# 3) Create a MapMaker object with the TOD loader and desired map parameters
mm = MapMaker(tod_loader=tod_loader, npix=80, pixel_size=1.5)

# 4) Make a healpix map by binning the destriped TOD.
bmap = mm._bin_tod_healpix(freq=cfg.freq, nside=cfg.nside)

print("Binned map shape:", getattr(bmap, "shape", None))