# Generated by Django 3.2.6 on 2021-11-24 08:58

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('notecheck', '0015_auto_20211114_1210'),
    ]

    operations = [
        migrations.CreateModel(
            name='ScaleExercise',
            fields=[
                ('exercise_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='notecheck.exercise')),
                ('clef', models.CharField(choices=[('treble', 'Treble'), ('bass', 'Bass')], default='treble', max_length=10)),
                ('scale_gender', models.CharField(choices=[('major', 'Major'), ('minor', 'Minor')], default='major', max_length=50)),
                ('scale_shape', models.CharField(choices=[('natural', 'Natural'), ('harmonic', 'Harmonic'), ('melodic', 'Melodic')], default='natural', max_length=50)),
                ('max_sharps', models.PositiveSmallIntegerField(default=7)),
                ('max_flats', models.PositiveSmallIntegerField(default=7)),
            ],
            bases=('notecheck.exercise',),
        ),
        migrations.CreateModel(
            name='ScaleSubmission',
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