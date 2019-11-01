# Installation script for Linux/macOS CI on Travis

# Install GAMS
$CACHE/$GAMSFNAME > install.out

# Show location
which gams


# Install and update conda
# -b: run in batch mode with no user input
# -u: update existing installation
# -p: install prefix
$CACHE/$CONDAFNAME -b -u -p $HOME/miniconda
conda update --yes conda pip

# Search conda-forge in addition to the default channels, for e.g. JPype
conda config --append channels conda-forge

# Create and activate named environment
conda create --yes --name testing python=$PYVERSION pip
. activate testing

# Install dependencies
conda install --yes --name testing --file ci/conda-requirements.txt
pip install --requirement ci/pip-requirements.txt

# Temporary: see https://github.com/IAMconsortium/pyam/issues/281
pip install "matplotlib>3.0.2"

# Show information
conda info --all
