# -*- coding: utf-8 -*-
# Generated by Django 1.11.2 on 2017-06-09 10:45
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('archive', '0007_auto_20170609_1044'),
    ]

    operations = [
        migrations.AlterField(
            model_name='strain',
            name='purchasers',
            field=models.ManyToManyField(related_name='purchases', to=settings.AUTH_USER_MODEL),
        ),
    ]
