from django.shortcuts import render, redirect
from . import models
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from store.forms import SignUpForm, UpdateUserProfileForm, ChangePasswordForm, UserInfoForm
from django.db.models import Q
import json
from cart.cart import Cart
from payment.forms import ShippingForm
from payment.models import ShippingAddress


def home(request):
    products = models.Product.objects.all()
    context = {
        'products': products
    }
    return render(request, 'home.html', context)


def about(request):
    context = {}
    return render(request, 'about.html', context)


def login_user(request):
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']

        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            
            # Get user's saved cart
            current_profile = models.Profile.objects.get(user__id=request.user.id)
            # Get their saved cart from database
            saved_cart = current_profile.old_cart
            # Convert database string to python dictionary
            if saved_cart:
                # Convert to dictionary using JSON
                converted_cart = json.loads(saved_cart)
                # Add the loaded cart dictionary to our session
                # Get cart
                cart = Cart(request)
                # Loop through the cart and add the items from the database
                for key, value in converted_cart.items():
                    cart.db_add(product=key, quantity=value)
            
            messages.success(request, ("You have successfully logged in!"))
            return redirect("home")
        else:
            messages.error(request, ("Login attempt unsuccessful"))
            return redirect("login")
    else:
        context = {}
        return render(request, 'login.html', context)


def logout_user(request):
    logout(request)

    context = {}
    return render(request, 'logout.html', context)


def register_user(request):
    form = SignUpForm()
    if request.method == "POST":
        form = SignUpForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data['username']
            password = form.cleaned_data['password1']
            # Log user in
            user = authenticate(request, username=username, password=password)
            login(request, user)
            messages.success(request, ("You have successfully registered, please tell us more about yourself"))
            return redirect('update_info')
        else:
            messages.error(request, ("There was an issue registering, please try again"))
            return redirect('register')
    else:
        context = {
            "form": SignUpForm
        }
    
    return render(request, 'register.html', context)


@login_required
def update_user(request):
    # Get user
    current_user = User.objects.get(id=request.user.id)
    form = UpdateUserProfileForm(request.POST or None, instance=current_user)
    if request.method == "POST":
        if form.is_valid():
            form.save()
            login(request, current_user)
            messages.success(request, ("You have successfully updated your profile"))
            return redirect('home')
        else:
            messages.error(request, ("There was an issue updating your profile, please try again"))
            return redirect('update_user')
    else:
        context = {
            "form": form
        }
        return render(request, 'update_user.html', context)


@login_required
def update_password(request):
    # Get user
    current_user = User.objects.get(id=request.user.id)
    if request.method == "POST":
        form = ChangePasswordForm(current_user, request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, ("Your password has successfully updated"))
            login(request, current_user) # TODO: Is this safe?
            return redirect('update_password')
        else:
            for error in list(form.errors.values()):
                messages.error(request, error)
            
            return redirect('update_password')
    else:
        form = ChangePasswordForm(current_user)
        context = {
            'form': form
        }
        return render(request, 'update_password.html', context)


@login_required
def update_info(request):
    # Get current user
    current_user = models.Profile.objects.get(user__id=request.user.id)
    # Get current user's shipping address
    shipping_address = ShippingAddress.objects.get(user__id=request.user.id)
    
    form = UserInfoForm(request.POST or None, instance=current_user)
    shipping_form = ShippingForm(request.POST or None, instance=shipping_address)
    if form.is_valid() or shipping_form.is_valid():
        # Save user info form
        form.save()
        # Save shipping form
        shipping_form.save()
        
        messages.success(request, ("Your info has successfully been updated"))
        return redirect('home')
    
    context = {
        'form': form,
        'shipping_form': shipping_form
    }
    return render(request, 'update_info.html', context)


def product(request, pk):
    context = {
        'product': models.Product.objects.get(id=pk)
    }
    return render(request, 'product.html', context)


def category(request, catname):
    catname = catname.replace('-', ' ')
    
    try:
        category = models.Category.objects.get(name=catname)
        products = models.Product.objects.filter(category=category)
    except:
        messages.error(request, ("That category does not exists"))
        return redirect('home')
    
    context = {
        'products': products,
        'category': category
    }
    return render(request, 'category.html', context)


def category_summary(request):
    categories = models.Category.objects.all()
    context = {
        'products': [],
        'categories': categories
    }
    return render(request, 'category_summary.html', context)

# Search

def search(request):
    if request.method == "POST":
        searched = request.POST['searched']
        products = models.Product.objects.filter(
            Q(name__icontains=searched)
            | Q(description__icontains=searched)
        )
        context = {
            'searched': searched,
            'products': products
        }
        return render(request, "search.html", context)
    else:
        context = {}
        return render(request, "search.html", context)
