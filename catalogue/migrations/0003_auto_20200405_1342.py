# Generated by Django 3.0.1 on 2020-04-05 10:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('catalogue', '0002_auto_20200330_2053'),
    ]

    operations = [
        migrations.AlterField(
            model_name='productingredient',
            name='cost',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=17, verbose_name='Κοστος'),
        ),
    ]