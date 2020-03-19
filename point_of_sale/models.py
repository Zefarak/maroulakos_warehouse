from django.db import models


from project_settings.constants import SALE_INVOICE_TYPES
from project_settings.models import PaymentMethod
from catalogue.models import Product, ProductStorage
from costumers.models import Costumer

from decimal import Decimal


class SalesInvoice(models.Model):
    date = models.DateField(verbose_name='Ημερομηνια')
    order_type = models.CharField(max_length=1, choices=SALE_INVOICE_TYPES, default='a')
    title = models.CharField(max_length=150, verbose_name='Αριθμος Τιμολογιου')
    payment_method = models.ForeignKey(PaymentMethod, on_delete=models.PROTECT, null=True,
                                       verbose_name='Τροπος Πληρωμης')
    costumer = models.ForeignKey(Costumer, on_delete=models.CASCADE, related_name='invoices', verbose_name='Προμηθευτης')
    value = models.DecimalField(decimal_places=2, max_digits=20, verbose_name='Καθαρή Αξια', default=0)
    extra_value = models.DecimalField(decimal_places=2, max_digits=20, verbose_name='Επιπλέον Αξία', default=0)
    final_value = models.DecimalField(decimal_places=2, max_digits=20, verbose_name='Αξία', default=0.00)
    description = models.TextField(blank=True, verbose_name='Λεπτομεριες')

    def __str__(self):
        return self.title


class SaleInvoiceItem(models.Model):
    UNITS = (
        ('a', 'Τεμάχιο'),
        ('b', 'Κιβώτιο'),
        ('c', 'Κιλό'),

    )
    order_code = models.CharField(max_length=50, blank=True)
    costumer = models.ForeignKey(Costumer, on_delete=models.PROTECT, verbose_name='')
    invoice = models.ForeignKey(SalesInvoice, on_delete=models.CASCADE, related_name='order_items')
    product = models.ForeignKey(Product, on_delete=models.PROTECT, verbose_name='product_items')

    unit = models.CharField(max_length=1, choices=UNITS, default='a', verbose_name='ΜΜ')
    qty = models.DecimalField(max_digits=17, decimal_places=2, default=1, verbose_name='Ποσότητα')
    value = models.DecimalField(max_digits=17, decimal_places=2, verbose_name='Τιμή')

    discount = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name='Εκπτωση')
    discount_value = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name='Ποσο Εκπτωσης')

    clean_value = models.DecimalField(max_digits=17, decimal_places=2, verbose_name='Αξια')
    total_clean_value = models.DecimalField(max_digits=17, decimal_places=2, verbose_name='Καθαρη Αξια')
    taxes_modifier = models.IntegerField(default=24, verbose_name='ΦΠΑ')
    taxes_value = models.DecimalField(max_digits=17, decimal_places=2, verbose_name='Αξια ΦΠΑ')
    total_value = models.DecimalField(max_digits=17, decimal_places=2, verbose_name='Τελικη Αξία')
    storage = models.ForeignKey(ProductStorage, blank=True, null=True, on_delete=models.CASCADE, related_name='storage_invoices')

    def save(self, *args, **kwargs):
        self.clean_value = self.qty * self.value
        self.discount_value = Decimal(self.clean_value) * Decimal(self.discount / 100)
        self.total_clean_value = Decimal(self.clean_value) - Decimal(self.discount_value)
        self.taxes_value = Decimal(self.total_clean_value) * Decimal(self.taxes_modifier / 100)
        self.total_value = Decimal(self.total_clean_value) + Decimal(self.taxes_value)

        super().save(*args, **kwargs)
        if self.storage:
            self.storage.update_product(self.value, self.discount, )
            self.storage.save()
        else:
            self.product.save()
        self.invoice.save()

    def tag_value(self):
        str_value = str(self.value).replace('.', ',')
        return str_value

    def tag_clean_value(self):
        return str(self.clean_value).replace('.', ',')

    def tag_total_value(self):
        return str(self.total_clean_value).replace('.', ',')

    def tag_discount(self):
        return str(self.discount).replace('.', ',')