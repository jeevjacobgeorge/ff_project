# Generated by Django 5.1.4 on 2025-03-06 10:04

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='KsrtcFromData',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date_hour', models.CharField(max_length=50)),
                ('from_stop_name', models.CharField(max_length=100)),
                ('total_passenger', models.IntegerField()),
            ],
        ),
        migrations.CreateModel(
            name='KsrtcToData',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date_hour', models.CharField(max_length=50)),
                ('to_stop_name', models.CharField(max_length=100)),
                ('total_passenger', models.IntegerField()),
            ],
        ),
    ]
