# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('appDrAI', '0008_auto_20180206_2053'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='datamodel',
            name='cond_else',
        ),
        migrations.RemoveField(
            model_name='datamodel',
            name='cond_elseif',
        ),
        migrations.RemoveField(
            model_name='datamodel',
            name='cond_if',
        ),
        migrations.AddField(
            model_name='datamodel',
            name='cond',
            field=models.IntegerField(default=0),
            preserve_default=False,
        ),
    ]
