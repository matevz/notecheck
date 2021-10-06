# Generated by Django 3.2.6 on 2021-10-06 07:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('notecheck', '0010_auto_20211006_0708'),
    ]

    operations = [
        migrations.AlterField(
            model_name='notepitchexercise',
            name='max_flats',
            field=models.PositiveSmallIntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='notepitchexercise',
            name='max_sharps',
            field=models.PositiveSmallIntegerField(default=0),
        ),
    ]