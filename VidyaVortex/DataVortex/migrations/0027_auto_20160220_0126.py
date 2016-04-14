# -*- coding: utf-8 -*-
# Generated by Django 1.9 on 2016-02-19 23:26
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('DataVortex', '0026_auto_20160220_0117'),
    ]

    operations = [
        migrations.AlterField(
            model_name='game',
            name='description',
            field=models.TextField(blank=True, default='https://example.com/myimage.png'),
        ),
        migrations.AlterField(
            model_name='highscore',
            name='mygame',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='DataVortex.MyGame'),
        ),
    ]