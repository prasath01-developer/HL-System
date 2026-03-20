from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('outpass', '0003_outpass_hostel_status'),
    ]

    operations = [
        migrations.AddField(
            model_name='student',
            name='status',
            field=models.CharField(
                choices=[('inside', 'Inside Hostel'), ('outside', 'Outside Hostel')],
                db_index=True,
                default='inside',
                max_length=20,
            ),
        ),
    ]
