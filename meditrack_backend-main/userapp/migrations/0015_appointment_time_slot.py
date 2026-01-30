# Generated migration for adding time_slot field to Appointment model

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('userapp', '0014_complaint_complaintimage'),
    ]

    operations = [
        migrations.AddField(
            model_name='appointment',
            name='time_slot',
            field=models.CharField(
                choices=[('morning', 'Morning (06:00 - 14:00)'), ('evening', 'Evening (14:00 - 22:00)')],
                default='morning',
                max_length=10
            ),
        ),
    ]
