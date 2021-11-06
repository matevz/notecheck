# Generated by Django 3.2.6 on 2021-11-06 22:30

import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('notecheck', '0013_alter_exercise_title'),
    ]

    operations = [
        migrations.CreateModel(
            name='IntervalExercise',
            fields=[
                ('exercise_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='notecheck.exercise')),
                ('clef', models.CharField(choices=[('treble', 'Treble'), ('bass', 'Bass')], default='treble', max_length=10)),
                ('answer_type', models.CharField(choices=[('interval_quantity', 'Interval quantity (e.g. 4)'), ('interval_quantity_quality', 'Interval quantity and quality (e.g. p4)'), ('fulltones', 'Fulltones and remaining semitone (e.g. 2.5)'), ('semitones', 'Semitones (e.g. 5)')], default='interval_quantity_quality', max_length=50)),
                ('direction', models.SmallIntegerField(default=0, validators=[django.core.validators.MaxValueValidator(1), django.core.validators.MinValueValidator(-1)])),
                ('max_quantity', models.PositiveSmallIntegerField(default=8)),
                ('max_sharps', models.PositiveSmallIntegerField(default=0)),
                ('max_flats', models.PositiveSmallIntegerField(default=0)),
            ],
            bases=('notecheck.exercise',),
        ),
        migrations.CreateModel(
            name='IntervalSubmission',
            fields=[
            ],
            options={
                'proxy': True,
                'indexes': [],
                'constraints': [],
            },
            bases=('notecheck.submission',),
        ),
        migrations.CreateModel(
            name='NotePitchSubmission',
            fields=[
            ],
            options={
                'proxy': True,
                'indexes': [],
                'constraints': [],
            },
            bases=('notecheck.submission',),
        ),
    ]