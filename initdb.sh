#!/bin/bash
echo "------ Create database tables ------"
python manage.py migrate --noinput
python manage.py load_data
waitress-serve --port=$VCAP_APP_PORT hourglass.wsgi:application
