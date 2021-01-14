===============
Getting Started
===============

Installation
------------
.. code-block:: shell

   git clone https://github.com/seankmartin/SIMURAN
   cd SIMURAN
   pip install -e .

File structure
--------------

Mapping file
^^^^^^^^^^^^
Layout channels, wires, brain areas, etc. should be provided per animal (simuran_base_params).

Function file
^^^^^^^^^^^^^
Which functions to run on the data, what data and figures to save, and sort input files (simuran_fn_params).

Batch file
^^^^^^^^^^
Which files to select from a directory to run on, for example by using a REGEX pattern (simuran_base_params).

Multi-batch file
^^^^^^^^^^^^^^^^
Run a series of batch files, optionally merging the results afterwards, or running a final analysis on the compiled results (e.g.) clustering.

Examples
--------
Check out the examples in the examples folder of the main GitHub repository.
When these are a bit cleaner, I'll pop them up here also.