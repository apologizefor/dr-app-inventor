# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('appDrAI', '0003_data'),
    ]

    operations = [
        migrations.CreateModel(
            name='DataModel',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=200)),
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
        migrations.DeleteModel(
            name='Data',
        ),
    ]
