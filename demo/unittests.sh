#!/bin/bash
SOURCE="${BASH_SOURCE[0]}"
DIR="$( cd -P "$( dirname "$SOURCE" )" && pwd )"
python $DIR/manage.py test django_tml --settings=test_settings
