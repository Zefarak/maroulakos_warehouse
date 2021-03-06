from django.db import models
from django.urls import reverse
from django.db.models import Sum, Q
from project_settings.constants import SALE_INVOICE_TYPES
from project_settings.models import PaymentMethod
from catalogue.models import Product, ProductStorage

from costumers.models import Costumer
from project_settings.tools import initial_date
from project_settings.constants import CURRENCY
from decimal import Decimal
from warehouse.warehouse_models import InvoiceTransformationItem


class SalesInvoice(models.Model):
    date = models.DateField(verbose_name='Ημερομηνια')
    order_type = models.CharField(max_length=1, choices=SALE_INVOICE_TYPES, default='a', verbose_name='Ειδος')
    title = models.CharField(max_length=150, verbose_name='Αριθμος Τιμολογιου', blank=True)
    payment_method = models.ForeignKey(PaymentMethod, on_delete=models.PROTECT, null=True,
                                       verbose_name='Τροπος Πληρωμης')
    lot = models.CharField(blank=True, null=True, max_length=25)
    costumer = models.ForeignKey(Costumer, on_delete=models.CASCADE, related_name='sale_invoices', verbose_name='Πελάτης')
    value = models.DecimalField(decimal_places=2, max_digits=20, verbose_name='Καθαρή Αξια', default=0)
    extra_value = models.DecimalField(decimal_places=2, max_digits=20, verbose_name='Επιπλέον Αξία', default=0)
    etxra_discount = models.DecimalField(decimal_places=2, max_digits=20, verbose_name='Επιπλέον Εκπτωση', default=0)
    final_value = models.DecimalField(decimal_places=2, max_digits=20, verbose_name='Αξία', default=0.00)
    description = models.TextField(blank=True, verbose_name='Λεπτομεριες')
    total_taxes = models.DecimalField(default=0, max_digits=20, decimal_places=2)

    class Meta:
        ordering = ['date']

    def save(self, *args, **kwargs):
        qs = self.order_items.all()
        if not self.title:
            self.title = f'{self.get_order_type_display()} - {self.id}'
        self.value = qs.aggregate(Sum('total_value'))['total_value__sum'] if qs.exists() else 0
        self.total_taxes = qs.aggregate(Sum('taxes_value'))['taxes_value__sum'] if qs.exists() else 0
        self.final_value = self.value + self.extra_value
        super().save(*args, **kwargs)
        self.costumer.update_orders()

    def __str__(self):
        return self.title

    @property
    def clean_value(self):
        return self.final_value - self.total_taxes

    def tag_final_value(self):
        return f'{self.final_value} {CURRENCY}'

    def tag_total_taxes(self):
        return f'{self.total_taxes} {CURRENCY}'

    def tag_order_type(self):
        return f'{self.get_order_type_display()}'

    def tag_person(self):
        return self.costumer

    def get_edit_url(self):
        return reverse('point_of_sale:sales_update', kwargs={'pk': self.id})

    def get_delete_url(self):
        return reverse('point_of_sale:sales_delete', kwargs={'pk': self.id})

    @staticmethod
    def filters_data(request, qs):
        search_name = request.GET.get('search_name', None)
        q = request.GET.get('q', None)
        costumer_name = request.GET.getlist('costumer_name', None)

        date_start, date_end, date_range = initial_date(request, 6)
        if date_start and date_end:
            qs = qs.filter(date__range=[date_start, date_end])

        qs = qs.filter(costumer_id__in=costumer_name) if costumer_name else qs
        if search_name:
            qs = qs.filter(Q(title__icontains=search_name) |
                           Q(costumer__title__icontains=search_name)
                           ).distinct()
        if q:
            qs = qs.filter(Q(title__icontains=q) |
                           Q(costumer__title__icontains=q)
                           ).distinct()
        return qs


class SalesInvoiceItem(models.Model):
    UNITS = (
        ('a', 'Τεμάχιο'),
        ('b', 'Κιβώτιο'),
        ('c', 'Κιλό'),

    )
    expiration_date = models.DateField(blank=True, verbose_name='Ημερομηνια λήξης', null=True)
    order_code = models.CharField(max_length=50, blank=True, verbose_name='Κωδικος Πωλησης')
    costumer = models.ForeignKey(Costumer, on_delete=models.PROTECT, verbose_name='')
    invoice = models.ForeignKey(SalesInvoice, on_delete=models.CASCADE, related_name='order_items')
    product = models.ForeignKey(Product, on_delete=models.PROTECT, related_name='sale_items', verbose_name='Προϊον')
    date = models.DateField(blank=True, null=True,)
    lot = models.CharField(blank=True, null=True, max_length=25)
    unit = models.CharField(max_length=1, choices=UNITS, default='a', verbose_name='ΜΜ')
    qty = models.DecimalField(max_digits=17, decimal_places=2, default=1, verbose_name='Ποσότητα')

    value = models.DecimalField(max_digits=17, decimal_places=2, verbose_name='Τιμή')
    taxes_modifier = models.IntegerField(default=24, verbose_name='ΦΠΑ')
    taxes_value = models.DecimalField(max_digits=17, decimal_places=2, verbose_name='Αξια ΦΠΑ')

    final_value = models.DecimalField(max_digits=17, decimal_places=2, verbose_name='Αξια Με φορο')
    total_value = models.DecimalField(max_digits=17, decimal_places=2, verbose_name='Τελικη Αξία')

    storage = models.ForeignKey(ProductStorage, blank=True, null=True, on_delete=models.CASCADE)

    warehouse_item = models.ForeignKey(InvoiceTransformationItem, null=True, blank=True, on_delete=models.PROTECT, related_name='sale_items')

    def save(self, *args, **kwargs):
        if self.invoice.lot:
            self.lot = self.invoice.lot
        self.date = self.invoice.date
        self.final_value = Decimal(self.value) + (Decimal(self.value)*(Decimal(self.taxes_modifier)/100))
        self.total_value = self.qty * self.final_value

        self.taxes_value = (self.value*(Decimal(self.taxes_modifier)/100))*self.qty
        super().save(*args, **kwargs)

        if self.storage:
            self.storage.update_product(self.value, self.taxes_modifier, )
            self.storage.save()
        else:
            self.product.save()
        self.invoice.save()

    def tag_value(self):
        str_value = str(self.value).replace('.', ',')
        return str_value

    def tag_clean_value(self):
        return str(self.value).replace('.', ',')

    @property
    def transaction_type_method(self):
        return 'remove'

    def transcation_type(self):
        return self.invoice.get_order_type_display()

    def transcation_person(self):
        return self.costumer

    @staticmethod
    def filter_data(request, qs):
        date_start, date_end, date_range = initial_date(request, 6)
        if date_start and date_end:
            qs = qs.filter(invoice__date__range=[date_start, date_end])
        return qs
