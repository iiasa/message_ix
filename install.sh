#!/bin/bash

inst_args=$@


function error_msg() {
	echo =====================================================
	echo  There was an error during the install process!
	echo =====================================================
	read -p "Press any key to continue..."
	exit 1
}

# update ixmp submodule
git submodule sync
git submodule update --init
if [ "$?" -ne "0" ]; then
    error_msg
fi

# install ixmp
cd ./ixmp
python setup.py install $inst_args
if [ "$?" -ne "0" ]; then
    error_msg
fi
py.test tests

# install message_ix
cd ../
python setup.py install $inst_args
if [ "$?" -ne "0" ]; then
    error_msg
fi
py.test tests

# copy some gams files so users dont commit them
cp ./model/templates/MESSAGE_master_template.gms ./model/MESSAGE_master.gms
cp ./model/templates/MESSAGE_project_template.gpr ./model/MESSAGE_project.gpr

# make the documentation
cd ./doc
make html
cd ../

echo 
echo Installation complete
echo
read -p "Press any key to continue..."
echo
exit 0

