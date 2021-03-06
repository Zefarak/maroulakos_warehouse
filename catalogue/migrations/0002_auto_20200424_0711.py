# Generated by Django 3.0.1 on 2020-04-24 04:11

from django.db import migrations, models
import django.db.models.deletion
import mptt.fields


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('warehouse', '0001_initial'),
        ('catalogue', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='vendor',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='warehouse.Vendor', verbose_name='Προμηθευτής'),
        ),
        migrations.AddField(
            model_name='category',
            name='parent',
            field=mptt.fields.TreeForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='children', to='catalogue.Category', verbose_name='Γονεας'),
        ),
        migrations.AlterUniqueTogether(
            name='productstorage',
            unique_together={('product', 'storage')},
        ),
        migrations.AlterUniqueTogether(
            name='productingredient',
            unique_together={('product', 'ingredient')},
        ),
    ]
