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

# Create and activate named environment
conda create --yes --name testing python=$PYVERSION pip
. activate testing

# Install dependencies
conda install --yes --name testing --file ci/conda-requirements.txt
pip install --requirement ci/pip-requirements.txt

# Show information
conda info --all
