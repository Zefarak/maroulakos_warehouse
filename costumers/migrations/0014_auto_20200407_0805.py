# Generated by Django 3.0.4 on 2020-04-07 05:05

import datetime
from django.db import migrations, models
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('costumers', '0013_auto_20200406_1936'),
    ]

    operations = [
        migrations.AlterField(
            model_name='paymentinvoice',
            name='date',
            field=models.DateTimeField(default=datetime.datetime(2020, 4, 7, 5, 5, 1, 420987, tzinfo=utc), verbose_name='Ημερομηνία'),
        ),
    ]
