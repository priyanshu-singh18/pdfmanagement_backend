#!/usr/bin/env bash
# exit on error
set -o errexit

poetry install
pip install --upgrade pippip install --force-reinstall -U setuptools

python manage.py migrate