# -*- coding: utf-8 -*-
# Generated by Django 1.9.8 on 2016-10-23 17:40
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('izarnet', '0003_izarnet_consumo_acumulado'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='izarnet',
            name='caudal',
        ),
        migrations.RemoveField(
            model_name='izarnet',
            name='consumo_acumulado',
        ),
    ]