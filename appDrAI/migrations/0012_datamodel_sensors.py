# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('appDrAI', '0011_datamodel_data_pers'),
    ]

    operations = [
        migrations.AddField(
            model_name='datamodel',
            name='sensors',
            field=models.IntegerField(default=0),
            preserve_default=False,
        ),
    ]
