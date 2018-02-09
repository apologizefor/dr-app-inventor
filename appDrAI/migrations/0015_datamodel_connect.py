# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('appDrAI', '0014_datamodel_social'),
    ]

    operations = [
        migrations.AddField(
            model_name='datamodel',
            name='connect',
            field=models.IntegerField(default=0),
            preserve_default=False,
        ),
    ]
