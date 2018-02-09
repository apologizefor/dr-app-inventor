# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('appDrAI', '0015_datamodel_connect'),
    ]

    operations = [
        migrations.AddField(
            model_name='datamodel',
            name='draw',
            field=models.IntegerField(default=0),
            preserve_default=False,
        ),
    ]
