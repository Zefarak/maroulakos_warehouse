# Generated by Django 3.0.1 on 2021-01-25 05:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('catalogue', '0003_auto_20210123_1601'),
    ]

    operations = [
        migrations.AlterField(
            model_name='category',
            name='level',
            field=models.PositiveIntegerField(editable=False),
        ),
        migrations.AlterField(
            model_name='category',
            name='lft',
            field=models.PositiveIntegerField(editable=False),
        ),
        migrations.AlterField(
            model_name='category',
            name='rght',
            field=models.PositiveIntegerField(editable=False),
        ),
    ]
