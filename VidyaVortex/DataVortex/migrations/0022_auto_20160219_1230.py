# -*- coding: utf-8 -*-
# Generated by Django 1.9 on 2016-02-19 10:30
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('DataVortex', '0021_auto_20160218_2324'),
    ]

    operations = [
        migrations.AddField(
            model_name='purchase',
            name='valid',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='highscore',
            name='mygame',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='DataVortex.MyGame'),
        ),
    ]
