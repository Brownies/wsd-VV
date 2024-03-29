# -*- coding: utf-8 -*-
# Generated by Django 1.9 on 2016-02-18 21:24
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('DataVortex', '0020_auto_20160218_2113'),
    ]

    operations = [
        migrations.AddField(
            model_name='purchase',
            name='amount',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=7),
        ),
        migrations.AlterField(
            model_name='highscore',
            name='mygame',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='DataVortex.MyGame'),
        ),
    ]
