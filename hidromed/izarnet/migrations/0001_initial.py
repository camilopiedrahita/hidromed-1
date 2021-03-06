# -*- coding: utf-8 -*-
# Generated by Django 1.9.8 on 2016-09-20 04:05
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('medidores', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Izarnetv1',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('fecha', models.DateTimeField()),
                ('volumen', models.FloatField(default=None)),
                ('consumo', models.FloatField(default=None)),
                ('volumen_litros', models.FloatField(default=None)),
                ('caudal', models.FloatField(default=None, verbose_name='Caudal Promedio')),
                ('alarma', models.CharField(max_length=255)),
                ('medidor', models.ForeignKey(default=None, on_delete=django.db.models.deletion.CASCADE, to='medidores.Medidor')),
            ],
        ),
        migrations.CreateModel(
            name='Izarnetv1Procesados',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(max_length=255)),
                ('fecha', models.DateTimeField()),
                ('estado', models.CharField(max_length=255)),
            ],
        ),
    ]
