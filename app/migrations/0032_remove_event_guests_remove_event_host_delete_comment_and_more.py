# Generated by Django 4.1.5 on 2024-05-30 22:53

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0031_delete_message'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='event',
            name='guests',
        ),
        migrations.RemoveField(
            model_name='event',
            name='host',
        ),
        migrations.DeleteModel(
            name='Comment',
        ),
        migrations.DeleteModel(
            name='Event',
        ),
    ]
