# Installation script for Windows CI on Appveyor
#
# This script mirrors travis-before_install.sh and travis-install.sh. The
# 'Progress', 'Bootstrap', and 'Exec' "cmdlets" are from the R Appveyor tool
# krlmlr/r-appveyor.
#
# 'Exec' is used because (in some cases, unpredictably) commands given directly
# in this file (a) do not produce any output in the Appveyor build log, and/or
# (b) cause the build to stop, even though the command completes successfully.
# 'Exec' resolves both of these issues.


# Halt instead of stalling on failure
$ErrorActionPreference = 'Stop'

# For debugging, use -Trace 1 or -Trace 2.
Set-PSDebug -Trace 0

Progress 'Download GAMS'
$GAMSInstaller = '..\windows_x64_64.exe'
Start-FileDownload 'https://d37drm4t2jghv5.cloudfront.net/distributions/25.1.1/windows/windows_x64_64.exe' -FileName $GAMSInstaller

Progress 'Install GAMS'
$GAMSPath = 'C:\GAMS'
$GAMSArgs = '/SP- /SILENT /DIR=' + $GAMSPath + ' /NORESTART'
Start-Process $GAMSInstaller $GAMSArgs -Wait

# Add to PATH
$env:PATH = $GAMSPath + ';' + $env:PATH

# Show information
# NB this doesn't generate any output in the Appveyor log, and it's unclear
#    why; possibly because GAMS uses non-standard output conventions (e.g. to
#    stderr).
Exec { gams }


Progress 'Set conda version/path'
# These correspond to folder naming of miniconda installs on appveyor
# See https://www.appveyor.com/docs/windows-images-software/#miniconda
if ( $env:PYTHON_VERSION -eq '2.7' ) {
  $MC_PYTHON_VERSION = ''
} else {
  $MC_PYTHON_VERSION = $env:PYTHON_VERSION.Replace('.', '')
}
if ( $env:PYTHON_ARCH -eq '64' ) { $ARCH_LABEL = '-x64' }


# Conda root path
$CR = 'C:\Miniconda' + $MC_PYTHON_VERSION + $ARCH_LABEL
$env:CONDA_ROOT = $CR

# Path for executables, e.g. pip, jupyter
$env:PATH = $CR + ';' + $CR + '\Scripts;' + $CR + '\Library\bin;' + $env:PATH

# Explicit path to Python executable, for reticulate 1.13. This workaround is
# suggested at rstudio/reticulate#571 to address errors that occurred during
# devtools::install() in appveyor-install.R
# TODO test and possibly remove once reticulate 1.14 is released
$env:RETICULATE_PYTHON = $CR + '\python.exe'

Progress 'Update conda'
# The installed conda on Appveyor workers is 4.5.x, while the latest is >4.7.
# --quiet here and below suppresses progress bars, which show up as many lines
# in the Appveyor build logs.
Exec { conda update --yes --quiet conda pip }

# Search conda-forge in addition to the default channels, for e.g. JPype
Exec { conda config --append channels conda-forge }

# NB at the corresponding location, travis-install.sh creates a new conda
#    environment, and later activates it. This was attempted for Windows/
#    Appveyor in iiasa/ixmp#192, but for unclear reasons the 'activate testing'
#    step could not be made to work. On Windows/Appveyor, message_ix and its
#    dependencies are installed into the base conda environment.

Progress 'Install dependencies'
Exec { conda install --yes --file ci/conda-requirements.txt }
Exec { pip install --requirement ci/pip-requirements.txt }

# Temporary: see https://github.com/IAMconsortium/pyam/issues/281
Exec { pip install "matplotlib>3.0.2" }

Progress 'Conda information'
conda info --all
