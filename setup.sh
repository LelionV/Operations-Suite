#!/bin/bash
set -e
echo "=== Integrated Operations Suite Setup ==="
python3 -m venv virtual
source virtual/bin/activate
pip install -r requirements/base.txt
python manage.py makemigrations accounts departments inventory purchase_orders procurement stores stock assets notify tickets visitors notifications settings_manager compliance policies risks equipment inspections maintenance ppe training audits incidents nonconformities actions licenses contractors environmental chemicals emergency evidence dashboard
python manage.py migrate
python manage.py bootstrap_demo
python manage.py createsuperuser
echo ""
echo "Done!  source virtual/bin/activate && python manage.py runserver"
echo "Login: http://127.0.0.1:8000/"
