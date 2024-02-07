# Configuration file for the Sphinx documentation builder.
#
# This file only contains a selection of the most common options. For a full
# list see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Path setup --------------------------------------------------------------

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.
#
# import os
# import sys
# sys.path.insert(0, os.path.abspath('.'))
import sys
import os
from datetime import date
import sphinx_rtd_theme
from pkg_resources import get_distribution

# -- Project information -----------------------------------------------------
try:
    from importlib.metadata import version as get_version

    version = get_version("km3io")
except ImportError:
    from pkg_resources import get_distribution

    version = get_distribution("km3io").version

short_version = ".".join(version.split(".")[:2])
project = "km3io {}".format(short_version)
copyright = "{0}, Zineb Aly and Tamas Gal".format(date.today().year)
author = "Zineb Aly, Tamas Gal, Johannes Schumann"

# -- General configuration ---------------------------------------------------

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.autosummary",
    "sphinx.ext.viewcode",
    "autoapi.extension",
    "numpydoc",
    "sphinx_gallery.gen_gallery",
]

# Add any paths that contain templates here, relative to this directory.
templates_path = ["_templates"]

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]

# AutoAPI
autoapi_type = "python"
autoapi_dirs = ["../src/km3io"]
autoapi_options = ["members", "undoc-members", "show-module-summary"]
autoapi_include_summaries = True

# Gallery
sphinx_gallery_conf = {
    "backreferences_dir": "modules/generated",
    "default_thumb_file": "_static/default_gallery_thumbnail.png",
    "examples_dirs": "../examples",  # path to your example scripts
    "gallery_dirs": "auto_examples",  # path to where to save gallery generated output
    "show_memory": True,
}

# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
#
html_theme = "sphinx_rtd_theme"
html_theme_path = [sphinx_rtd_theme.get_html_theme_path()]

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ["_static"]
html_title = "km3io {}".format(version)
