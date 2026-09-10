@echo off
echo === Integrated Operations Suite Setup ===
python -m venv virtual
call virtual\Scripts\activate.bat
pip install -r requirements\base.txt
python manage.py makemigrations accounts departments inventory purchase_orders procurement stores stock assets notify tickets visitors notifications settings_manager compliance policies risks equipment inspections maintenance ppe training audits incidents nonconformities actions licenses contractors environmental chemicals emergency evidence dashboard
python manage.py migrate
python manage.py bootstrap_demo
python manage.py createsuperuser
echo Done! Run: virtual\Scripts\activate ^&^& python manage.py runserver
