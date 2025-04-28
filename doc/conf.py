# Configuration file for the Sphinx documentation builder.
#
# This file only contains a selection of the most common options. For a full
# list see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

import os
from importlib.metadata import version as get_version
from pathlib import Path
from typing import Optional

# -- Project information ---------------------------------------------------------------

project = "MESSAGEix"
copyright = "2018–%Y, IIASA Energy, Climate, and Environment (ECE) Program"
author = "MESSAGEix Developers"

# The major project version, used as the replacement for |version|.
version = get_version("message_ix")
# The full project version, used as the replacement for |release| and in HTML templates.
release = version

# -- General configuration -------------------------------------------------------------

# Add any Sphinx extension module names here, as strings. They can be extensions coming
# with Sphinx (named 'sphinx.ext.*') or your custom ones.
extensions = [
    # First-party
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
    # Others
    "genno.compat.sphinx.rewrite_refs",
    "ixmp.util.sphinx_linkcode_github",
    "message_ix.util.sphinx_gams",
]

# Add any paths that contain templates here, relative to this directory.
templates_path = ["_templates"]

# List of patterns, relative to source directory, that match files and directories to
# ignore when looking for source files. This pattern also affects html_static_path and
# html_extra_path.
exclude_patterns = ["_build", "README.rst"]

nitpicky = True

# A string of reStructuredText that will be included at the beginning of every source
# file that is read.
rst_prolog = r"""
.. role:: py(code)
   :language: python

.. role:: strike
.. role:: underline

.. |MESSAGEix| replace:: MESSAGE\ :emphasis:`ix`
.. |ixmp| replace:: :emphasis:`ix` modeling platform
.. |IIASA| raw:: html

   <abbr title="International Institute for Applied Systems Analysis">IIASA</abbr>

.. |yA| replace:: :math:`y^A`
.. |yV| replace:: :math:`y^V`
"""

# Add reST replacements for references to particular MESSAGE/MACRO model items. These
# are of the form ".. |foo| replace:: :ref:`foo <foo>`", such that |foo| in reST links
# to the hyperlink target #foo with the text 'foo'. The explicit text is needed because
# sometimes multiple targets appear above a single heading, and that heading text would
# be automatically used for the link text.
for name in (
    "duration_period",
    "duration_period_sum",
    "growth_new_capacity_up",
    "historical_new_capacity",
    "initial_new_capacity_up",
    "map_tec_lifetime",
    "remaining_capacity",
):
    rst_prolog += f"\n.. |{name}| replace:: :ref:`{name} <{name}>`"


# -- Options for HTML output -----------------------------------------------------------

# A list of CSS files.
html_css_files = ["custom.css"]

html_favicon = "_static/messageix-favicon.svg"

# The name of an image file (relative to this directory) to place at the top of the
# sidebar.
html_logo = "_static/combined-logo-white.svg"

# Add any paths that contain custom static files (such as style sheets) here, relative
# to this directory. They are copied after the builtin static files, so a file named
# "default.css" will overwrite the builtin "default.css".
html_static_path = ["_static"]

# The theme to use for HTML and HTML Help pages.
html_theme = "sphinx_rtd_theme"

html_theme_options = {"logo_only": True}

# Define the canonical URL if you are using a custom domain on Read the Docs
html_baseurl = os.environ.get("READTHEDOCS_CANONICAL_URL", "")

# Tell Jinja2 templates the build is running on Read the Docs
if os.environ.get("READTHEDOCS", "") == "True":
    if "html_context" not in globals():
        html_context = {}
    html_context["READTHEDOCS"] = True

# -- Options for LaTeX output ----------------------------------------------------------

# The LaTeX engine to build the docs.
latex_engine = "lualatex"

# -- Options for genno.compat.sphinx.rewrite_refs --------------------------------------

# When base classes in upstream (genno, ixmp) packages are inherited in message_ix,
# Sphinx will not properly resolve relative references within docstrings of methods of
# the former. Some of these aliases are to allow Sphinx to locate the correct targets.
reference_aliases = {
    # genno
    "AnyQuantity": ":data:`genno.core.quantity.AnyQuantity`",
    "Computer": "genno.Computer",
    "Graph": "genno.core.graph.Graph",
    "Operator": "genno.Operator",
    "KeyLike": ":data:`genno.core.key.KeyLike`",
    "iter_keys": "genno.core.key.iter_keys",
    "single_key": "genno.core.key.single_key",
    r"(genno\.|)Key(?=Seq|[^\w]|$)": "genno.core.key.Key",
    r"(genno\.|)Quantity": "genno.core.attrseries.AttrSeries",
    # ixmp
    "ItemType": "ixmp.backend.ItemType",
    "Platform": "ixmp.Platform",
    "TimeSeries": "ixmp.TimeSeries",
    #
    # Many projects (including Sphinx itself!) do not have a py:module target in for the
    # top-level module in objects.inv. Resolve these using :doc:`index` or similar for
    # each project.
    "dask$": ":std:doc:`dask:index`",
    "plotnine$": ":class:`plotnine.ggplot`",
}

