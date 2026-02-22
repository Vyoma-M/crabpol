#! /usr/bin/env python
# -*- coding: utf-8 -*-

# import os
# import sys
from setuptools import setup, find_namespace_packages

# if sys.argv[-1] == "publish":
#     os.system("python setup.py sdist upload")
#     sys.exit()

setup(
    name='crabpol',
    version='0.1.0',
    author='Vyoma Muralidhara',
    author_email='vyoma1993@gmail.com',
    description='A Python package for analysis of NPIPE TOD and IXPE observations of the Crab nebula\
        (also known as Tau-A or M1).',
    long_description=open('README.md').read(),
    packages=find_namespace_packages(),
    package_data={
        "crabpol": ["LICENSE"],
        "crabpol.data": [
            "HFI_RIMO_R4.00.fits",
            "LFI_RIMO_R4.00.fits",
        ],
        "crabpol.data.PR2-3": [
            "HFI_UC_CC_RIMO-4_alpha-0.28.txt",
            "HFI_UC_CC_RIMO-4_alpha-0.35.txt",
            "LFI_UC_CC_RIMO-4_alpha-0.35.txt",
            "LFI_UC_CC_RIMO-4_alpha-0.28.txt"
        ]
    },
    include_package_data=True,
    long_description_content_type='text/markdown',
    url='https://github.com/Vyoma-M/crabpol',
    classifiers=[
        'Programming Language :: Python :: 3',
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.8',
    install_requires=[
        'healpy',
        'numpy',
        'scipy',
        'astropy',
    ],
    test_suite='tests',
    zip_safe=False,
)
