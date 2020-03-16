from django.views.generic import ListView, TemplateView, DetailView, CreateView, UpdateView
from django.utils.decorators import method_decorator
from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import reverse, get_object_or_404, redirect

from .models import Vendor, Note, VendorBankingAccount, Invoice
from .warehouse_models import InvoiceTransformation, InvoiceTransformationItem, InvoiceTransformationIngredient

from .forms import (VendorForm, PaymentForm, InvoiceForm, NoteForm, InvoiceVendorDetailForm,
                    InvoiceProductForm, InvoiceTransformationForm
                    )
from catalogue.models import Product, ProductStorage
from .tables import ProductTransTable, VendorTable, InvoiceTable, InvoiceTransformationTable
from .mixins import ListViewMixin

from django_tables2 import RequestConfig

from decimal import Decimal

@method_decorator(staff_member_required, name='dispatch')
class VendorListView(ListView):
    model = Vendor
    template_name = 'warehouse/list_view.html'
    paginate_by = 25

    def get_queryset(self):
        qs = Vendor.objects.all()
        qs = Vendor.filters_data(self.request, qs)
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        qs_table = VendorTable(self.object_list)
        RequestConfig(self.request, paginate={'per_page': self.paginate_by}).configure(qs_table)
        queryset_table = qs_table
        create_url = reverse('warehouse:vendor_create')
        page_title, back_url = 'Προμηθευτές', reverse('warehouse:homepage')
        # report_button, report_url = True, reverse('vendors:ajax_vendors_balance')
        balance_filter, search_filter = [True] * 2
        context.update(locals())
        return context


@method_decorator(staff_member_required, name='dispatch')
class CreateVendorView(CreateView):
    template_name = 'warehouse/form_view.html'
    model = Vendor
    form_class = VendorForm

    def get_initial(self):
        initial = super().get_initial()
        # initial['site'] = 'http://'
        return initial

    def get_success_url(self):
        return self.new_object.get_edit_url()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["form_title"], context['back_url'], = 'Δημιουργια Προμηθευτη', reverse('warehouse:vendor_list')

        return context

    def form_valid(self, form):
        self.new_object = form.save()
        new_vendor = form.cleaned_data['title']
        messages.success(self.request, f'Ο Προμηθευτής {new_vendor} δημιουργήθηκε.')
        return super().form_valid(form)


@method_decorator(staff_member_required, name='dispatch')
class UpdateVendorView(UpdateView):
    model = Vendor
    template_name = 'warehouse/update_vendor.html'
    form_class = VendorForm

    def get_success_url(self):
        return self.object.get_edit_url()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['invoice_form'] = InvoiceVendorDetailForm(initial={'vendor': self.object})
        context['payment_form'] = PaymentForm(initial={'vendor': self.object})
        # context['employer_form'] = EmployerForm(initial={'vendor': self.object})
        # context['page_title'] = f'{self.object.title}'
        # context['notes'] = Note.objects.filter(vendor_related=self.object, status=True)
        # context['invoices'] = Invoice.filters_data(self.request, self.object.invoices.all())
        # context['payments'] = Payment.filters_data(self.request, self.object.payments.all())
        # context['action_url'] = reverse('vendors:list')
        return context


@staff_member_required
def delete_vendor_view(request, pk):
    instance = get_object_or_404(Vendor, id=pk)
    instance.delete()
    return redirect(reverse('warehouse:vendor_list'))


@method_decorator(staff_member_required, name='dispatch')
class VendorNotesView(ListView):
    template_name = 'vendors/NoteContainer.html'
    model = Note

    def get_queryset(self):
        self.vendor = get_object_or_404(Vendor, id=self.kwargs['pk'])
        return self.vendor.notes.all()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = f'Σημειώσεις {self.vendor}'
        context['back_url'] = self.vendor.get_edit_url()
        context['form'] = NoteForm(initial={'vendor_related': self.vendor})
        context['vendor'] = self.vendor
        return context


@method_decorator(staff_member_required, name='dispatch')
class NoteUpdateView(UpdateView):
    model = Note
    form_class = NoteForm
    template_name = 'vendors/note_update.html'

    def get_initial(self):
        initial = super().get_initial()
        initial['vendor_related'] = self.object.vendor_related
        return initial

    def get_success_url(self):
        vendor = self.object.vendor_related
        return reverse('vendors:notes', kwargs={'pk': vendor.id})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["vendor"] = self.object.vendor_related
        context['back_url'] = self.get_success_url()
        return context

    def form_valid(self, form):
        form.save()
        return super().form_valid(form)


@staff_member_required
def delete_note_view(request, pk):
    note = get_object_or_404(Note, id=pk)
    note.delete()
    return redirect(reverse('vendors:notes', kwargs={'pk': note.vendor_related.id}))


@method_decorator(staff_member_required, name='dispatch')
class VendorCardView(ListView):
    model = Product
    template_name = 'vendors/vendor_card.html'
    paginate_by = 500

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["vendor"] = self.vendor

        context['search_filter'], context['category_filter'] = [True] * 2
        cate_ids = self.object_list.values_list('product__categories').distinct()

        return context


