# Generated by Django 4.1.5 on 2024-05-08 06:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0016_remove_profile_email_remove_profile_name_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='event',
            name='email',
        ),
        migrations.RemoveField(
            model_name='event',
            name='name',
        ),
        migrations.RemoveField(
            model_name='event',
            name='particular_eateries',
        ),
        migrations.RemoveField(
            model_name='event',
            name='phone',
        ),
        migrations.RemoveField(
            model_name='event',
            name='profile_pic',
        ),
        migrations.RemoveField(
            model_name='event',
            name='attendees',
        ),
        migrations.RemoveField(
            model_name='event',
            name='guests',
        ),
        migrations.AddField(
            model_name='event',
            name='attendees',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='event',
            name='guests',
            field=models.ManyToManyField(blank=True, related_name='attended_events', to='app.profile'),
        ),
    ]
