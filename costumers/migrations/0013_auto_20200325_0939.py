# Generated by Django 2.2 on 2020-03-25 07:39

import datetime
from django.db import migrations, models
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('costumers', '0012_auto_20200323_1336'),
    ]

    operations = [
        migrations.AlterField(
            model_name='paymentinvoice',
            name='date',
            field=models.DateTimeField(default=datetime.datetime(2020, 3, 25, 7, 39, 44, 855001, tzinfo=utc), verbose_name='Ημερομηνία'),
        ),
    ]