@method_decorator(staff_member_required, name='dispatch')
class HomepageView(TemplateView):
    template_name = 'warehouse/dashboard.html'


@method_decorator(staff_member_required, name='dispatch')
class ProductTransformationListView(ListView):
    template_name = 'warehouse/list_view.html'
    model = Product

    def get_queryset(self):
        qs = Product.objects.filter(product_class__have_ingredient=True)
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        qs_table = ProductTransTable(self.object_list)
        context['queryset_table'] = qs_table
        return context


@method_decorator(staff_member_required, name='dispatch')
class InvoiceTransformationListView(ListView):
    template_name = 'warehouse/list_view.html'
    model = InvoiceTransformation

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        queryset_table = InvoiceTransformationTable(self.object_list)

        context['queryset_table'] = queryset_table
        return context


@method_decorator(staff_member_required, name='dispatch')
class InvoiceTransformationDetailView(DetailView):
    template_name = 'warehouse/transfo_detail.html'
    model = InvoiceTransformation


@method_decorator(staff_member_required, name='dispatch')
class ProductTransformationPrepareView(DetailView):
    model = Product
    template_name = 'warehouse/prepare_view.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        max_per_ind = []
        for ele in self.object.ingredients.all():
            max_per_ind.append(ele.ingredient.qty/ele.qty if ele.qty != 0 else 0)
        context['max_items'] = min(max_per_ind)
        context['create_form'] = InvoiceTransformationForm()
        context['invoices'] = InvoiceTransformation.objects.filter(locked=False)
        return context

    def post(self, request, *args, **kwargs):
        my_product = get_object_or_404(Product, id=self.kwargs['pk'])
        form = InvoiceTransformationForm(request.POST or None)
        ids, storages_ids = [], []
        print('product', my_product)
        for ele in request.POST:
            if str(ele).startswith('product_'):
                product, id = ele.split('_')
                ids.append([id, request.POST.get(ele)])
            if str(ele).startswith('storage_'):
                storage, id = ele.split('_')
                storages_ids.append([id, request.POST.get(ele)])
        qty = Decimal(request.POST.get('qty', 0))
        if form.is_valid():
            new_invoice = form.save()
        else:
            new_invoice = get_object_or_404(InvoiceTransformation, id=request.POST.get('edit_form', None))
        new_item = InvoiceTransformationItem.objects.create(
            product=my_product,
            invoice=new_invoice,
            qty=qty
        )
        for id_list in ids:
            storage = None
            for ele in storages_ids:
                if ele[0] == id_list[0]:
                    storage = get_object_or_404(ProductStorage, id=ele[1])
            product = get_object_or_404(Product, id=id_list[0])
            InvoiceTransformationIngredient.objects.create(
                invoice_item=new_item,
                product=product,
                qty=qty,
                cost=id_list[1],
                storage=storage
            )
        return self.render_to_response(context={})
    

@method_decorator(staff_member_required, name='dispatch')
class InvoiceListView(ListView):
    model = Invoice
    template_name = 'warehouse/list_view.html'
    paginate_by = 25

    def get_queryset(self):
        qs = Invoice.objects.all()
        qs = Invoice.filters_data(self.request, qs)
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        qs_table = InvoiceTable(self.object_list)
        RequestConfig(self.request, paginate={'per_page': self.paginate_by}).configure(qs_table)
        queryset_table = qs_table
        create_url = reverse('warehouse:invoice_create')
        page_title, back_url = 'Προμηθευτές', reverse('warehouse:homepage')
        # report_button, report_url = True, reverse('vendors:ajax_vendors_balance')
        balance_filter, search_filter = [True] * 2
        context.update(locals())
        return context


@method_decorator(staff_member_required, name='dispatch')
class CreateInvoiceView(CreateView):
    template_name = 'warehouse/form_view.html'
    model = Invoice
    form_class = InvoiceForm

    def get_initial(self):
        initial = super().get_initial()
        # initial['site'] = 'http://'
        return initial

    def get_success_url(self):
        return self.new_object.get_edit_url()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["form_title"], context['back_url'], = 'Δημιουργια Προμηθευτη', reverse('warehouse:invoice_list')

        return context

    def form_valid(self, form):
        self.new_object = form.save()
        new_vendor = form.cleaned_data['title']
        messages.success(self.request, f'Το Παραστατικο {new_vendor} δημιουργήθηκε.')
        return super().form_valid(form)


@method_decorator(staff_member_required, name='dispatch')
class InvoiceDetailView(UpdateView):
    model = Invoice
    template_name = 'warehouse/invoice_detail.html'
    form_class = InvoiceForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['products'] = Product.objects.filter(vendor=self.object.vendor)
        context['product_form'] = InvoiceProductForm(initial={'vendor': self.object.vendor})
        context['order_items'] = self.object.order_items.all()
        return context


@staff_member_required
def delete_invoice_view(request, pk):
    instance = get_object_or_404(Invoice, id=pk)
    instance.delete()
    return redirect(reverse('warehouse:invoice_list'))


