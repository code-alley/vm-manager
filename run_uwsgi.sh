#!/bin/bash

SCRIPT_DIR=$(dirname "$0")

cd $SCRIPT_DIR
source env/bin/activate
uwsgi uwsgi_prod.ini
