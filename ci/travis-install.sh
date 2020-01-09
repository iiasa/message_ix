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

# - Less noisy output
# - Search conda-forge in addition to the default channels, for e.g. JPype
# conda config --set quiet true
conda config --set always_yes true \
             --append channels conda-forge

# Create, update, and activate named environment
conda create --name testing python=$PYVERSION pip
conda update --name testing conda
. activate testing

# Install dependencies
conda install --name testing --file ci/conda-requirements.txt
pip install --requirement ci/pip-requirements.txt

# Temporary: see https://github.com/IAMconsortium/pyam/issues/281
pip install "matplotlib>3.0.2"

# Show information
conda info --all
