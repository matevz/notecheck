# Generated by Django 3.2.6 on 2021-08-08 09:56

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('notecheck', '0006_remove_submission_assignment'),
    ]

    operations = [
        migrations.RenameField(
            model_name='submission',
            old_name='submission',
            new_name='answers',
        ),
    ]