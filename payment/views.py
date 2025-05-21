from django.shortcuts import render, redirect
from django.contrib import messages
from cart.cart import Cart
from payment.models import ShippingAddress, Order, OrderItem
from payment.forms import ShippingForm, BillingForm
from store.models import Profile
from django.contrib.auth.models import User
import datetime

# Imports for Paypal
from django.urls import reverse
from paypal.standard.forms import PayPalPaymentsForm
from django.conf import settings
import uuid # To create unique user ID


def checkout(request):
    # Get cart
    cart = Cart(request)
    
    # Get products saved in cart
    products = cart.get_products()
    quantities = cart.get_quantities()

    # Calculate totals
    totals = cart.total()

    if request.user.is_authenticated:
        # Get current user's shipping address
        shipping_address = ShippingAddress.objects.get(user__id=request.user.id)
        # Checkout as logged in user
        shipping_form = ShippingForm(request.POST or None, instance=shipping_address)
    
        context = {
            'products': products,
            'quantities': quantities,
            'totals': totals,
            'shipping_form': shipping_form
        }
        return render(request, 'checkout.html', context)
    else:
        # Checkout as guest
        shipping_form = ShippingForm(request.POST or None)
    
        context = {
            'products': products,
            'quantities': quantities,
            'totals': totals,
            'shipping_form': shipping_form
        }
        return render(request, 'checkout.html', context)


def billing_info(request):
    if request.POST:
        # Get cart
        cart = Cart(request)
        
        # Get products saved in cart
        products = cart.get_products()
        quantities = cart.get_quantities()

        # Calculate totals
        totals = cart.total()

        # Create a session with Shipping Info
        user_shipping = request.POST
        request.session['user_shipping'] = user_shipping

        # Get the host
        host = request.get_host() # localhost:8000
        
        # Create PayPal form dictionary
        paypal_dict = {
            'business': settings.PAYPAL_RECEIVER_EMAIL,
            'amount': totals,
            'item_name': 'Book Order',
            'no_shipping': '2',
            'invoice': str(uuid.uuid4()),
            'currency_code': 'MYR',
            'notify_url': f'https://{host}{reverse("paypal-ipn")}',
            'return_url': f'https://{host}{reverse("payment_success")}',
            'cancel_return': f'https://{host}{reverse("payment_failed")}',
        }

        # Create actual PayPal button
        paypal_form = PayPalPaymentsForm(initial=paypal_dict)

        # Checkout as logged in user
        if request.user.is_authenticated:
            # Get current user's shipping address
            shipping_address = ShippingAddress.objects.get(user__id=request.user.id)
            shipping_form = ShippingForm(request.POST or None, instance=shipping_address)
            billing_form = BillingForm()
        
            context = {
                'products': products,
                'quantities': quantities,
                'totals': totals,
                'shipping_info': request.POST,
                'billing_form': billing_form,
                'paypal_form': paypal_form,
            }
            return render(request, 'billing_info.html', context)
        else:
            # Checkout as guest
            shipping_info = request.POST
            billing_form = BillingForm()
        
            context = {
                'products': products,
                'quantities': quantities,
                'totals': totals,
                'shipping_info': shipping_info,
                'billing_form': billing_form,
                'paypal_form': paypal_form,
            }
            return render(request, 'billing_info.html', context)
    else:
        messages.error(request, ("Access denied"))
        return redirect('home')


