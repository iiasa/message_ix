# The MESSAGEix framework

## Overview

MESSAGEix is a versatile systems optimization model.
The framework includes the possibility for integration with the general-economy MACRO model.
The MESSAGEix and MACRO models are implemented in [GAMS](http://www.gams.com).
The mathematical formulation is based on the MESSAGE Integrated Assessment model 
developed at IIASA since the 1980s.

This repository contains the GAMS implementation of the MESSAGEix framework
and the interface to the ix modeling platform (ixmp), 
as well as a number of tutorials and examples using simple .


## License

Copyright 2017 IIASA Energy Program

The MESSAGEix framework is licensed under the Apache License, Version 2.0 (the "License");
you may not use the files in this repository except in compliance with the License.
You may obtain a copy of the License at <http://www.apache.org/licenses/LICENSE-2.0>.

Please refer to the [NOTICE](NOTICE.md) for details and the user guidelines.


## Documentation

A [documentation of the MESSAGEix framework](http://www.iiasa.ac.at/message_ix),
including the complete mathematical formulation and the model run workflow logic,
is automatically created from mark-up comments in the GAMS code and the R/Python packages. 
The online documentation is synchronyzed with the contents of the master branch
of the repository [www.github.com/iiasa/message_ix](http://www.github.com/iiasa/message_ix).


## Dependency Installation

Please follow the installation instructions of the [ixmp](ixmp/README.md) package,
which is included as a submodule to this repository.
Instead of forking and cloning the GitHub repository [iiasa/ixmp](https://www.github.com/iiasa/ixmp),
please fork and clone the the repository [iiasa/message_ix](http://www.github.com/iiasa/message_ix).
