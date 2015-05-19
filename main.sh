#!/usr/bin/env bash

set -x

SUBJECT="OpenStack Unittest"
RECIPIENTS=(
    badi@iu.edu
    lee212@indiana.edu
)
RECIPIENTS=(badi@iu.edu)
DEV_EMAIL=badi@iu.edu

KEY='host_india contact_badi_AT_iu_edu'
VENV=venv


setup() {
    module load openstack
    source ~/.cloudmesh/clouds/india/juno/openrc.sh

    test -d $VENV || virtualenv $VENV
    source $VENV/bin/activate
    pip install -r requirements.txt
}


setup > SETUP.txt 2>&1
if ! test $? -eq 0; then
    mail -s "$SUBJECT Setup Failure" $DEV_EMAIL <SETUP.txt
    exit 1
fi

source $VENV/bin/activate
./novatest.py -k "$KEY" >OUTPUT.txt 2>&1

if ! test $? -eq 0; then
    subject="$SUBJECT FAIL"
else
    subject="$SUBJECT PASS"
fi
mail -s "$subject" ${RECIPIENTS[@]} <OUTPUT.txt
