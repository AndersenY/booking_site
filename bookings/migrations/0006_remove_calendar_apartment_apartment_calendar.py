# Generated by Django 4.2.2 on 2024-10-19 17:52

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('bookings', '0005_remove_apartment_max_guests_apartment_image_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='calendar',
            name='apartment',
        ),
        migrations.AddField(
            model_name='apartment',
            name='calendar',
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='bookings.calendar'),
        ),
    ]
