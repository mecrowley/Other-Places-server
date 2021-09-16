#!/bin/bash

rm -rf otherplacesapi/migrations
rm db.sqlite3
python manage.py makemigrations otherplacesapi
python manage.py migrate