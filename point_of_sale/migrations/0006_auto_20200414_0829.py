# Generated by Django 3.0.1 on 2020-04-14 05:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('point_of_sale', '0005_auto_20200412_1450'),
    ]

    operations = [
        migrations.AlterField(
            model_name='salesinvoiceitem',
            name='expiration_date',
            field=models.DateField(blank=True, null=True, verbose_name='Ημερομηνια λήξης'),
        ),
    ]