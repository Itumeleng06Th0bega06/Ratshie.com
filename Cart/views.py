from django.shortcuts import render, get_object_or_404, redirect
#from .models import Cart, CartItem
from .cart import Cart
from django.contrib import messages
from decimal import Decimal
from Shop.models import Product
from django.http import JsonResponse

# Create your views here.
def cart(request):
    # get cart
    cart = Cart(request)
    cart_products = cart.get_prods
    quantities = cart.get_quants
    totals = cart.cart_total()
    return render(request, 'cart.html', {'cart_products': cart_products, 'quantities': quantities, 'totals': totals})

def cart_add(request):
    # Get the cart
    cart = Cart(request)

    # test for POST
   
    if request.POST.get('action') == 'post':
        # Get stuff
        product_id = int(request.POST.get('product_id'))
        product_qty = int(request.POST.get('product_qty'))
        
        # lookup product in db
        product = get_object_or_404(Product, id=product_id)

        # save to a session
        cart.add(product=product, quantity=product_qty)
        # get quantity
        cart_quantity = cart.__len__()
        response = JsonResponse({'Product Name: ': product.name, 'qty': cart_quantity})
        messages.success(request, f"{product.name} Added To Cart")
        return response
    messages.success(request, f"Not Added To Cart")

    
def cart_delete(request):
    cart = Cart(request)
    if request.POST.get('action') == 'post':
        # Get stuff
        product_id = int(request.POST.get('product_id'))
        # call delete function
        cart.delete(product=product_id)
        response = JsonResponse({'product':product_id})
        messages.success(request, "Item Removed")
        return response

def cart_update(request):
    cart = Cart(request)
    if request.POST.get('action') == 'post':
        # Get stuff
        product_id = int(request.POST.get('product_id'))
        product_qty = int(request.POST.get('product_qty'))

        cart.update(product=product_id, quantity=product_qty)
        response = JsonResponse({'qty':product_qty})
        messages.success(request, "Item Updated")
        return response

