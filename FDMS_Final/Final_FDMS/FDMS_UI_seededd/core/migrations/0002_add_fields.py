
# Generated migration: add Location and new quantity fields (manual)
from django.db import migrations, models
import django.db.models.deletion

class Migration(migrations.Migration):

    dependencies = [
        ('core', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Location',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=128, unique=True)),
            ],
        ),
        migrations.AddField(
            model_name='donation',
            name='initial_quantity',
            field=models.IntegerField(default=1),
        ),
        migrations.AddField(
            model_name='donation',
            name='available_quantity',
            field=models.IntegerField(default=1),
        ),
        migrations.AddField(
            model_name='donation',
            name='location',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='donations', to='core.Location'),
        ),
        migrations.AddIndex(
            model_name='donation',
            index=models.Index(fields=['location'], name='core_donation_location_idx'),
        ),
    ]
