# -*- coding: utf-8 -*-
# Generated by Django 1.9.8 on 2016-10-07 01:46
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('izarnet', '0002_auto_20161004_2325'),
    ]

    operations = [
        migrations.AddField(
            model_name='izarnet',
            name='consumo_acumulado',
            field=models.FloatField(default=None),
        ),
    ]
