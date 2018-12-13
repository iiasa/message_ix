# The MESSAGEix framework

## Overview

MESSAGEix is a versatile, open-source, dynamic systems-optimization model.  It
was developed for strategic energy planning and integrated assessment of
energy-engineering-economy-environment systems (E4).  The framework includes the
possibility for integration with the general-economy MACRO model to incorporate
the feedback from price changes on demand for commodities or energy services.
The mathematical formulation is based on the MESSAGE Integrated Assessment model
developed at IIASA since the 1980s.

The MESSAGEix and MACRO models are implemented in [GAMS](http://www.gams.com).
This repository contains the GAMS code and a number of tutorials and examples
using stylized national energy system models.

The MESSAGEix framework is fully integrated with IIASA's
[ix modeling platform (ixmp)](https://www.github.com/iiasa/ixmp),
a data warehouse for high-powered numerical scenario analysis.


## License

Copyright 2018 IIASA Energy Program

The MESSAGEix framework is licensed under the Apache License, Version 2.0 (the
"License"); you may not use the files in this repository except in compliance
with the License.  You may obtain a copy of the License at
<http://www.apache.org/licenses/LICENSE-2.0>.

Please refer to the [NOTICE](NOTICE.rst) for details and user guidelines.


## Documentation

A [documentation of the MESSAGEix framework](http://MESSAGEix.iiasa.ac.at/),
including the complete mathematical formulation and associated files, is
automatically created from mark-up comments in the GAMS code and the R/Python
packages.  The online documentation is synchronyzed with the contents of the
master branch of the repository
[www.github.com/iiasa/message_ix](http://www.github.com/iiasa/message_ix).


## Scientific reference

Please cite the following manuscript when using the MESSAGEix framework and/or
the ix modeling platform for scientific publications or technical reports:

  Daniel Huppmann, Matthew Gidden, Oliver Fricko, Peter Kolp, Clara Orthofer,
  Michael Pimmer, Adriano Vinca, Alessio Mastrucci, Keywan Riahi, and Volker
  Krey.  "The |MESSAGEix| Integrated Assessment Model and the ix modeling
  platform". 2018, submitted.  Electronic pre-print available at
  [pure.iiasa.ac.at/15157/](https://pure.iiasa.ac.at/15157/).



## Install from Conda (New Users)

1. Install Python via [Anaconda](https://www.anaconda.com/download/). We
   recommend the latest version, e.g., Python 3.6+.

2. Install [GAMS](https://www.gams.com/download/). **Importantly**:

   - Windows:
      - Check the box labeled `Use advanced installation mode`
      - Check the box labeled `Add GAMS directory to PATH environment variable` on
        the Advanced Options page.
   - MacOSX/Linux:
      - Add the following line to you `.bash_profile` (Mac) or `.bashrc` (Linux)

         ```
         export PATH=$PATH:/path/to/gams-directory-with-gams-binary
         ```

3. Open a command prompt and type

    ```
    conda install -c conda-forge message-ix
    ```


## Install from Source (Advanced Users)

1. Follow the installation instructions of the
   [ixmp](https://github.com/iiasa/ixmp#install-from-source-advanced-users)
   package.

2. Fork this repository and clone the forked repository (`<user>/message_ix`)
   to your machine. Add `iiasa/message_ix` as `upstream` to your clone.

3. Open a command prompt in the `message_ix` directory and type

      ```
      python setup.py install && py.test tests
      ```

## Configure Model Files

By default, the model files (e.g., GAMS files) are installed with `message_ix`
(in your Python `site-packages` directory). Many users will simply want to run
MESSAGEix, and will never need to see the these files; however, some users will
want to edit the files directly to change the mathematical formulation, such as
adding new types of parameters, constraints, etc. Accordingly, we provide a
utility to place the model files in a local directory of your choosing:

   ```
   messageix-config --model_path /path/to/model
   ```

Please note, if you cloned this repository and installed MESSAGEix with
`install.bat`, this command has already been run, pointing to
`message_ix/model`.

## Getting Tutorial Files

If you installed from source, all tutorial files are in the `tutorial`
folder. If you installed from conda, you can download them to your machine by
opening a command prompt and typing

   ```
   messageix-dl --local_path /path/to/tutorials
   ```

## Running Tutorials

### Using Anaconda

1. Additionally install the following package:

    ```
    conda install nb_conda
    ```

2. Open Jupyter Notebooks from Anaconda's "Home" Tab (or directly if you have
   the option)

3. Open the tutorial notebook file

4. Make sure the Kernel is aligned with your conda environment

   - Change kernels with menu options `Kernel` -> `Change Kernel` -> `Python
     [conda root]` (for example)

### Using Command Line

Navigate to the tutorial folder and type

   ```
   jupyter notebook
   ```

## Building Documentation

Navigate to the `doc` folder and in a command prompt type

   ```
   make doc
   ```
