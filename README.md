# The MESSAGEix framework

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.4005684.svg)](https://doi.org/10.5281/zenodo.4005684)
[![PyPI version](https://img.shields.io/pypi/v/message_ix.svg)](https://pypi.python.org/pypi/message_ix/)
[![Anaconda version](https://img.shields.io/conda/vn/conda-forge/message-ix)](https://anaconda.org/conda-forge/message-ix)
[![Documentation build](https://readthedocs.com/projects/iiasa-energy-program-message-ix/badge/?version=master)](https://docs.messageix.org/en/master/)
[![Build status](https://github.com/iiasa/message_ix/workflows/pytest/badge.svg)](https://github.com/iiasa/message_ix/actions?query=workflow:pytest)
[![Test coverage](https://codecov.io/gh/iiasa/message_ix/branch/master/graph/badge.svg)](https://codecov.io/gh/iiasa/message_ix)


MESSAGEix is a versatile, dynamic systems-optimization modeling framework developed by the IIASA Energy, Climate, and Environment (ECE) Program since the 1980s.

MESSAGE is a specific mathematical formulation of a model for strategic energy planning and integrated assessment of energy-engineering-economy-environment (E4) systems.
The linear-programming optimization model can be be linked to the general-equilibrium MACRO model to incorporate feedback between prices and demand levels for energy and commodities.

The `message_ix` Python package includes [GAMS](http://www.gams.com) implementations of MESSAGE, MACRO, and their linkage, along with scientific programming APIs and tools for model-building, a test suite, and documentation.
The framework is built on IIASA's [*ix* modeling platform (ixmp)](https://github.com/iiasa/ixmp), which provides data warehouse features for high-powered numerical scenario analysis.


## License

Copyright © 2018–2021 IIASA Energy, Climate, and Environment (ECE) Program

The MESSAGEix framework is licensed under the Apache License, Version 2.0 (the
"License"); you may not use the files in this repository except in compliance
with the License. You may obtain a copy of the License at
<http://www.apache.org/licenses/LICENSE-2.0>.

Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.

See the user guidelines and notice [in the online documentation](https://docs.messageix.org/en/stable/notice.html) or the file [`NOTICE.rst`](NOTICE.rst).


## Getting started

### Documentation

[Documentation of the MESSAGEix framework](https://docs.messageix.org/),
including the complete mathematical formulation and associated files, is
automatically created from mark-up comments in the GAMS, Python, and R code.

- Documentation for the ‘latest’ or ‘stable’ release is shown by default.
- Use the chooser to access the [docs for the ‘master’ branch](https://docs.messageix.org/en/master) of the GitHub repository, including the latest development code; or, to access docs for a specific version of message_ix, e.g. `v3.2.0`.
- For offline use, the documentation can be built from the source code.
  See the file `doc/README.rst`.

### Installation

See [the online documentation](https://docs.messageix.org/en/stable/#getting-started) or the file `INSTALL.rst`.

### Tutorials

For formal and self-guided learning, introductory tutorials are provided that
illustrate the basic features of the modelling framework using simplified, single-country models.
See [‘Tutorials’ in the documentation](https://docs.messageix.org/en/stable/tutorials.html) or the file `tutorial/README.rst`.


## Scientific reference

Please cite the following manuscript when using the MESSAGEix framework and/or
the ix modeling platform for scientific publications or technical reports:

> Daniel Huppmann, Matthew Gidden, Oliver Fricko, Peter Kolp, Clara Orthofer,
  Michael Pimmer, Nikolay Kushin, Adriano Vinca, Alessio Mastrucci,
  Keywan Riahi, and Volker Krey.
  "The |MESSAGEix| Integrated Assessment Model and the ix modeling platform".
  *Environmental Modelling & Software* 112:143-156, 2019.
  doi: [10.1016/j.envsoft.2018.11.012](https://doi.org/10.1016/j.envsoft.2018.11.012)
  electronic pre-print available at
  [pure.iiasa.ac.at/15157/](https://pure.iiasa.ac.at/15157/)

You may also cite the latest released version using the Zenodo DOI; again, see the `NOTICE`.
