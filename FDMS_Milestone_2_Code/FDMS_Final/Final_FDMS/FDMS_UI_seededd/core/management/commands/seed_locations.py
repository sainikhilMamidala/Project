
from django.core.management.base import BaseCommand
from core.models import Location

class Command(BaseCommand):
    help = 'Seed initial locations for FDMS'

    def handle(self, *args, **options):
        names = ['Texas', 'Chicago', 'Milwaukee']
        for n in names:
            Location.objects.get_or_create(name=n)
        self.stdout.write(self.style.SUCCESS('Seeded locations: ' + ', '.join(names)))
