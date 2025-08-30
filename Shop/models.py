from django.db import models
import datetime
from django.contrib.auth.models import User
from django.db.models.signals import post_save


# customer profile
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    date_modified = models.DateTimeField(User, auto_now=True) # type: ignore 
    phone = models.CharField(max_length=20, blank=True)
    address1 = models.CharField(max_length=200, blank=True)
    address2 = models.CharField(max_length=200, blank=True)
    city = models.CharField(max_length=200, blank=True)
    state = models.CharField(max_length=200, blank=True)
    zipcode = models.CharField(max_length=200, blank=True)
    country = models.CharField(max_length=200, blank=True)
    old_cart = models.CharField(max_length=200, blank=True, null=True)

    def __str__(self):
        return self.user.username


# default user profile when register

def Create_Profile(sender, instance, created, **kwargs):
    if created:
        user_profile = Profile(user=instance)
        user_profile.save()


# automate profile
post_save.connect(Create_Profile, sender=User)


# Category Class.
class Category(models.Model):
    name = models.CharField(max_length=50, default=" ", blank=True)

    # this class is to correct spelling in the admin panel
    class Meta:
        verbose_name_plural = 'Categories'

    def __str__(self):
        return self.name


# Customer Class.
class Customer(models.Model):
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    phone = models.CharField(max_length=10)
    email = models.EmailField(max_length=100)
    password = models.CharField(max_length=100)

    def __str__(self):
        return f'{self.first_name} {self.last_name}'


# Products Class.
class Product(models.Model):
    name = models.CharField(max_length=100)
    price = models.DecimalField(decimal_places=2, max_digits=12, default=None)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    description = models.TextField(max_length=15000, default='', blank=True, null=True)
    image = models.ImageField(upload_to='uploads/product/')
    stock = models.PositiveIntegerField(default=0)

    # Sale

    sale = models.BooleanField(default=False)
    sale_price = models.DecimalField(decimal_places=2, max_digits=12, null=True, blank=True, default=None)

    def __str__(self):
        return self.name


# Order Class.
class Order(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, null=True, blank=True)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)
    address = models.CharField(max_length=100, default='', blank=False)
    phone = models.CharField(max_length=20, default='', blank=True)
    date = models.DateField(default=datetime.datetime.today)
    status = models.BooleanField(default=False)

    def __str__(self):     # str
        return str(self.product)








