# Pre-installation script for Linux/macOS CI on Travis

# Download files into the cache directory
maybe_download () {
  if [ ! -x $CACHE/$2 ]; then
    curl $1 --output $CACHE/$2 --remote-time --time-cond $CACHE/$2
  else
    curl $1 --output $CACHE/$2 --remote-time
  fi
  chmod +x $CACHE/$2
}

maybe_download $GAMSURL $GAMSFNAME
maybe_download $CONDAURL $CONDAFNAME

# # Install graphiz on OS X
# if [ `uname` = "Darwin" ];
# then
#   # NB 'brew update' is triggered in .travis.yml
#
#   brew config
#
#   # Install graphviz' dependencies, but avoid installing 'python', which fails
#   # and causes the build to error. See
#   # https://github.com/iiasa/message_ix/pull/295.
#   brew install gd
#   brew upgrade glib  # depends on python
#   brew install netpbm
#   brew install --ignore-dependencies gts # depends on glib
#
#   brew install --ignore-dependencies graphviz
# fi
