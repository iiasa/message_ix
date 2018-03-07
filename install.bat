
cd > .foo
set /p MESSAGE_IX=<.foo
del .foo
echo %MESSAGE_IX%

echo Python MESSAGE_IX setup
chdir ixmp
python setup.py install
chdir ../
python setup.py install

echo R MESSAGE_IX setup
where /q r
IF ERRORLEVEL 1 (
    ECHO No valid installation of R found, skipped build and installation of rixmp package.
    @rem set ERRORLEVEL to 0 -> ignore R setup
    VERIFY
) ELSE (
    chdir ixmp
    rscript rixmp/build_rixmp.R [--verbose]
    chdir ../
    rscript rmessageix/build_rmessageix.R [--verbose]
)

if %errorlevel% neq 0 GOTO InstallError

setx IXMP_PATH "%MESSAGE_IX%"

copy model\\templates\\MESSAGE_master_template.gms model\\MESSAGE_master.gms
copy model\\templates\\MESSAGE_project_template.gpr model\\MESSAGE_project.gpr

chdir doc/
call make.bat html
chdir ../

py.test ixmp\\tests
py.test tests

pause
exit

@rem install error
:InstallError
echo =====================================================
echo  There was an error during the install process!
echo =====================================================
pause
exit
