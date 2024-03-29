import datetime
from django.http import HttpResponse
from django.shortcuts import render, redirect
from base.models import *
from accounts.models import *
from users.forms import OrderForm
from .models import *
import json
from django.contrib import messages
from django.http import HttpResponseRedirect, HttpResponseNotFound
from django.template.loader import render_to_string
from django.core.mail import EmailMessage
from django.shortcuts import get_object_or_404


import paypalrestsdk
from django.conf import settings
from django.urls import reverse
from django.core.exceptions import ObjectDoesNotExist

# Create your views here.

paypalrestsdk.configure({
    "mode": "sandbox",  # Change to "live" for production
    "client_id": settings.PAYPAL_CLIENT_ID,
    "client_secret": settings.PAYPAL_SECRET,
})

def create_payment(request):
    total = 0
    quantity = 0
    cart_items = None
    tax = 0
    grand_total = 0

    try:
        if request.user.is_authenticated:
            # If the user is authenticated, filter the cart items by the user
            cart_items = CartItem.objects.filter(user=request.user, is_active=True).order_by('product__product_name')
        else:
            # If the user is not authenticated, return an empty queryset or handle as needed 
            cart_items = CartItem.objects.none()

        for cart_item in cart_items:
            total += cart_item.product.price * cart_item.quantity
            quantity += cart_item.quantity
        tax = (2 * total) / 100
        grand_total = total + tax

    except ObjectDoesNotExist:
        pass

    # Convert grand_total to string before passing it to PayPal
    grand_total_str = str(grand_total)

    payment = paypalrestsdk.Payment({
        "intent": "sale",
        "payer": {
            "payment_method": "paypal",
        },
        "redirect_urls": {
            "return_url": request.build_absolute_uri(reverse('execute_payment')),
            "cancel_url": request.build_absolute_uri(reverse('payment_failed')),
        },
        "transactions": [
            {
                "amount": {
                    "total": grand_total_str,  # Convert to string
                    "currency": "USD",
                },
                "description": "Payment for Product from Akalibe",
            }
        ],
    })

    if payment.create():
        return redirect(payment.links[1].href)  # Redirect to PayPal for payment
    else:
        return render(request, 'base/payment_failed.html')
    



def execute_payment(request):

    # Fetch user associated with the request
    user = request.user
    order = Order.objects.get(user=user, is_ordered=False)
    
    payment_id = request.GET.get('paymentId')
    payer_id = request.GET.get('PayerID')

    # order = Order.objects.get(user=request.user, is_ordered=False)

    # orderproduct = OrderProduct.objects.filter(user=request.user)

    payment = paypalrestsdk.Payment.find(payment_id)

    try:
        if payment.execute({"payer_id": payer_id}):
            # Payment execution successful, save details to Payment model
            payment_details = payment.to_dict()
            # Extract relevant details from payment_details and save to your Payment model and create Payment object
            payment_obj = Payment.objects.create(
                user=user, # Associate the user with the payment
                payment_id=payment_details['id'],
                full_name = payment_details['payer']['payer_info']['shipping_address']['recipient_name'],
                address = payment_details['payer']['payer_info']['shipping_address']['line1'],
                city = payment_details['payer']['payer_info']['shipping_address']['city'],
                state = payment_details['payer']['payer_info']['shipping_address']['state'],
                country = payment_details['payer']['payer_info']['shipping_address']['country_code'],
                payment_method=payment_details['payer']['payment_method'],
                amount_paid=payment_details['transactions'][0]['amount']['total'],
                status=payment_details['state']
                
            )

            # Associate the payment with the order and mark it as ordered
            order.payment = payment_obj
            order.is_ordered = True
            order.save()

            # move the cart items to order product table
            cart_items = CartItem.objects.filter(user=user)
            for item in cart_items:
                    orderproduct = OrderProduct()
                    orderproduct.order_id = order.id
                    orderproduct.payment = payment_obj
                    orderproduct.user_id = user.id
                    orderproduct.product_id = item.product_id
                    orderproduct.quantity = item.quantity
                    orderproduct.product_price = item.product.price
                    orderproduct.ordered = True
                    orderproduct.save()

                    cart_item = CartItem.objects.get(id=item.id)
                    product_variation = cart_item.variations.all()
                    orderproduct = OrderProduct.objects.get(id=orderproduct.id)
                    orderproduct.variations.set(product_variation)

                    orderproduct.save()


            #reduce quantiy of sold products
                    product = Product.objects.get(uuid=item.product.uuid)
                    product.stock -= item.quantity
                    product.save()

            # Clear cart
            CartItem.objects.filter(user=user).delete()

            #send order received email to customer
            subject = 'Thank you for your order'
            message = render_to_string('orders/order_received_email.html', {
                'user': user, 
                'order': order,   
            })
            to_email = request.user.email
            send_email = EmailMessage(subject, message, to=[to_email])
            send_email.send()

           # Convert payment.amount_paid to float
            amount_paid_float = float(payment_obj.amount_paid) if payment_obj.amount_paid is not None else 0.0

            # Convert order.tax to float
            order_tax_float = float(order.tax) if order.tax is not None else 0.0

            # Perform the subtraction
            subtotal = amount_paid_float - order_tax_float
            grand_total = payment_obj.amount_paid

            order_products = OrderProduct.objects.filter(order=order)

            context = {
                'subtotal': subtotal,
                'grand_total': grand_total,
                'order': order,
                'order_products': order_products,
                'payment': payment_obj,
            }

            # Redirect to payment success page
            print('payment_success')
            return render(request, 'base/payment_success.html', context)
            # return HttpResponseRedirect(reverse('payment_success'))
        else:
            # Payment execution failed
            messages.error(request, 'Payment execution failed.')
            print('payment_failed')
            return HttpResponseRedirect(reverse('payment_failed'))
    
    except Exception as e:
        # Handle any exceptions that might occur during payment execution
        messages.error(request, f'An error occurred during payment execution: {str(e)}')
        print(str(e))
        return HttpResponseRedirect(reverse('payment_failed'))






