# The MESSAGEix framework

## Overview

MESSAGEix is a versatile, open-source, dynamic systems-optimization model.
It was developed for strategic energy planning and integrated assessment of
energy-engineering-economy-environment systems (E4).
The framework includes the possibility for integration with the general-economy MACRO model
to incorporate the feedback from price changes on demand for commodities or energy services.
The mathematical formulation is based on the MESSAGE Integrated Assessment model 
developed at IIASA since the 1980s.

The MESSAGEix and MACRO models are implemented in [GAMS](http://www.gams.com).
This repository contains the GAMS code and a number of tutorials and examples
using stylized national energy system models.

The repository includes, as a git-submodule, the interface 
to the *ix modeling platform* (ixmp), a modeling "data warehouse"
for *integrated and cross-cutting* scenario analysis.


## License

Copyright 2018 IIASA Energy Program

The MESSAGEix framework is licensed under the Apache License, Version 2.0 (the "License");
you may not use the files in this repository except in compliance with the License.
You may obtain a copy of the License at <http://www.apache.org/licenses/LICENSE-2.0>.

Please refer to the [NOTICE](NOTICE.rst) for details and user guidelines.


## Documentation

A [documentation of the MESSAGEix framework](http://MESSAGEix.iiasa.ac.at/),
including the complete mathematical formulation and associated files,
is automatically created from mark-up comments in the GAMS code and the R/Python packages. 
The online documentation is synchronyzed with the contents of the master branch
of the repository [www.github.com/iiasa/message_ix](http://www.github.com/iiasa/message_ix).


## Scientific reference

Please cite the following manuscript when using the MESSAGEix framework and/or the ix modeling platform 
for scientific publications or technical reports:

  Daniel Huppmann, Matthew Gidden, Oliver Fricko, Peter Kolp, 
  Clara Orthofer, Michael Pimmer, Adriano Vinca, Alessio Mastrucci, Keywan Riahi, and Volker Krey. 
  "The |MESSAGEix| Integrated Assessment Model and the ix modeling platform". 2018, submitted. 
  Electronic pre-print available at [pure.iiasa.ac.at/15157/](https://pure.iiasa.ac.at/15157/).


## Dependency installation

Please follow the installation instructions
of the [ixmp](https://github.com/iiasa/ixmp/blob/master/README.md) package,
which is included as a submodule to this repository.
Instead of forking and cloning the GitHub repository [iiasa/ixmp](https://www.github.com/iiasa/ixmp),
please fork and clone the repository [iiasa/message_ix](http://www.github.com/iiasa/message_ix).
