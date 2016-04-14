# -*- coding: utf-8 -*-
# Generated by Django 1.9.2 on 2016-02-19 13:17
from __future__ import unicode_literals

import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('DataVortex', '0022_auto_20160219_1230'),
    ]

    operations = [
        migrations.AlterField(
            model_name='game',
            name='url',
            field=models.URLField(default='https://example.com/game.html', unique=True, validators=[django.core.validators.URLValidator(message='Please provide a valid https URL', schemes=['https'])]),
        ),
        migrations.AlterField(
            model_name='highscore',
            name='mygame',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='DataVortex.MyGame'),
        ),
    ]