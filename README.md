# The MESSAGEix framework

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.4005684.svg)](https://doi.org/10.5281/zenodo.4005684)
[![PyPI version](https://img.shields.io/pypi/v/message_ix.svg)](https://pypi.python.org/pypi/message_ix/)
[![Anaconda version](https://img.shields.io/conda/vn/conda-forge/message-ix)](https://anaconda.org/conda-forge/message-ix)
[![Documentation build](https://readthedocs.com/projects/iiasa-energy-program-message-ix/badge/?version=stable)](https://docs.messageix.org/en/stable/)
[![Build status](https://github.com/iiasa/message_ix/actions/workflows/pytest.yaml/badge.svg)](https://github.com/iiasa/message_ix/actions/workflows/pytest.yaml)
[![Test coverage](https://codecov.io/gh/iiasa/message_ix/branch/main/graph/badge.svg)](https://codecov.io/gh/iiasa/message_ix)


MESSAGEix is a versatile, dynamic, model framework for energy-engineering-economy-environment (E4) systems research.

**MESSAGE** (without “…ix”) is a specific formulation of a generic linear programming (LP) optimization model for strategic energy planning and integrated assessment of E4 systems, developed by the IIASA Energy, Climate, and Environment (ECE) Program since the 1980s.
To incorporate feedback between prices and demand levels for energy and commodities, the LP model can optionally be linked to the economic general equilibrium (GE) **MACRO** model.

The `message_ix` Python package—also fully usable from R—includes:

- Implementations of MESSAGE, MACRO, and their linkage, in GAMS,
- Application programming interfaces (APIs) and tools for model building and scientific programming,
- Extensive documentation and a complete test suite.

The framework is built on IIASA's [*ix* modeling platform (`ixmp`)](https://github.com/iiasa/ixmp), which provides data warehouse features for high-powered numerical scenario analysis.

## Documentation

Complete documentation of the framework is avaiable at **https://docs.messageix.org/**.
This includes:

- **Installation** and recommended pre-requisite learning.
  See [‘Getting started’](https://docs.messageix.org/en/stable/#getting-started), or the file [`INSTALL.rst`](INSTALL.rst).
- **Tutorials** that introduce and demonstrate core features of the model framework using simple, single-country models, for both independent and classroom learning.
  See [‘Tutorials’](https://docs.messageix.org/en/stable/tutorials.html) or the file  [`tutorial/README.rst`](tutorial/README.rst).
- The [**Python and R APIs**](https://docs.messageix.org/en/stable/api.html).
- The complete [**mathematical formulation**](https://docs.messageix.org/#mathematical-specification) of MESSAGE and MACRO, created automatically from inline comments in the GAMS source code.
- How to **cite MESSAGEix when using it in published scientific work.**
  See [‘User guidelines and notice’](https://docs.messageix.org/en/stable/notice.html) or the file [`NOTICE.rst`](NOTICE.rst).

Other forms of documentation:

- The online documentation is built automatically from the contents of the
[`message_ix` GitHub repository](https://github.com/iiasa/messag_ix).
- Documentation for the ‘latest’ or ‘stable’ release is shown by default.
- Use the chooser to access the [‘latest’ version](https://docs.messageix.org/en/latest/), corresponding to the ``main`` branch and including the latest development code; or to access docs for a specific release, e.g. `v3.2.0`.
- For offline use, the documentation can be built from the source code.
  See the file [`doc/README.rst`](doc/README.rst)

## License

Copyright © 2018–2022 IIASA Energy, Climate, and Environment (ECE) Program

The MESSAGEix framework is licensed under the Apache License, Version 2.0 (the "License"); you may not use the files in this repository except in compliance with the License. You may obtain a copy of the License in [`LICENSE`](LICENSE) or at <http://www.apache.org/licenses/LICENSE-2.0>.

In addition and per good scientific practice, you **must** cite the appropriate publications when you use MESSAGEix in scientific work.
Again, see [‘User guidelines and notice’](https://docs.messageix.org/en/stable/notice.html) or the file [`NOTICE.rst`](NOTICE.rst).
