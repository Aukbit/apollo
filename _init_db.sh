#!/usr/bin/env bash
# https://linuxconfig.org/bash-scripting-tutorial
# note: make file executable by running
# `chmod +x hello_world.sh`
# now you can execute it like
# `./hello_world.sh`
#
echo -e "\nYou are about to sync this project with your local DB."
# Activate virtual environment
source ~/.virtualenv/apollo/bin/activate
export FLASK_APP=./main.py
#
echo -e "\nDefine <SETTINGS_PATH> default <../settings.cfg>: \c"
read  path
if [ ! $path = '' ]
then
    export SETTINGS_PATH=$path
else
    export SETTINGS_PATH='../settings.cfg'
fi
#
flask initdb
exit