# SIMURAN

[![Documentation Status](https://readthedocs.org/projects/simuran/badge/?version=latest)](https://simuran.readthedocs.io/en/latest/?badge=latest)
[![Build Status](https://travis-ci.com/seankmartin/SIMURAN.svg?branch=master)](https://app.travis-ci.com/github/seankmartin/SIMURAN)
[![Quality Gate Status](https://sonarcloud.io/api/project_badges/measure?project=seankmartin_SIMURAN&metric=alert_status)](https://sonarcloud.io/summary/new_code?id=seankmartin_SIMURAN)
[![codecov](https://codecov.io/gh/seankmartin/SIMURAN/branch/main/graph/badge.svg?token=F67OEU0PF2)](https://codecov.io/gh/seankmartin/SIMURAN)
[![Maintainability](https://api.codeclimate.com/v1/badges/97aa79ac8f356de695d5/maintainability)](https://codeclimate.com/github/seankmartin/SIMURAN/maintainability)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)

![Demo of UI](demo.gif)

Simultaneous Multi-Region Analysis.

## Installation

```Bash
git clone https://github.com/seankmartin/SIMURAN
cd SIMURAN
pip install ".[neurochat]"
```

## OS specific setup

### MAC OS

- To use the UI, you will need to perform at least the following. brew install libpng
- It is possible you may also need the MAC command line developer tools, but perhaps not.
- To use doit on MAC, you will need the developer tools.

## Objective

Currently, this can facilitate batch processing of many neural recordings in an easy to handle way.
Firstly, create a table which describes all of your recordings.
Then you can filter out specific recordings which match certain criteria.
A recording container stores these recordings which match these criteria, and provides some bridges between common neuroscience packages to facilate loading / analysing in different formats and with different packages

Here, the main object is to setup Recordings (containing all information relevant to an experiment, or part of an experiment) and RecordingContainers, which are a series of Recordings.

For instance, RecordingContainer could represent all t-maze running speed, spikes, etc. and associated metadata, while a Recording is an individual t-maze session.
This can then support easy extraction of subcontainers, such as, all trials which were successful in mice expressing a particular gene - in a simple filtering method with Pandas style.

Finally, these RecordingContainers can be used to facilitate batch processing of data, and establishing workflows for processing the data.

### GUI - WORK IN PROGRESS

Here, the focus is mostly on the Recording level, but multiple recordings can be bundled as blocks.

Recordings are loaded and processed via Nodes which are established through the UI and run in a digraph fashion.

## Using custom analysis code

SIMURAN can use any code that is on the Python path. The easiest way to manage this is to either:

1. Fork SIMURAN and place your custom analysis code in the SIMURAN package under the directory labelled custom.
2. Place your code on path separately, such as by creating a `setup.py` file for your code, or a `pyproject.toml` file for installation.
3. If you place python code and/or a file with the `.pth` extension in a directory named analysis in the same directory that batch_config_path is in, this `.pth` file will be automatically processed and its contents placed on path. If this option is chosen, it is recommended to store the analysis functions directly so that anyone can run the code without modification.
4. See [examples](https://github.com/seankmartin/neuro-tools/tree/master/SIMURAN).

## Inspiration

1. [GitHub - seankmartin/NeuroChaT: Analysis toolset with GUI for Neuroscience](https://github.com/seankmartin/NeuroChaT)
2. [SpikeInterface · GitHub](https://github.com/SpikeInterface)
3. [GitHub - seankmartin/NeuroChaT_API_Scripts: A set of python neuroscience scripts which rely on the NeuroChaT API](https://github.com/seankmartin/NeuroChaT_API_Scripts)
4. [GitHub - mne-tools/mne-python: MNE: Magnetoencephalography (MEG) and Electroencephalography (EEG) in Python](https://github.com/mne-tools/mne-python/)
5. [Sumatra - NeuralEnsemble](http://neuralensemble.org/sumatra/)

## TODO

1. Add more tests
2. Add more documentation
3. Convert bridge functions into classes
4. Add more examples
5. Add more nodes to the UI
6. Implement a direct threading system for the RecordingContainer
