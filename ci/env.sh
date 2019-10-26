# Set environment variables for Linux/macOS CI on Travis

export CACHE=$HOME/.cache/message_ix

# gams info
case "${TRAVIS_OS_NAME}" in
  linux)
    OSFIX=linux
    GAMSPATH=linux_x64_64_sfx
  ;;
  osx)
    OSFIX=macosx
    GAMSPATH=osx_x64_64_sfx
  ;;
  windows)
    OSFIX=windows
    GAMSPATH=windows_x64_64
  ;;
esac

GAMS_VERSION_SHORT=25.1
GAMS_VERSION_LONG=25.1.1

export GAMSFNAME=$GAMSPATH.exe
export GAMSURL=https://d37drm4t2jghv5.cloudfront.net/distributions/$GAMS_VERSION_LONG/$OSFIX/$GAMSFNAME
export PATH=$PATH:$PWD/gams"$GAMS_VERSION_SHORT"_"$GAMSPATH"

# miniconda info
case "${TRAVIS_OS_NAME}" in
  linux)
    OSNAME=Linux
    EXT=sh
  ;;
  osx)
    OSNAME=MacOSX
    EXT=sh
  ;;
  windows)
    OSNAME=Windows
    EXT=exe
  ;;
esac

case "${PYENV}" in
  py37)
    export PYVERSION=3
  ;;
esac

export CONDAFNAME=Miniconda$PYVERSION-latest-$OSNAME-x86_64.$EXT
export CONDAURL=https://repo.anaconda.com/miniconda/$CONDAFNAME
export PATH=$HOME/miniconda/bin:$PATH

# Echo all environment variables for debugging
env | sort
