# Generated by Django 3.2.6 on 2021-09-10 07:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('notecheck', '0008_exercise_title'),
    ]

    operations = [
        migrations.AlterField(
            model_name='submission',
            name='created',
            field=models.DateTimeField(auto_now=True, verbose_name='submission created date'),
        ),
    ]
