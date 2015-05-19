#!/bin/bash -l

set -x

SUBJECT="OpenStack Unittest"
RECIPIENTS=(
    badi@iu.edu
    lee212@indiana.edu
)
DEV_EMAIL=badi@iu.edu

KEY=india-key
VENV=venv

setup() {
    test -d $VENV || virtualenv $VENV
    source $VENV/bin/activate
    pip install -r requirements.txt
}

notify-dev() {
    local description="$1"
    local contents_file="$2"
    mail -s "$SUBJECT $description" $DEV_EMAIL <$contents_file
}

cleanup() {
    test -d $VENV && rm -vr $VENV
}

trap "notify-dev 'CRON Failure' cron.log" EXIT
set -e
module load python
which pip
which virtualenv
module load openstack
source ~/.cloudmesh/clouds/india/juno/openrc.sh
set +e

trap cleanup EXIT

setup > SETUP.txt 2>&1
if ! test $? -eq 0; then
    mail -s "$SUBJECT Setup Failure" $DEV_EMAIL <SETUP.txt
    exit 1
fi

source $VENV/bin/activate
time ./novatest.py -k "$KEY" >OUTPUT.txt 2>&1

if ! test $? -eq 0; then
    status="FAIL"
    mail -s "$SUBJECT $status" ${RECIPIENTS[@]} <OUTPUT.txt
else
    status="PASS"
fi

