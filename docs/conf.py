# Configuration file for the Sphinx documentation builder.
#
# This file only contains a selection of the most common options. For a full
# list see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

import importlib.metadata
import re

# -- Project information -----------------------------------------------------

project = "Virtue"
author = "Julian Berman"
copyright = "2014, " + author

release = importlib.metadata.version("virtue")
version = release.partition("-")[0]


# -- General configuration ---------------------------------------------------

# The reST default role (used for this markup: `text`) to use for all documents
default_role = "any"

extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.autosectionlabel",
    "sphinx.ext.coverage",
    "sphinx.ext.doctest",
    "sphinx.ext.intersphinx",
    "sphinx.ext.napoleon",
    "sphinx.ext.viewcode",
    "sphinxcontrib.spelling",
]

# Add any paths that contain templates here, relative to this directory.
templates_path = ["_templates"]

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]


# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
#
html_theme = "furo"

# Theme options are theme-specific and customize the look and feel of a theme
# further.  For a list of options available for each theme, see the
# documentation.
#
# html_theme_options = {}

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
# html_static_path = ["_static"]


# -- Extension configuration -------------------------------------------------

# -- Options for autodoc extension -------------------------------------------

autodoc_default_options = {
    "members": True,
    "member-order": "bysource",
}

# -- Options for autosectionlabel extension ----------------------------------

autosectionlabel_prefix_document = True

# -- Options for intersphinx extension ---------------------------------------

# Example configuration for intersphinx: refer to the Python standard library.
intersphinx_mapping = dict(
    python=("https://docs.python.org/3", None),
    twisted=("https://twistedmatrix.com/documents/current/api/", None),
)

# -- Options for the linkcheck builder ------------------------------------


def entire_domain(host):
    return r"http.?://" + re.escape(host) + r"($|/.*)"


linkcheck_ignore = [
    entire_domain("codecov.io"),
    "https://github.com/Julian/Virtue/actions",
    "https://github.com/Julian/Virtue/workflows/CI/badge.svg",
]

# -- Options for sphinxcontrib-spelling -----------------------------------

spelling_word_list_filename = "spelling-wordlist.txt"
