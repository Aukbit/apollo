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
flask initdb
exit