# -- Options for ixmp.util.sphinx_linkcode_github / sphinx.ext.linkcode ----------------

linkcode_github_repo_slug = "iiasa/message_ix"

# -- Options for message_ix.util.sphinx_gams -------------------------------------------

gams_source_dir = Path(__file__).parents[1].joinpath("message_ix", "model")
gams_target_dir = "model"

# -- Options for sphinx.ext.extlinks ---------------------------------------------------

# Link to "main" blob if a non-release version of the docs is being built; otherwise
# to the tag for the release
gh_ref = "main" if ".dev" in version else f"v{version}"

extlinks = {
    "issue": ("https://github.com/iiasa/message_ix/issue/%s", "#%s"),
    "pull": ("https://github.com/iiasa/message_ix/pull/%s", "PR #%s"),
    "tut": (f"https://github.com/iiasa/message_ix/blob/{gh_ref}/tutorial/%s", None),
}

# -- Options for sphinx.ext.intersphinx ------------------------------------------------


def local_inv(name: str, *parts: str) -> Optional[str]:
    """Construct the path to a local intersphinx inventory."""

    from importlib.util import find_spec

    spec = find_spec(name)
    if spec is None:
        return None

    if 0 == len(parts):
        parts = ("doc", "_build", "html")
    assert spec.origin is not None
    return str(Path(spec.origin).parents[1].joinpath(*parts, "objects.inv"))


intersphinx_mapping = {
    "dask": ("https://docs.dask.org/en/stable/", None),
    "genno": ("https://genno.readthedocs.io/en/latest", (local_inv("genno"), None)),
    "ixmp": (
        "https://docs.messageix.org/projects/ixmp/en/latest/",
        (local_inv("ixmp"), None),
    ),
    "message-ix-models": (
        "https://docs.messageix.org/projects/models/en/latest/",
        None,
    ),
    "pandas": ("https://pandas.pydata.org/pandas-docs/stable/", None),
    "pint": ("https://pint.readthedocs.io/en/stable/", None),
    "plotly": ("https://plotly.com/python-api-reference", None),
    "plotnine": ("https://plotnine.org", None),
    "pyam": ("https://pyam-iamc.readthedocs.io/en/stable/", None),
    "python": ("https://docs.python.org/3/", None),
    "sphinx": ("https://www.sphinx-doc.org/en/master/", None),
    "xarray": ("https://docs.xarray.dev/en/stable", None),
}

# -- Options for sphinx.ext.mathjax ----------------------------------------------------

# See https://github.com/iiasa/message_ix/pull/721#pullrequestreview-1497907368:
# prefer to write \text{} explicitly
# TODO read at least some of these from message_ix.models
# TODO complete list
# TODO also add these to a LaTeX preamble
macros = {}
macros.update(
    {
        k.replace("_", ""): r"\text{{{k}}}"
        for k in """ACT
STORAGE
STORAGE_CHARGE
duration_time_rel
input
map_time_commodity_storage
storage_initial
storage_self_discharge""".split()
    }
)
macros.update(
    {
        "dp": r"\text{duration_period}",
        "hnc": r"\text{historical_new_capacity}",
        "mtl": r"\text{map_tec_lifetime}",
        "tl": r"\text{technical_lifetime}",
    }
)

mathjax3_config = dict(tex=dict(macros=macros))

# -- Options for sphinx.ext.napoleon ---------------------------------------------------

napoleon_preprocess_types = True
napoleon_type_aliases = {
    # Standard library
    "callable": ":ref:`callable <python:callable-types>`",
    "iterable": ":class:`collections.abc.Iterable`",
    "mapping": ":class:`collections.abc.Mapping`",
    "sequence": ":class:`collections.abc.Sequence`",
    # Upstream
    "DataFrame": "pandas.DataFrame",
    "Series": "pandas.Series",
    "Quantity": "genno.Quantity",
}

# -- Options for sphinx.ext.todo -------------------------------------------------------

# If true, `todo` and `todoList` produce output, else they produce nothing.
todo_include_todos = True

# -- Options for sphinxcontrib.bibtex --------------------------------------------------

bibtex_bibfiles = ["references.bib"]
