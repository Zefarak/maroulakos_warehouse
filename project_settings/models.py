from django.db import models
from django.shortcuts import reverse
# Create your models here.

PAYMENT_METHOD_CATEGORY = (
    ('a', 'Αντικαταβολή'),
    ('b', 'Τραπεζική ΚατάΘεση')
)


class PaymentMethod(models.Model):
    title = models.CharField(max_length=200, unique=True, verbose_name='Τιτλος')
    category = models.CharField(max_length=1, choices=PAYMENT_METHOD_CATEGORY, verbose_name='Κατηγορια')

    def __str__(self):
        return self.title


class Storage(models.Model):
    active = models.BooleanField(default=True, verbose_name='Κατασταση')
    title = models.CharField(unique=True, max_length=250, verbose_name='Ονομασια')
    position = models.TextField(blank=True, null=True)
    capacity = models.DecimalField(decimal_places=2, max_digits=17, default=0, verbose_name='Χωρητικοτητα')
    max_capacity = models.DecimalField(decimal_places=2, max_digits=17, default=0, verbose_name='Μεγιστη Χωρητικοτητα')
    warning_max_capacity = models.DecimalField(decimal_places=2, max_digits=17, default=0)
    warning_low_max_capacity = models.DecimalField(decimal_places=2, max_digits=17, default=0)

    def __str__(self):
        return self.title

    def get_edit_url(self):
        return reverse('settings:storage_update', kwargs={'pk': self.id})

    def get_delete_url(self):
        return reverse('settings:storage_delete', kwargs={'pk': self.id})

    def get_storage_url(self):
        return reverse('settings:storage_analysis', kwargs={'pk': self.id})
