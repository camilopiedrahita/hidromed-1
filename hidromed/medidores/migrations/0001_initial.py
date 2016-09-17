# -*- coding: utf-8 -*-
# Generated by Django 1.9.8 on 2016-09-17 02:55
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('empresas', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Medidor',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('serial', models.CharField(max_length=255)),
            ],
        ),
        migrations.CreateModel(
            name='Medidor_Acueducto',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('acueducto', models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.CASCADE, to='empresas.Acueducto')),
                ('medidor', models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.CASCADE, to='medidores.Medidor')),
            ],
            options={
                'verbose_name': 'Medidor vs Acueducto',
                'verbose_name_plural': 'Medidor vs Acueductos',
            },
        ),
        migrations.CreateModel(
            name='Medidor_Cliente',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('cliente', models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.CASCADE, to='empresas.Cliente')),
                ('medidor', models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.CASCADE, to='medidores.Medidor')),
            ],
            options={
                'verbose_name': 'Medidor vs Cliente',
                'verbose_name_plural': 'Medidor vs Clientes',
            },
        ),
    ]
