"""How to install simuran."""

import os
from setuptools import setup, find_packages


def read(fname):
    """Read files from the main source dir."""
    return open(os.path.join(os.path.dirname(__file__), fname)).read()


DESCRIPTION = "SIMURAN: Simulataneous Multi-Region Analysis"
LONG_DESCRIPTION = """Simuran is a giant from Philippine Mythology."""

DISTNAME = "simuran"
MAINTAINER = "Sean Martin"
MAINTAINER_EMAIL = "martins7@tcd.ie"
URL = "https://github.com/seankmartin/SIMURAN"
DOWNLOAD_URL = "https://github.com/seankmartin/SIMURAN"
VERSION = "0.0.1"

INSTALL_REQUIRES = [
    "matplotlib >= 3.0.2",
    "numpy >= 1.15.0",
    "skm_pyutils",
    "seaborn",
    "more_itertools",
    "indexed",
    "tqdm",
    "doit",
]

CLASSIFIERS = [
    "Intended Audience :: Science/Research",
    "Programming Language :: Python :: 3.6",
    "Programming Language :: Python :: 3.7",
    "Programming Language :: Python :: 3.8",
    "Topic :: Scientific/Engineering :: Mathematics",
    "Operating System :: POSIX",
    "Operating System :: Unix",
    "Operating System :: MacOS",
    "Operating System :: Windows",
]

ENTRY_POINTS = {
    "console_scripts": [
        "simuran = simuran.cli:cli_entry",
        "simuran-merge = simuran.cli:merge_entry",
    ],
}

if __name__ == "__main__":

    setup(
        name=DISTNAME,
        author=MAINTAINER,
        author_email=MAINTAINER_EMAIL,
        maintainer=MAINTAINER,
        maintainer_email=MAINTAINER_EMAIL,
        description=DESCRIPTION,
        long_description=LONG_DESCRIPTION,
        license=read("LICENSE"),
        url=URL,
        version=VERSION,
        download_url=DOWNLOAD_URL,
        install_requires=INSTALL_REQUIRES,
        include_package_data=True,
        packages=find_packages(),
        classifiers=CLASSIFIERS,
        entry_points=ENTRY_POINTS,
    )
