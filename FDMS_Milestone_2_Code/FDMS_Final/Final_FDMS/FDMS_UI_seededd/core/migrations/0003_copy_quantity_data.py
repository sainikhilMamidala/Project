
from django.db import migrations

def copy_quantity(apps, schema_editor):
    Donation = apps.get_model('core', 'Donation')
    for d in Donation.objects.all():
        try:
            q = getattr(d, 'quantity', None)
            if q is None:
                continue
            d.initial_quantity = q
            d.available_quantity = q
            d.save(update_fields=['initial_quantity','available_quantity'])
        except Exception:
            pass

class Migration(migrations.Migration):
    dependencies = [
        ('core', '0002_add_fields'),
    ]

    operations = [
        migrations.RunPython(copy_quantity, reverse_code=migrations.RunPython.noop),
    ]
