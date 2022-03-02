'''
Configuration file for the Sphinx documentation builder.
This file only contains a selection of the most common options. For a full
# list see the documentation:
# http://www.sphinx-doc.org/en/master/config
'''

# -- Path setup --------------------------------------------------------------

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.

import datetime
import os
import sys

sys.path.insert(0, os.path.abspath('..'))

# -- The master toctree document
root_doc = 'index'

#pylint: disable=invalid-name
# -- Project information -----------------------------------------------------

project = 'Lambda Packager'
copyright = f'{datetime.datetime.now().year}, 3M' #pylint: disable=redefined-builtin
author = '3M'

# -- General configuration ---------------------------------------------------

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = [
    'sphinx.ext.napoleon',
    'sphinx.ext.autodoc',
    'sphinx_autodoc_typehints',
    'recommonmark',
]


# Napoleon settings
napoleon_google_docstring = True

# Add any paths that contain templates here, relative to this directory.
templates_path = ['_templates']

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = ['_build', 'Thumbs.db', '_docs', '.DS_Store']

# -- Parser Options ---------------------------------------------------------

source_suffix = {
    '.rst': 'restructuredtext',
    '.md': 'markdown',
}

# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.

html_theme = 'classic'

# 3M Sphinx theme options (see theme.conf for more information)
html_theme_options = {
    # Set the name of the project to appear in the sidebar
    'repo_url': 'https://github.com/3mcloud/lambda-packager',
    'repo_name': 'lambda-packager',
}

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".

html_static_path = []
