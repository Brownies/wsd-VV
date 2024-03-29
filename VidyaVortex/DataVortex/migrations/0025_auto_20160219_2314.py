# -*- coding: utf-8 -*-
# Generated by Django 1.9.2 on 2016-02-19 21:14
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('DataVortex', '0024_auto_20160219_1808'),
    ]

    operations = [
        migrations.AlterField(
            model_name='highscore',
            name='mygame',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='DataVortex.MyGame'),
        ),
        migrations.AlterField(
            model_name='verification',
            name='apikey',
            field=models.CharField(max_length=32, unique=True),
        ),
    ]
