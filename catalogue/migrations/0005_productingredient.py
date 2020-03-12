# Generated by Django 3.0.1 on 2020-03-12 14:09

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('catalogue', '0004_auto_20200312_1518'),
    ]

    operations = [
        migrations.CreateModel(
            name='ProductIngredient',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('qty', models.DecimalField(decimal_places=2, max_digits=17)),
                ('cost', models.DecimalField(decimal_places=2, max_digits=17)),
                ('ingredient', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='ingredient_value', to='catalogue.Product')),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='ingredients', to='catalogue.Product')),
            ],
        ),
    ]
