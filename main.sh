#!/usr/bin/env bash

set -x

SUBJECT="OpenStack Unittest"
RECIPIENTS=(
    badi@iu.edu
    lee212@indiana.edu
)
DEV_EMAIL=badi@iu.edu

KEY=india-key
VENV=venv


module load python
which pip
which virtualenv
module load openstack
source ~/.cloudmesh/clouds/india/juno/openrc.sh


setup() {
    test -d $VENV || virtualenv $VENV
    source $VENV/bin/activate
    pip install -r requirements.txt
}

cleanup() {
    test -d $VENV && rm -vr $VENV
}

trap cleanup EXIT

setup > SETUP.txt 2>&1
if ! test $? -eq 0; then
    mail -s "$SUBJECT Setup Failure" $DEV_EMAIL <SETUP.txt
    exit 1
fi

source $VENV/bin/activate
./novatest.py -k "$KEY" >OUTPUT.txt 2>&1

if ! test $? -eq 0; then
    subject="$SUBJECT FAIL"
    mail -s "$subject" ${RECIPIENTS[@]} <OUTPUT.txt
fi

