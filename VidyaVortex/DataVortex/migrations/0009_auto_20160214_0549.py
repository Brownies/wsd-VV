# -*- coding: utf-8 -*-
# Generated by Django 1.9 on 2016-02-14 03:49
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('DataVortex', '0008_auto_20160214_0041'),
    ]

    operations = [
        migrations.AlterField(
            model_name='game',
            name='id',
            field=models.PositiveIntegerField(primary_key=True, serialize=False),
        ),
    ]