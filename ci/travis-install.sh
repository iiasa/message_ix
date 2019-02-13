#!/bin/bash
set -x
set -e

# install gams
echo "Starting download from $GAMSURL"
wget $GAMSURL
echo "Download complete from $GAMSURL"
chmod u+x $GAMSFNAME
./$GAMSFNAME > install.out
which gams

# install and update conda
echo "Starting download from $CONDAURL"
wget $CONDAURL -O miniconda.sh
echo "Download complete from $CONDAURL"
chmod +x miniconda.sh
./miniconda.sh -b -p $HOME/miniconda
conda update --yes conda

# create named env
conda create -n testing python=$PYVERSION --yes

# install deps
conda install -n testing -c conda-forge --yes \
      ixmp \
      pytest \
      coveralls \
      pytest-cov 
conda remove -n testing --force --yes ixmp
