# Generated by Django 3.2.6 on 2021-08-06 20:50

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Exercise',
            fields=[
                ('token', models.CharField(max_length=32, primary_key=True, serialize=False)),
                ('created', models.DateTimeField(verbose_name='date published')),
                ('exercise', models.JSONField()),
            ],
        ),
        migrations.CreateModel(
            name='Submission',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('seed', models.IntegerField(default=0)),
                ('submission', models.JSONField()),
                ('created', models.DateTimeField(verbose_name='submission date')),
                ('duration', models.DurationField()),
                ('token', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='notecheck.exercise')),
            ],
        ),
    ]
