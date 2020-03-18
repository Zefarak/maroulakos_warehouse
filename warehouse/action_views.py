from django.shortcuts import render, reverse, get_object_or_404, HttpResponseRedirect, redirect
from django.utils.decorators import method_decorator
from django.contrib.admin.views.decorators import staff_member_required

from django.contrib import messages

from .forms import InvoiceVendorDetailForm, InvoiceProductForm, InvoiceItemForm, InvoiceForm, InvoiceTransformationItemForm
from .models import Vendor, Invoice, InvoiceItem, Product
from .warehouse_models import InvoiceTransformation, InvoiceTransformationIngredient


@staff_member_required
def validate_invoice_form_view(request, pk):
    vendor = get_object_or_404(Vendor, id=pk)
    form = InvoiceVendorDetailForm(request.POST or None, initial={'vendor': vendor})
    if form.is_valid():
        new_instance = form.save()
        messages.success(request, f'Το παραστατικό {new_instance.title} δημιουργηθηκε.')
        return redirect(new_instance.get_edit_url())
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


@staff_member_required
def create_product_from_invoice(request, pk):
    instance = get_object_or_404(Invoice, id=pk)
    form = InvoiceProductForm(request.POST or None, initial={'vendor': instance.vendor})
    if form.is_valid():
        product = form.save()
        qty = form.cleaned_data.get('qty', 1)
        '''
        new_item =InvoiceItem.object.create(
                    order_code=product.order_sku,
                    vendor=product.vendor,
                    invoice=invoice,    
                    product=product,
                    unit=product.unit,
                    qty=qty,
                    value=product.price_buy,
                    discount=product.order_discount,
                    taxes_modifier=product.taxes_modifier    
                )
        '''
        
        return redirect(instance.get_edit_url())
    else:
        messages.warning(request, form.errors)
    return redirect(instance.get_edit_url())


@staff_member_required
def validate_create_invoice_order_item_view(request, pk):
    instance = get_object_or_404(Invoice, id=pk)
    form = InvoiceItemForm(request.POST or None, initial={'invoice': instance,
                                                          'vendor': instance.vendor,
                                                          })
    if form.is_valid():
        form.save()
    return redirect(instance.get_edit_url())


@staff_member_required
def validate_order_item_update_view(request, pk):
    instance = get_object_or_404(InvoiceItem, id=pk)
    form = InvoiceItemForm(request.POST or None, instance=instance)
    if form.is_valid():
        form.save()
    return redirect(instance.invoice.get_edit_url())


@staff_member_required
def validate_invoice_edit_view(request, pk):
    instance = get_object_or_404(Invoice, id=pk)
    form = InvoiceForm(request.POST or None, instance=instance)
    if form.is_valid():
        form.save()
        messages.success(request, 'Οι αλλαγες Αποθηκευτηκαν')
    return instance.get_edit_url()


@staff_member_required
def add_product_to_invoice_trans_view(request, pk, dk):
    instance = get_object_or_404(InvoiceTransformation, id=pk)
    product_ = get_object_or_404(Product, id=dk)
    form_title = 'Create'
    info_trans = True

    back_url = instance.get_edit_url()
    form = InvoiceTransformationItemForm(request.POST or None, initial={'product': product_,
                                                                        'invoice': instance}
                                         )
    if form.is_valid():
        item = form.save()
        ingredients = product_.ingredients.all()
        for ingre in ingredients:
            pro = ingre.ingredient
            new_ingre = InvoiceTransformationIngredient.objects.create(
                invoice_item=item,
                product=pro,
                qty=form.cleaned_data['qty']/ingre.qty if ingre.qty != 0 else 0,
                cost=pro.price_buy
            )
            if pro.favorite_storage():
                new_ingre.storage = pro.favorite_storage()
                new_ingre.save()


        return redirect(instance.get_edit_url())
    return render(request, 'warehouse/form_view.html', context=locals())

