"""
Configuration file for the Sphinx documentation builder.

See https://www.sphinx-doc.org/en/master/usage/configuration.html
"""

# -- Path setup --------------------------------------------------------------

import os
import sys

curdir = os.path.dirname(__file__)
package_location = os.path.abspath(os.path.join(curdir, "../"))
sys.path.append(package_location)


# -- Project information -----------------------------------------------------

project = "simuran"
copyright = "2023, Sean K. Martin"
author = "Sean K. Martin"

# The full version, including alpha/beta/rc tags
release = "23.08.0"


# -- General configuration ---------------------------------------------------

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = ["sphinx.ext.napoleon", "sphinxcontrib.apidoc", "sphinx.ext.todo"]

# Add any paths that contain templates here, relative to this directory.
templates_path = ["_templates"]

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store", "reference/modules.rst"]


# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
#
html_theme = "sphinx_rtd_theme"

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ["_static"]

master_doc = "index"

# -- Apidoc configuration ----------------------------------------------------
apidoc_module_dir = "../simuran"
apidoc_output_dir = "reference"
apidoc_excluded_paths = ["tests"]
apidoc_separate_modules = True
