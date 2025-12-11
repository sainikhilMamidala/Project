from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.utils import timezone
from core.models import Donation

User = get_user_model()

class Command(BaseCommand):
    help = "Seed DB with 2 donors, 2 receivers, groups and sample donations."

    def handle(self, *args, **options):
        # Create groups
        donor_group, _ = Group.objects.get_or_create(name='Donor')
        receiver_group, _ = Group.objects.get_or_create(name='Receiver')

        def create_user(username, password, first_name="", is_staff=False):
            user, created = User.objects.get_or_create(username=username)
            if created or not user.has_usable_password():
                user.set_password(password)
                user.first_name = first_name
                user.is_staff = is_staff
                user.save()
                self.stdout.write(self.style.SUCCESS(f"Created/updated user {username}"))
            else:
                self.stdout.write(self.style.NOTICE(f"User {username} already exists"))
            return user

        # Create donors
        donor1 = create_user('donor1', 'Donor1Pass!', 'Donor1')
        donor2 = create_user('donor2', 'Donor2Pass!', 'Donor2')
        donor1.groups.add(donor_group)
        donor2.groups.add(donor_group)

        # Create receivers
        recv1 = create_user('receiver1', 'Receiver1Pass!', 'Receiver1')
        recv2 = create_user('receiver2', 'Receiver2Pass!', 'Receiver2')
        recv1.groups.add(receiver_group)
        recv2.groups.add(receiver_group)

        # Create sample donations if not exist
        now = timezone.now()
        if not Donation.objects.filter(title__icontains='Cooked Meal - 5').exists():
            d1 = Donation.objects.create(
                title='Cooked Meal - 5 plates',
                donor=donor1,
                address='123 Donor St',
                quantity=5,
                donation_type='cooked',
            )
            self.stdout.write(self.style.SUCCESS(f"Created donation: {d1}"))
        else:
            self.stdout.write("Cooked sample donation already exists")

        if not Donation.objects.filter(title__icontains='Frozen Packets - 10').exists():
            d2 = Donation.objects.create(
                title='Frozen Packets - 10',
                donor=donor2,
                address='456 Donor Ave',
                quantity=10,
                donation_type='frozen',
            )
            self.stdout.write(self.style.SUCCESS(f"Created donation: {d2}"))
        else:
            self.stdout.write("Frozen sample donation already exists")

        self.stdout.write(self.style.SUCCESS("Seed complete."))
        self.stdout.write('Donors: donor1 / Donor1Pass!, donor2 / Donor2Pass!')
        self.stdout.write('Receivers: receiver1 / Receiver1Pass!, receiver2 / Receiver2Pass!')

        