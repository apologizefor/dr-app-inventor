# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('appDrAI', '0006_auto_20180202_1716'),
    ]

    operations = [
        migrations.CreateModel(
            name='UserModel',
            fields=[
                ('id_number', models.AutoField(serialize=False, primary_key=True)),
                ('ainame', models.CharField(max_length=20)),
                ('user', models.OneToOneField(to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AlterField(
            model_name='datamodel',
            name='id_number',
            field=models.AutoField(serialize=False, primary_key=True),
        ),
        migrations.AddField(
            model_name='datamodel',
            name='author',
            field=models.ForeignKey(blank=True, to='appDrAI.UserModel', null=True),
        ),
    ]
