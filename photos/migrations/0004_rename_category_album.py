# Generated by Django 4.1.5 on 2024-06-02 07:02

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("photos", "0003_photo_timestamp"),
    ]

    operations = [
        migrations.RenameModel(
            old_name="Category",
            new_name="Album",
        ),
    ]
