from django.shortcuts import render, redirect
from .models import Product, Category, Profile
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.models import User
from .forms import SignUpForm, UpdateUserForm, ChangePasswordForm,UserInfoForm
from Payment.forms import ShippingForm
from Payment.models import ShippingAddress
import json
from Cart.cart import Cart




# Create your views here.
def home(request):
    
    products = Product.objects.all()
    return render(request, 'home.html', {'products': products})

def about(request):
    return render(request, 'about.html', {})

def login_user(request):
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            # Cart persistance
            current_user = Profile.objects.get(user__id=request.user.id)
            # get save cart from db
            saved_cart = current_user.old_cart
            # convert db str to dict.
            if saved_cart:
                # covert to dict. using json
                converted_cart = json.loads(saved_cart)
                # add loaded dict to session
                # get cart
                cart=Cart(request)
                # loop through cart to add items
                for key,value in converted_cart.items():
                    cart.db_add(product=key, quantity=value)
            messages.success(request, ("logged In Successfully"))
            return redirect('home')
        else:
            messages.warning(request, ("Error, Please Input Correct Username/Password And Try Again"))
            return redirect('login')
    else:
        return render(request, 'login.html', {})

def logout_user(request):
    logout(request)
    messages.success(request, ("You have been logged out Successfully"))
    return redirect('home')

def register_user(request):
    form = SignUpForm()
    if request.method == "POST":
        form = SignUpForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data['username']
            password = form.cleaned_data['password1']
            # log in user
            user = authenticate(username=username,password=password)
            login(request,user)
            messages.success(request, ("User Name Created, Please fill in User Info Below"))
            return redirect('update_info')
        else:
            messages.success(request, ("Oops! There was a Problem Please Try Again"))
            return redirect('register')
    else:
        return render(request, 'register.html', {'form':form})

def product(request,pk):
    product = Product.objects.get(id=pk)
    return render(request, 'product.html', {'product': product})

def category(request, foo):
    # replace hyphens with spaces
    foo = foo.replace('-', ' ')
    # grab the category from the url
    try:
        # look up the category
        category = Category.objects.get(name=foo)
        products = Product.objects.filter(category=category)
        return render(request, 'category.html', {'products':products, 'category':category})
    except:
        messages.success(request, ("Category Doesn't Exist"))
        return redirect(request, 'home')

def terms(request):
    return render(request, 'terms.html')

def category_summary(request):
    categories= Category.objects.all()
    return render(request, 'category_summary.html', {'categories':categories})

# user views
def update_user(request):
    if request.user.is_authenticated:
        current_user = User.objects.get(id=request.user.id)
        user_form = UpdateUserForm(request.POST or None, instance = current_user)
        if user_form.is_valid():
            user_form.save()
            login(request, current_user)
            messages.success(request, "User Updated!")
            return redirect('home')
        return render(request, "update_user.html", {'user_form': user_form})
    else:
        messages.warning(request, "Please login to access page!")
        return redirect('home')
    

def update_password(request):
    if request.user.is_authenticated:
        current_user = request.user
        # check if they filled the form
        if request.method == 'POST':
            form = ChangePasswordForm(current_user, request.POST)
            if form.is_valid():
                form.save()
                messages.success(request, "Password Updated, You can continue to shop")
                login(request, current_user)
                return redirect('update_user')
            else:
                for error in list(form.errors.values()):
                    messages.error(request, error) # type: ignore
                    return redirect('update_password')
        else:
            form = ChangePasswordForm(current_user)
            return render(request, 'update_password.html', {'form':form})
    else:
        messages.warning(request, "Please login to access page!")

def update_info(request):
    if request.user.is_authenticated:
        # Get Current user
        current_user = Profile.objects.get(user__id=request.user.id)

        # Get Current User's Shipping Info
        shipping_user = ShippingAddress.objects.get(user__id=request.user.id) 
        
        # Get original user form
        form = UserInfoForm(request.POST or None, instance = current_user)
        
        # Get user's shipping form
        shipping_form = ShippingForm(request.POST or None, instance=shipping_user)
        
        if form.is_valid() or shipping_form.is_valid():
            # Saving the original form and the shipping form
            form.save()
            shipping_form.save()
            messages.success(request, "User info Updated!")
            return redirect('home')
        return render(request, "update_info.html", {'form': form, 'shipping_form': shipping_form})
    else:
        messages.warning(request, "Please login to access page!")
        return redirect('home')