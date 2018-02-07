# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('appDrAI', '0010_auto_20180206_2332'),
    ]

    operations = [
        migrations.AddField(
            model_name='datamodel',
            name='data_pers',
            field=models.IntegerField(default=0),
            preserve_default=False,
        ),
    ]
