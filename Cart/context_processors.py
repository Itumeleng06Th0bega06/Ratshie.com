from .cart import Cart

# Create processor for making sure cart works in all pages
def cart(request):
    # return default data from our cart
    return {'cart': Cart(request)}