def process_order(request):
    if request.POST:
        # Get cart
        cart = Cart(request)
        
        # Get products saved in cart
        products = cart.get_products()
        quantities = cart.get_quantities()

        # Calculate totals
        totals = cart.total()
        
        # Get Billing Info from the last page
        # billing_form = BillingForm(request.POST or None)
        # Get shipping session data
        user_shipping = request.session.get('user_shipping')
        
        # Gather order info
        full_name = user_shipping['shipping_full_name']
        email = user_shipping['shipping_email']
        amount_paid = totals

        # Create Shipping Address from session info
        shipping_address = f'''
            {user_shipping['shipping_full_name']}
            \n{user_shipping['shipping_address1']}
            \n{user_shipping['shipping_address2']}
            \n{user_shipping['shipping_city']}
            \n{user_shipping['shipping_state']}
            \n{user_shipping['shipping_zipcode']}
            \n{user_shipping['shipping_country']}
        '''

        if request.user.is_authenticated:
            user = request.user
            # Create Order
            new_order = Order(user=user, shipping_full_name=full_name, shipping_email=email, amount_paid=amount_paid, shipping_address=shipping_address)
            new_order.save()

            # Add Order Item(s)
            # Get the order ID
            order_id = new_order.pk
            # Get the product info
            for product in products:
                # Get the product ID
                product_id = product.id
                # Get the product price
                if product.is_on_sale:
                    product_price = product.sale_price
                else:
                    product_price = product.price
                # Get quantity
                for key, value in quantities.items():
                    if int(key) == product_id:
                        new_order_item = OrderItem(user=user, order_id=order_id, product_id=product_id, quantity=value, price=product_price)
                        new_order_item.save()
        
            # Clear out cart after placing order
            for key in list(request.session.keys()):
                if key == "session_key":
                    # Delete the key
                    del request.session[key]
            
            # Delete Cart from Database (old_cart field) after placing order
            current_user = Profile.objects.filter(user__id=request.user.id)
            current_user.update(old_cart='')
        else:
            # Create Order
            new_order = Order(shipping_full_name=full_name, shipping_email=email, amount_paid=amount_paid, shipping_address=shipping_address)
            new_order.save()

            # Add Order Item(s)
            # Get the order ID
            order_id = new_order.pk
            # Get the product info
            for product in products:
                # Get the product ID
                product_id = product.id
                # Get the product price
                if product.is_on_sale:
                    product_price = product.sale_price
                else:
                    product_price = product.price
                # Get quantity
                for key, value in quantities.items():
                    if int(key) == product_id:
                        new_order_item = OrderItem(order_id=order_id, product_id=product_id, quantity=value, price=product_price)
                        new_order_item.save()
        
            # Clear out cart after placing order
            for key in list(request.session.keys()):
                if key == "session_key":
                    # Delete the key
                    del request.session[key]

        messages.success(request, ("Order placed!"))
        return redirect('home')
    else:
        messages.error(request, ("Access denied"))
        return redirect('home')


def payment_success(request):
    context = {}
    return render(request, 'payment_success.html', context)


def payment_failed(request):
    context = {}
    return render(request, 'payment_failed.html', context)


def shipped_dashboard(request):
    if request.user.is_authenticated and request.user.is_superuser:
        orders = Order.objects.filter(shipped=True)

        if request.POST:
            pk = request.POST['num']
            # Get the order
            order = Order.objects.filter(id=pk)
            # Update the status
            order.update(shipped=False)
            
            messages.success(request, ("Shipping Status updated"))
            return redirect('home')
        
        context = {
            'orders': orders
        }
        return render(request, 'shipped_dashboard.html', context)
    else:
        messages.error(request, ("Access Denied"))
        return redirect('home')


def unshipped_dashboard(request):
    if request.user.is_authenticated and request.user.is_superuser:
        orders = Order.objects.filter(shipped=False)

        if request.POST:
            pk = request.POST['num']
            # Get the order
            order = Order.objects.filter(id=pk)
            # Update the status
            datetime_now = datetime.datetime.now()
            order.update(shipped=True, date_shipped=datetime_now)
            
            messages.success(request, ("Shipping Status updated"))
            return redirect('home')
        
        context = {
            'orders': orders
        }
        return render(request, 'unshipped_dashboard.html', context)
    else:
        messages.error(request, ("Access Denied"))
        return redirect('home')


def orders(request, pk):
    if request.user.is_authenticated and request.user.is_superuser:
        # Get the order
        order = Order.objects.get(id=pk)
        # Get the order items
        order_items = OrderItem.objects.filter(order=pk)

        if request.POST:
            status = request.POST['shipping_status']
            # Check if true or false
            if status == 'true':
                # Get the order
                order = Order.objects.filter(id=pk)
                # Update the status
                datetime_now = datetime.datetime.now()
                order.update(shipped=True, date_shipped=datetime_now)
            else:
                # Get the order
                order = Order.objects.filter(id=pk)
                # Update the status
                order.update(shipped=False)
            
            messages.success(request, ("Shipping Status updated"))
            return redirect('home')
        
        context = {
            'order': order,
            'items': order_items
        }
        return render(request, 'orders.html', context)
    else:
        messages.error(request, ("Access Denied"))
        return redirect('home')
