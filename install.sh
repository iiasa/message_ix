#!/bin/bash

cd ./ixmp
python setup.py install --user
if [ "$?" -ne "0" ]; then
	echo =====================================================
	echo  There was an error during the install process!
	echo =====================================================
	read -p "Press any key to continue..."
	exit 1
fi
cd ../
python setup.py install --user
if [ "$?" -ne "0" ]; then
	echo =====================================================
	echo  There was an error during the install process!
	echo =====================================================
	read -p "Press any key to continue..."
	exit 1
fi

cp ./model/templates/MESSAGE_master_template.gms ./model/MESSAGE_master.gms
cp ./model/templates/MESSAGE_project_template.gpr ./model/MESSAGE_project.gpr

cd ./doc
make html
cd ../

py.test ./ixmp/tests
py.test tests


echo 
echo Please add the MESSAGE_ix directory to your environmental variables by writing:
echo "	export MESSAGE_IX_PATH=$PWD"
echo in the command line and in ~/.bashrc
echo
read -p "Press any key to continue..."
echo
exit 0

