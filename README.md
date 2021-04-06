# SIMURAN
[![Build Status](https://travis-ci.com/seankmartin/SIMURAN.svg?branch=master)](https://travis-ci.com/seankmartin/SIMURAN)
[![Documentation Status](https://readthedocs.org/projects/simuran/badge/?version=latest)](https://simuran.readthedocs.io/en/latest/?badge=latest)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)

Simultaneous Multi-Region Analysis.
The general design is to have single objects with large amounts of information and an intuitive system to set this up.

## Objective
Describe what is in your data and facilitate batch processing.
Provide some analysis methods and allow for easy creation of further analyses.

## Installation
```
git clone https://github.com/seankmartin/PythonUtils
cd PythonUtils
pip install -e .
cd ..
git clone https://github.com/seankmartin/SIMURAN
cd SIMURAN
pip install -e .
```

## Requirements
Listed in requirements.txt.

## Ideas
Interface with other programs such as SpikeInterface to allow for many different systems and sorters to be used.

## Information in an experiment
1. Date and time
2. Channel map (like spike sorters)
3. Parameters file

## Information in a signal
1. Date and time (or just time).
2. Region
3. Geometrical Location
4. Tag
5. Source data location
6. File format
7. Description
8. Sampling rate
9. Duration
10. Data type

## Considerations
1. Add more unit test cases
2. List front facing functions
3. Clean up the naming in main
4. Add copy operations to the primary classes

## Using custom analysis code
SIMURAN can use any code that is on the Python path. The easiest way to manage this is to either:
1. Fork SIMURAN and place your custom analysis code in the SIMURAN package under the directory labelled custom.
2. Place your code on path separately, such as by creating a `setup.py` file for your code, or a `pyproject.toml` file for installation.
3. If you place python code and/or a file with the `.pth` extension in a directory named analysis in the same directory that batch_config_path is in, this `.pth` file will be automatically processed and its contents placed on path. If this option is chosen, it is recommended to store the analysis functions directly so that anyone can run the code without modification.

## Inspiration
1. https://github.com/seankmartin/NeuroChaT
2. https://github.com/SpikeInterface
3. https://github.com/seankmartin/NeuroChaT_API_Scripts
4. https://github.com/mne-tools/mne-python/
