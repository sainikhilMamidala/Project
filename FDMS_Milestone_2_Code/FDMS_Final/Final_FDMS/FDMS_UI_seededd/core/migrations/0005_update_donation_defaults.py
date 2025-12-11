from django.db import migrations, models

class Migration(migrations.Migration):

    dependencies = [
        ('core', '0004_alter_donation_options_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='donation',
            name='quantity',
            field=models.IntegerField(default=1),
        ),
        migrations.AlterField(
            model_name='donation',
            name='status',
            field=models.CharField(
                max_length=20,
                choices=[
                    ('available', 'available'),
                    ('claimed', 'claimed'),
                    ('picked_up', 'picked_up'),
                    ('rejected', 'rejected'),
                ],
                default='available'
            ),
        ),
        migrations.AlterField(
            model_name='donation',
            name='initial_quantity',
            field=models.IntegerField(default=1),
        ),
        migrations.AlterField(
            model_name='donation',
            name='available_quantity',
            field=models.IntegerField(default=1),
        ),
    ]
