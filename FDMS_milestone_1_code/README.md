
FDMS - Food Donation Management System (minimal Django project)

Setup (Windows PowerShell):

1. Create and activate virtual environment:
   python -m venv venv
   venv\Scripts\Activate.ps1
2. Install requirements:
   pip install -r requirements.txt
3. Run migrations:
   python manage.py migrate
4. Create superuser (optional):
   python manage.py createsuperuser
5. Run server:
   python manage.py runserver
6. Open http://127.0.0.1:8000
