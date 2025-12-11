
## Quick Start (after extracting)

1. Create virtualenv and activate.
2. Install requirements: `pip install -r requirements.txt` (or `pip install django` if not present).
3. Run migrations: `python manage.py migrate`
4. (Optional) Create superuser: `python manage.py createsuperuser`
5. Seed test users & donations: `python manage.py seed_fdms`
6. Run server: `python manage.py runserver`
7. Login as:
   - donor1 / Donor1Pass!
   - donor2 / Donor2Pass!
   - receiver1 / Receiver1Pass!
   - receiver2 / Receiver2Pass!
