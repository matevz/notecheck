# Generated by Django 3.2.6 on 2021-08-07 21:06

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('notecheck', '0005_alter_submission_duration'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='submission',
            name='assignment',
        ),
    ]