# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('appDrAI', '0007_auto_20180204_2117'),
    ]

    operations = [
        migrations.AlterField(
            model_name='datamodel',
            name='naming',
            field=models.IntegerField(),
        ),
    ]
