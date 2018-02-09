# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('appDrAI', '0017_datamodel_operator'),
    ]

    operations = [
        migrations.AddField(
            model_name='datamodel',
            name='ui',
            field=models.IntegerField(default=0),
            preserve_default=False,
        ),
    ]
