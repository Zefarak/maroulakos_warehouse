# Generated by Django 3.0.1 on 2020-04-16 06:52

import datetime
from django.db import migrations, models
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('costumers', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='paymentinvoice',
            name='date',
            field=models.DateTimeField(default=datetime.datetime(2020, 4, 16, 6, 52, 6, 435404, tzinfo=utc), verbose_name='Ημερομηνία'),
        ),
    ]
