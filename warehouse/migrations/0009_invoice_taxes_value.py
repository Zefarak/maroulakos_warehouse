# Generated by Django 2.2 on 2020-03-26 18:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('warehouse', '0008_auto_20200316_2044'),
    ]

    operations = [
        migrations.AddField(
            model_name='invoice',
            name='taxes_value',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=20, verbose_name='Φορος'),
        ),
    ]
