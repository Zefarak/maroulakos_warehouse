# Generated by Django 3.0.1 on 2020-03-28 14:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('catalogue', '0006_auto_20200328_0737'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='safe_warning',
            field=models.BooleanField(default=False),
        ),
    ]