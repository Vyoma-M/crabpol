# crabpol
### Python package for processing of Planck [NPIPE](https://www.aanda.org/articles/aa/full_html/2020/11/aa38073-20/aa38073-20.html) Time-ordered Data (TOD) and [IXPE](https://arxiv.org/abs/2112.01269) observations of the Crab Nebula
This package contains the analysis tools for the processing of observations of the Crab nebula (also known as Tau-A or M1) by Planck (sub-mm) and IXPE (X-ray) satellites. It supports map-making, unit conversions and visualization, turning raw satellite observations into maps ready for analysis. 

![Static Badge](https://img.shields.io/badge/GitHub-Vyoma--M-blue?link=https%3A%2F%2Fgithub.com%2FVyoma-M)

## Features
Planck/NPIPE TOD:
1) Load and pre-process NPIPE Time-Ordered Data  datasets
2) Map-making: Binning data into HEALPix or a square grid (flat-field approximation) pixelization scheme
3) Optional unit conversion and colour correction
4) Conversions between different coordinate systems
5) Visualise Stokes I, Q, and U maps with overlay of polarization vectors
6) Tools for variable aperture photometry

IXPE:
1) Filtering of events within energy windows
2) Application of corrections with the Ancillary and Response Matrix files
3) Map-making by binning the events onto a square grid (valid in flat-approximation)
4) Visualise Stokes I, Q, and U maps with overlay of polarization vectors

Other
- Compute polarisation degree and position angle
- Flexible workflow for research and analysis


## Installation
- By cloning the repository:

``` </> Bash 
git clone https://github.com/Vyoma-M/crabpol.git
cd crabpol
pip install -e .
pip install -r requirements-dev.txt
```
This installs the package in editable mode.

## Test
Test your installation with:

``` 
cd crabpol
pytest
```

## Quick start
An example for a quick end-to-end map-making routine from NPIPE TOD:
```
</> Python

from crabpol import Get_TOD, GetTODConfig, MapMaker 

# 1) Configure with variables of interest
cfg = GetTODConfig(
    instrument="HFI",  # High-frequency Instrument aboard Planck
    data_path=<path-to-TOD-directory>,
    freq=100, # in GHz
    nside=2048,
    withcc=False, # set to True if colour correction needs to be applied
    bg_subtraction=False, # set to True if background subtraction needs to be applied
)

# 2) Create a TOD loader with the above configuration
tod_loader = Get_TOD(config=cfg)

# 3) Create a MapMaker object with the TOD loader and desired map parameters
mm = MapMaker(tod_loader=tod_loader, npix=80, pixel_size=1.5)

# 4) Make a healpix map by binning the destriped TOD.
bmap = mm._bin_tod_healpix(freq=cfg.freq, nside=cfg.nside)
```
This routine takes the relevant data columns from the NPIPE TOD and bins them into maps with [HEALPix](https://arxiv.org/abs/astro-ph/0409513) pixelization scheme. 
For more examples: [examples folder](https://github.com/Vyoma-M/crabpol/tree/main/examples)

## Workflow
1. Acquire relevant columns from TOD/IXPE event files
2. Pre-process (filtering, coordinate transformation, optional corrections for bandpass, effective area, calibration)
3. Bin into Stokes I, Q, U maps
4. Visualise maps and analyse them to obtain flux densities and characteristics of polarised emission like polarisation degree and position angle of polarisation
<details><summary>Advanced Usage: Colour Correction, Background Subtraction and Map-making</summary>

#### On Colour Correction
- Compute colour correction for a power-law spectral index (eg. -0.28 for Crab nebula)
- Apply corrections at TOD or map level
- Applying colour corrections also converts units to MJy/sr

#### Background Subtraction
One needs an estimate of the background flux to apply this correction. 
- Make Stokes I, Q, U maps by binning the TOD.
- Estimate background flux by selecting an annular region outside of the target emission
- Apply subtraction at TOD level before map-making

#### Map-making
Map-making is a data reduction method with the benefit of making pretty visualisations of the data. There are two options available for map-making:
- Binning in [HEALPix](https://arxiv.org/abs/astro-ph/0409513) pixelization scheme
- Binning on a square grid with user-defined pixel size and side length (in number of pixels) for small fields for which flat approximation applies
</details>



## Contributing

Contributions are welcome! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for development setup, testing and style guidelines.

## Acknowledgement
If you found this package useful for your work, please cite my thesis:

Vyoma Muralidhara (2024): Spectral distortion and polarization of the cosmic microwave background: Measurement, challenges and perspectives, [DOI:10.5282/edoc.34768](https://arxiv.org/abs/2503.08538). 
BibTex entry:
```
@phdthesis{Muralidhara:2024hey,
    author = "Muralidhara, Vyoma",
    title = "{Spectral distortion and polarization of the cosmic microwave background}",
    eprint = "2503.08538",
    archivePrefix = "arXiv",
    primaryClass = "astro-ph.CO",
    doi = "10.5282/edoc.34768",
    school = "Munich U.",
    year = "2024"
}
```

## License

Copyright 2026 Vyoma Muralidhara.

crabpol is free software made available under the MIT License. For details see the LICENSE file.
