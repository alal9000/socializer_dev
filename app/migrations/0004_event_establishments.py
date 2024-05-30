# Generated by Django 4.1.5 on 2024-02-25 22:23

from django.db import migrations
import multiselectfield.db.fields


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0003_event_title'),
    ]

    operations = [
        migrations.AddField(
            model_name='event',
            name='establishments',
            field=multiselectfield.db.fields.MultiSelectField(choices=[('Cafes', 'Cafes'), ('Restaurants', 'Restaurants'), ('Bars / Pubs', 'Bars / Pubs')], max_length=20, null=True),
        ),
    ]