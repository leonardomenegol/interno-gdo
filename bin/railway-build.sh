#!/usr/bin/env bash
set -o errexit

echo "-----> Installing Python dependencies"
python -m pip install pipenv
pipenv install --system

echo "-----> Running database migration"
cd ./tabbycat/
python manage.py migrate --noinput

echo "-----> Running dynamic preferences checks"
python manage.py checkpreferences

echo "-----> Installing Node dependencies and building assets"
cd ..
npm install
npm run build

echo "-----> Collecting static files"
cd ./tabbycat/
python manage.py collectstatic --noinput

echo "-----> Build done"
