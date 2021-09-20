#!/bin/bash

rm -rf otherplacesapi/migrations
rm db.sqlite3
python manage.py makemigrations otherplacesapi
python manage.py migrate
python manage.py loaddata users
python manage.py loaddata tokens
python manage.py loaddata opusers
python manage.py loaddata places
python manage.py loaddata visitedplaces