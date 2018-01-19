
cd > .foo
set /p MESSAGE_IX=<.foo
del .foo
echo %MESSAGE_IX%

python setup.py install

if %errorlevel% neq 0 exit GOTO InstallError

setx MESSAGE_IX_PATH "%MESSAGE_IX%"

copy model\\templates\\MESSAGE_master_template.gms model\\MESSAGE_master.gms
copy model\\templates\\message_project_template.gpr model\\message_project.gpr

chdir doc/
call make.bat html
chdir ../

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
