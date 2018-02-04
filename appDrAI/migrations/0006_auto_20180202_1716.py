# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('appDrAI', '0005_auto_20180202_1652'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='datamodel',
            name='id',
        ),
        migrations.AddField(
            model_name='datamodel',
            name='id_number',
            field=models.IntegerField(default=0, serialize=False, primary_key=True),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='datamodel',
            name='lists',
            field=models.IntegerField(default=1),
            preserve_default=False,
        ),
    ]
