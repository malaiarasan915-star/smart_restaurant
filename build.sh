#!/usr/bin/env bash
# Render.com build script for Smart Restaurant Django app
set -o errexit

pip install -r requirements.txt
python manage.py collectstatic --no-input
python manage.py migrate
