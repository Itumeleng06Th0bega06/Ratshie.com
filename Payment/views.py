
from django.shortcuts import redirect, render
from django.contrib import messages
from Payment.forms import ShippingForm, PaymentForm
from .models import ShippingAddress, Order,OrderItem
from Shop.models import Product, Profile
from Cart.cart import Cart
import datetime
#paypal
from django.urls import reverse
from paypal.standard.forms import PayPalPaymentsForm
from django.conf import settings
import uuid #unique id for duplicate orders 


# Create your views here.
def payment_success(request):
    return render(request, 'payment/payment_success.html', {})
def payment_failed(request):
    return render(request, 'payment/payment_failed.html', {})


def checkout(request):
    # Get cart items
    cart = Cart(request)
    cart_products = cart.get_prods
    quantities = cart.get_quants
    totals = cart.cart_total()


    if request.user.is_authenticated:
        shipping_user = ShippingAddress.objects.get(user__id=request.user.id)
        shipping_form = ShippingForm(request.POST or None, instance=shipping_user)
        return render(request, 'payments/checkout.html', {
            'cart_products': cart_products,
            'quantities': quantities,
            'totals': totals,
            'shipping_form': shipping_form})
    else:
        shipping_form = ShippingForm(request.POST or None)
        return render(request, 'payments/checkout.html', {
            'cart_products': cart_products,
            'quantities': quantities,
            'totals': totals,
            'shipping_form': shipping_form})
	
        

def billing_info(request,product_id):
    if request.POST:
        cart = Cart(request)
        cart_products = cart.get_prods
        quantities = cart.get_quants
        totals = cart.cart_total()
        product = Product.objects.get(id=product_id)

        # Create a session with shipping info
        my_shipping = request.POST
        request.session['my_shipping'] = my_shipping
        # Get host
        host = request.get_host()
        # paypal form
        paypal_dict={
            'business': settings.PAYPAL_RECEIVER_EMAIL,
            'amount': totals,
            'item_name': 'Parts Order',
            'no_shipping': '2',
            'invoice': str(uuid.uuid4()),
            'currency_code': 'ZAR',
            #'notify_url': 'https://{}{}'.format(host, reverse("paypal-ipn")),
            'notify_url': f"https://{host}{reverse('paypal-ipn')}",
            #'return_url': 'https://{}{}'.format(host, reverse("payment_success")),
            'return_url': f"https://{host}{reverse('payment_success', kwargs={'product_id':product.id})}", # type: ignore
            #'cancel_url': 'https://{}{}'.format(host, reverse("payment_failed")),
            'cancel_url': f"https://{host}{reverse('payment_failed', kwargs={'product_id':product.id})}", # type: ignore
        }
        #paypal button
        paypal_form = PayPalPaymentsForm(initial=paypal_dict)
        if request.user.is_authenticated:
            # get billing form
            billing_form = PaymentForm()
            return render(request, 'payments/billing_info.html', {
                'paypal_form': paypal_form,
                'cart_products': cart_products,
                'quantities': quantities,
                'totals': totals,
                'shipping_info': request.POST, 'billing_form': billing_form})
        elif not request.user.is_authenticated:
            billing_form = PaymentForm()
            return render(request, 'payments/billing_info.html', {
                'paypal_form': paypal_form,
                'cart_products': cart_products,
                'quantities': quantities,
                'totals': totals,
                'shipping_info': request.POST, 'billing_form': billing_form})

        shipping_form = request.POST
        return render(request, 'payments/billing_info.html', {
            'cart_products': cart_products,
            'quantities': quantities,
            'totals': totals,
            'shipping_form': shipping_form})
    else:
        messages.warning(request, 'Access Denied')
        return redirect('home')

