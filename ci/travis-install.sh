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

# Create named environment
conda create --yes -n testing python=$PYVERSION pip

# Install dependencies
conda install --yes --file ci/conda-requirements.txt
pip install --requirement ci/pip-requirements.txt

# Activate the environment. Use '.' (POSIX) instead of 'source' (a bashism).
. activate testing

# Show information
conda info --all
