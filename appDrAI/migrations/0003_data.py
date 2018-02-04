# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('appDrAI', '0002_aiafile'),
    ]

    operations = [
        migrations.CreateModel(
            name='Data',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('screens', models.IntegerField()),
                ('naming', models.FloatField()),
                ('cond_if', models.IntegerField()),
                ('cond_else', models.IntegerField()),
                ('cond_elseif', models.IntegerField()),
                ('events', models.IntegerField()),
                ('loop_while', models.IntegerField()),
                ('loop_range', models.IntegerField()),
                ('loop_list', models.IntegerField()),
            ],
        ),
    ]