def process_order(request):
    if request.POST:
        cart = Cart(request)
        cart_products = cart.get_prods
        quantities = cart.get_quants
        totals = cart.cart_total()

        # Get Billing info from the last page
        payment_form = PaymentForm(request.POST or None)

        # Get shipping session data
        my_shipping = request.session.get('my_shipping')
        
        # Gather  oder info
        full_name = my_shipping['shipping_full_name']
        email = my_shipping['shipping_email']
        # Create Address from session info
        shipping_address = f"{my_shipping['shipping_address1']}\n{my_shipping['shipping_address2']}\n{my_shipping['shipping_city']}\n{my_shipping['shipping_state']}\n{my_shipping['shipping_zipcode']}\n{my_shipping['shipping_country']}"
        amount_paid = totals

        #create an oder
        if request.user.is_authenticated:
            user = request.user
            create_order = Order(user=user, full_name=full_name, email=email, shipping_address=shipping_address, amount_paid=amount_paid)
            create_order.save()

            # add items
            # get order id
            order_id = create_order.pk
            # get product info
            for product in cart_products():
                # get product id
                product_id = product.id # type: ignore
                # get product price
                if product.sale:
                    price = product.sale_price
                else:
                    price = product.price

                # get quantity
                for key, value in quantities().items():
                    if int(key) == product.id: # type: ignore
                        # create order item
                        create_order_item = OrderItem(order_id=order_id, product_id=product_id, user=user, quantity=value, price=price)
                        create_order_item.save()
            # delete cart
            for key in list(request.session.keys()):
                if key == 'session_key':
                    # delete key
                    del request.session[key]
            # delete from db(old cart)
            curr_user = Profile.objects.filter(user__id=request.user.id)
            curr_user.update(old_cart="")
            
            messages.warning(request, 'oder placed')
            return redirect('home')
        else:
            create_order = Order(full_name=full_name, email=email, shipping_address=shipping_address, amount_paid=amount_paid)
            create_order.save()

             # add items
            # get order id
            order_id = create_order.pk
            # get product info
            for product in cart_products():
                # get product id
                product_id = product.id # type: ignore
                # get product price
                if product.sale:
                    price = product.sale_price
                else:
                    price = product.price

                # get quantity
                for key, value in quantities().items():
                    if int(key) == product.id: # type: ignore
                        # create order item
                        create_order_item = OrderItem(order_id=order_id, product_id=product_id, quantity=value, price=price)
                        create_order_item.save()
            # delete cart
            for key in list(request.session.keys()):
                if key == 'session_key':
                    # delete key
                    del request.session[key]
            
            messages.warning(request, 'oder placed')
            return redirect('home')
        
    else:
        messages.warning(request, 'Access Denied')
        return redirect('home')

def shipped_dash(request):
    if request.user.is_authenticated and request.user.is_superuser:
        orders = Order.objects.filter(shipped=True)
        if request.POST:
            status = request.POST['shipping_status']
            num = request.POST['num']
            # get the order
            order = Order.objects.filter(id=num)
            # get the date
            now = datetime.datetime.now()
            # update the order
            order.update(shipped=False)
            # redirect
            #messages.success(request, "Shipping Status Updated")
            return redirect('shipped_dash')
        
        return render(request, 'payments/shipped_dash.html', {'orders': orders})
    else:
        messages.success(request, "Access Denied")
        return redirect(request, 'home')
    

def not_shipped(request):
    if request.user.is_authenticated and request.user.is_superuser:
        orders = Order.objects.filter(shipped=False)
        if request.POST:
            status = request.POST['shipping_status']
            num = request.POST['num']
            # get the order
            order = Order.objects.filter(id=num)
            # get the date
            now = datetime.datetime.now()
            # update the order
            order.update(shipped=True,date_shipped=now)
            # redirect
            #messages.success(request, "Shipping Status Updated")
            return redirect('not_shipped')
        return render(request, 'payments/not_shipped.html', {'orders': orders})
    else:
        messages.success(request, "Access Denied")
        return redirect(request, 'home')
    
def orders(request,pk):
    if request.user.is_authenticated and request.user.is_superuser:
        # get orders
        order = Order.objects.get(id=pk)
        # get order items
        items = OrderItem.objects.filter(order=pk)
        if request.POST:
            status = request.POST['shipping_status']
            # check idf tru or false
            if status == 'true':
                # get the order
                order = Order.objects.filter(id=pk)
                # update
                now = datetime.datetime.now()
                order.update(shipped=True, date_shipped=now)
            else:
                order = Order.objects.filter(id=pk)
                # update
                order.update(shipped=False)
            messages.success(request, "Shipping Status Updated")
            return redirect('home')
        return render(request, 'payments/orders.html', {'order': order, 'items':items})
    else:
        messages.success(request, "Access Denied")
        return redirect(request, 'home')