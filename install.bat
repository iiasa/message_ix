
cd > .foo
set /p MESSAGE_IX=<.foo
del .foo
echo %MESSAGE_IX%

echo Python MESSAGE_IX setup
python setup.py install
messageix-config --model_path message_ix\\model

echo R MESSAGE_IX setup
where /q r
IF ERRORLEVEL 1 (
    ECHO No valid installation of R found, skipped build and installation of rixmp package.
    @rem set ERRORLEVEL to 0 -> ignore R setup
    VERIFY
) ELSE (
    rscript rmessageix/build_rmessageix.R [--verbose]
)

if %errorlevel% neq 0 GOTO InstallError

setx IXMP_PATH "%MESSAGE_IX%"

copy message_ix\\model\\templates\\MESSAGE_master_template.gms message_ix\\model\\MESSAGE_master.gms
copy message_ix\\model\\templates\\MESSAGE_project_template.gpr message_ix\\model\\MESSAGE_project.gpr

py.test tests

pause
exit

@rem install error
:InstallError
echo ==========================================================
echo  There was an error during the installation of MESSAGEix!
echo ==========================================================
pause
exit
