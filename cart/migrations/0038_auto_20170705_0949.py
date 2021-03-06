# -*- coding: utf-8 -*-
# Generated by Django 1.11.2 on 2017-07-05 09:49
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('cart', '0037_order_invoice_file'),
    ]

    operations = [
        migrations.AddField(
            model_name='confirmedbasket',
            name='applied_promotion',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='cart.Promotion'),
        ),
        migrations.AddField(
            model_name='confirmedbasket',
            name='promotion_cost',
            field=models.FloatField(null=True),
        ),
    ]
