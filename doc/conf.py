# Configuration file for the Sphinx documentation builder.
#
# This file only contains a selection of the most common options. For a full
# list see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Path setup --------------------------------------------------------------

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.

from pathlib import Path

from pkg_resources import get_distribution

# -- Project information -----------------------------------------------------

project = "MESSAGEix"
copyright = "2021, IIASA Energy, Climate, and Environment (ECE) Program"
author = "MESSAGEix Developers"

# The major project version, used as the replacement for |version|.
version = get_distribution("message_ix").version
# The full project version, used as the replacement for |release| and e.g. in
# the HTML templates.
release = version


# -- General configuration ----------------------------------------------------

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.doctest",
    "sphinx.ext.extlinks",
    "sphinx.ext.intersphinx",
    "sphinx.ext.todo",
    "sphinx.ext.coverage",
    "sphinx.ext.mathjax",
    "sphinxcontrib.bibtex",
    "sphinx.ext.autosummary",
    "sphinx.ext.napoleon",
    "message_ix.util.sphinx_gams",
]

# Add any paths that contain templates here, relative to this directory.
templates_path = ["_templates"]

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = ["_build", "README.rst"]

# A string of reStructuredText that will be included at the beginning of every
# source file that is read.
rst_prolog = r"""
.. |MESSAGEix| replace:: MESSAGE\ :emphasis:`ix`

.. |ixmp| replace:: :emphasis:`ix` modeling platform

.. |IIASA| raw:: html

   <abbr title="International Institute for Applied Systems Analysis">IIASA</abbr>

.. role:: strike

.. role:: underline

"""  # noqa: E501

# -- Options for HTML output ----------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
html_theme = "sphinx_rtd_theme"

# A list of CSS files.
html_css_files = ["custom.css"]

# The name of an image file (relative to this directory) to place at the top
# of the sidebar.
html_logo = "_static/logo_white.png"

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ["_static"]

# -- Options for LaTeX output -------------------------------------------------

# The LaTeX engine to build the docs.
latex_engine = "lualatex"


# -- Options for sphinx.ext.extlinks ------------------------------------------

extlinks = {
    "pull": ("https://github.com/iiasa/message_ix/pull/%s", "PR #"),
}


# -- Options for sphinx.ext.intersphinx ---------------------------------------

intersphinx_mapping = {
    "dask": ("https://docs.dask.org/en/stable/", None),
    "ixmp": ("https://docs.messageix.org/projects/ixmp/en/latest/", None),
    # For a local build, uncomment and use the following line with a path to
    # the directory containing built HTML documentation for ixmp:
    # 'ixmp': ('/home/user/path-to-ixmp/doc/build/html', None),
    "pandas": ("https://pandas.pydata.org/pandas-docs/stable/", None),
    "pint": ("https://pint.readthedocs.io/en/stable/", None),
    "pyam": ("https://pyam-iamc.readthedocs.io/en/stable/", None),
    "python": ("https://docs.python.org/3/", None),
}


# -- Options for sphinx.ext.todo ----------------------------------------------

# If true, `todo` and `todoList` produce output, else they produce nothing.
todo_include_todos = True


# -- Options for sphinxcontrib.bibtex -----------------------------------------

bibtex_bibfiles = ["references.bib"]


# -- Options for message_ix.util.sphinx_gams -------------------------------------------

gams_source_dir = Path(__file__).parents[1].joinpath("message_ix", "model")
gams_target_dir = "model"
