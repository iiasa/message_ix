# The MESSAGEix framework

[![PyPI version](https://img.shields.io/pypi/v/message_ix.svg)](https://pypi.python.org/pypi/message_ix/)
[![Anaconda version](https://img.shields.io/conda/vn/conda-forge/message-ix)](https://anaconda.org/conda-forge/message-ix)
[![Documentation build](https://readthedocs.com/projects/iiasa-energy-program-message-ix/badge/?version=master)](https://message.iiasa.ac.at/en/master/)
[![Build status](https://travis-ci.org/iiasa/message_ix.svg?branch=master)](https://travis-ci.org/iiasa/message_ix)
[![Test coverage](https://codecov.io/gh/iiasa/message_ix/branch/master/graph/badge.svg)](https://codecov.io/gh/iiasa/message_ix)

## Overview

MESSAGEix is a versatile, open-source, dynamic systems-optimization model.
It was developed for strategic energy planning and integrated assessment of
energy-engineering-economy-environment (E4) systems. The framework includes the
possibility for integration with the general-economy MACRO model to incorporate
the feedback from price changes on demand for commodities or energy services.
The mathematical formulation is based on the MESSAGE Integrated Assessment
model developed at IIASA since the 1980s.

The MESSAGEix and MACRO models are implemented in [GAMS](http://www.gams.com).
This repository contains the GAMS code and a number of tutorials and examples
using stylized national energy system models.

The MESSAGEix framework is fully integrated with IIASA's
[ix modeling platform (ixmp)](https://www.github.com/iiasa/ixmp),
a data warehouse for high-powered numerical scenario analysis.


## License

Copyright © 2018–2020 IIASA Energy Program

The MESSAGEix framework is licensed under the Apache License, Version 2.0 (the
"License"); you may not use the files in this repository except in compliance
with the License. You may obtain a copy of the License at
<http://www.apache.org/licenses/LICENSE-2.0>.

Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.

Please refer to the [NOTICE](NOTICE.rst) for details and user guidelines.


## Getting started

### Documentation

[Documentation of the MESSAGEix framework](https://message.iiasa.ac.at/),
including the complete mathematical formulation and associated files, is
automatically created from mark-up comments in the GAMS, Python, and R code.
The online documentation is synchronized with the contents of the master branch
of the [message_ix Github repository](https://github.com/iiasa/message_ix).

For offline use, the documentation can be built from the source code.
See `doc/README.md` for further details.


### Installation

See [‘Installation’ in the documentation](https://message.iiasa.ac.at/en/1.2.x/getting_started.html) or the file `INSTALL.rst`.


### Tutorials

Several introductory tutorials are provided.
See [‘Tutorials’ in the documentation](https://message.iiasa.ac.at/en/1.2.x/tutorials.html) or the file
`tutorial/README.rst`.


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
