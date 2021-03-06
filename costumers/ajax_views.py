from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import get_object_or_404, redirect, reverse
from django.template.loader import render_to_string
from django.db.models import Sum
from django.http import JsonResponse

from .models import PaymentInvoice, InvoiceItem, CostumerDetails,Costumer
from .forms import CreateInvoiceItemForm, CostumerDetailsForm


@staff_member_required
def ajax_create_item(request, pk):
    instance = get_object_or_404(PaymentInvoice, id=pk)
    form = CreateInvoiceItemForm(request.POST or None, initial={'invoice': instance})
    if form.is_valid():
        form.save()
    instance.refresh_from_db()
    data = dict()
    data['result'] = render_to_string(template_name='costumers/ajax/order_items.html',
                                      request=request,
                                      context={'object': instance})
    data['details'] = render_to_string(template_name='costumers/ajax/order_details.html',
                                       request=request,
                                       context={
                                           'object': instance
                                       }
                                       )
    return JsonResponse(data)


@staff_member_required
def ajax_delete_order_item(request, pk):
    instance = get_object_or_404(InvoiceItem, id=pk)
    order = instance.invoice
    instance.delete()
    order.refresh_from_db()
    data = dict()
    data['result'] = render_to_string(template_name='costumers/ajax/order_items.html',
                                      request=request,
                                      context={
                                          'object': order
                                      }
                                      )
    data['details'] = render_to_string(template_name='costumers/ajax/order_details.html',
                                       request=request,
                                       context={
                                           'object': order
                                       }
                                       )
    return JsonResponse(data)

@staff_member_required
def update_costumer_detail_view(request, pk):
    instance = get_object_or_404(CostumerDetails, id=pk)
    form = CostumerDetailsForm(request.POST or None, instance=instance)
    if form.is_valid():
        form.save()
    else:
        print(form.errors)
    return redirect(instance.invoice.get_edit_url())





@staff_member_required
def ajax_calculate_balance(request):
    customers = Costumer.filters_data(request, Costumer.objects.all())
    total_balance = customers.aggregate(Sum('balance'))['balance__sum'] if customers else 0
    data = dict()
    data['result'] = render_to_string(request=request,
                                      template_name='ajax_views/calculate_balance_view.html',
                                      context = {
                                          'total_balance':total_balance
                                      }
                                      )
    return JsonResponse(data)


@staff_member_required
def quick_view_costumer_view(request, pk):
    costumer = get_object_or_404(Costumer, id=pk)
    data = dict()
    data['result'] = render_to_string(template_name='ajax_views/quick_view_modal.html',
                                      request=request,
                                      context={
                                          'costumer': costumer
                                      })
    return JsonResponse(data)


@staff_member_required
def quick_pay_costumer_view(request, pk):
    customer = get_object_or_404(Costumer, id=pk)
    if customer.balance <= 0:
        return redirect(reverse('costumer_list'))
    payment = Payment.objects.create(customer=customer,
                                     value=customer.balance,
                                     date=timezone.now()
                                     )
    return redirect(reverse('costumer_list'))


@staff_member_required()
def ajax_analysis_view(request):
    date_range = request.GET.get('date_range')
    orders = Order.filters_data(request, Order.objects.all())
    payments = Payment.filters_data(request, Payment.objects.all())
    costumers_orders = orders.values('customer__first_name', 'customer__last_name').annotate(
        total=Sum('value')).order_by('-total')
    costumers_payments = payments.values('customer__first_name', 'customer__last_name').annotate(
        total=Sum('value')).order_by('-total')
    total_value = orders.aggregate(Sum('value'))['value__sum'] if orders else 0
    total_payment = payments.aggregate(Sum('value'))['value__sum'] if payments else 0
    difference = total_value - total_payment
    data = dict()
    data['result'] = render_to_string(template_name='ajax_views/ajax_analysis_view.html',
                                      request=request,
                                      context=locals()
                                      )
    return JsonResponse(data)


@staff_member_required
def ajax_quick_order_view(request, pk):
    instance = get_object_or_404(Order, id=pk)
    data = dict()
    data['result'] = render_to_string(template_name='ajax_views/quick_order_container.html',
                                      request=request,
                                      context={
                                          'instance': instance
                                      }
                                      )
    return JsonResponse(data)


@staff_member_required
def ajax_quick_payment_view(request, pk):
    instance = get_object_or_404(Payment, id=pk)
    data = dict()
    data['result'] = render_to_string(template_name='ajax_views/quick_order_container.html',
                                      request=request,
                                      context={
                                          'instance': instance
                                      }
                                      )
    return JsonResponse(data)


@staff_member_required
def create_costumer_invoice_view(request, pk):
    instance = get_object_or_404(Order, id=pk)
    Order.objects.exclude(id=pk).update(favorite=False)
    instance.favorite = True
    instance.save()
    return redirect(reverse('costumers:payment_invoice_create_costumer', kwargs={'pk': instance.customer.id}))


