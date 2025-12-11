FDMS Minimal UI Project
======================
This is a minimal Django project skeleton that implements:
- Donor Dashboard
- Receiver Dashboard
- Simple admin-ready models
- Reports page (CSV export link)

How to run:
1. python -m venv env
2. .\env\Scripts\activate   (Windows PowerShell) or source env/bin/activate (mac/linux)
3. pip install -r requirements.txt
4. python manage.py migrate
5. python manage.py createsuperuser
6. python manage.py runserver
