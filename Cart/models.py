from django.db import models
from django.contrib.auth.models import User
from Shop.models import Product

# Create your models here.
# Cart functionality
class Cart(models.Model):
    # stores cart data for both logged in and anonymous users

    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    session_key = models.CharField(max_length=100, null=True, blank=True)
    status = models.CharField(max_length=20, default='active')
    created_at = models.DateTimeField(auto_now_add=True) # Just added

    class Meta:
        verbose_name = "Cart"
        verbose_name_plural = "Carts"
        unique_together = [['user', 'session_key']]

    def __str__(self):
        if self.user:
            return f"{self.user.username}'s Cart"
        else:
            return f"Anonymous Cart ({self.session_key})"

class CartItem(models.Model):
    # stores idividual products added to cart
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name="items")  # allows cart.items.all()
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveBigIntegerField(default=1)

    class Meta:
        verbose_name = "Cart Item"
        verbose_name_plural = "Carts Items"

    def subtotal(self):
        #price = self.product.sale_price if hasattr(self.product, 'sale_price') and self.product.sale_price else self.product.price
        if self.product.sale_price is not None and self.product.sale_price > 0:
            return self.product.sale_price * self.quantity
        else:
            return self.product.price * self.quantity

    def __str__(self):
        return f'{self.quantity} x {self.product.name}'
    