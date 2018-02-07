# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('appDrAI', '0009_auto_20180206_2106'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='datamodel',
            name='loop_list',
        ),
        migrations.RemoveField(
            model_name='datamodel',
            name='loop_range',
        ),
        migrations.RemoveField(
            model_name='datamodel',
            name='loop_while',
        ),
        migrations.AddField(
            model_name='datamodel',
            name='loop',
            field=models.IntegerField(default=0),
            preserve_default=False,
        ),
    ]