# def payment_success(request):
    
#     context = {
#             } 
#     return render(request, 'base/payment_success.html', context)



def payment_checkout(request):
    return render(request, 'base/checkout.html')


def payment_failed(request):
    return render(request, 'base/payment_failed.html')


def place_order(request):
    current_user = request.user

    # if the cart count is 0 then redirect back to store

    cart_items = CartItem.objects.filter(user=current_user)
    cart_count = cart_items.count()
    if cart_count <= 0:
        return redirect('store')
    
    grand_total = 0
    tax = 0
    total = 0
    quantity = 0

    for cart_item in cart_items:
        total += (cart_item.product.price * cart_item.quantity)
        quantity += cart_item.quantity
    tax = (2 * total)/100
    grand_total = total + tax
    
    if request.method == 'POST':
        form = OrderForm(request.POST)
        if form.is_valid():
            #store all the billing information inside the Order table
            data = Order()
            data.user = current_user
            data.first_name = form.cleaned_data['first_name']
            data.last_name = form.cleaned_data['last_name']
            data.email = form.cleaned_data['email']
            data.phone = form.cleaned_data['phone']
            data.address_line_1 = form.cleaned_data['address_line_1']
            data.address_line_2 = form.cleaned_data['address_line_2']
            data.country = form.cleaned_data['country']
            data.state = form.cleaned_data['state']
            data.city = form.cleaned_data['city']
            data.order_note = form.cleaned_data['order_note']
            data.order_total = grand_total
            data.tax = tax
            data.ip = request.META.get('REMOTE_ADDR')
            data.save()
            # Generate Order Number
            yr = int(datetime.date.today().strftime('%Y'))
            dt = int(datetime.date.today().strftime('%d'))
            mt = int(datetime.date.today().strftime('%m'))
            d = datetime.date(yr,mt,dt)
            current_date = d.strftime("%Y%m%d")
            order_number = current_date + str(data.id)
            data.order_number = order_number
            data.save()

            order = Order.objects.get(user=current_user, is_ordered=False, order_number=order_number)
            context = {
                'order': order,
                'cart_items': cart_items,
                'total': total,
                'tax': tax,
                'grand_total': grand_total,
            }
            return render(request, 'base/payments.html', context)
        else:
            return OrderForm()
    else:
        return redirect('checkout')



def payments(request):
    body = json.loads(request.body)
    print(body)
    return render(request, 'base/payments.html')