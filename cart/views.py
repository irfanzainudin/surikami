from django.shortcuts import render, get_object_or_404
from cart.cart import Cart
from store.models import Product
from django.http import JsonResponse
from django.contrib import messages


def cart_summary(request):
    # Get cart
    cart = Cart(request)
    
    # Get products saved in cart
    products = cart.get_products()
    quantities = cart.get_quantities()

    # Calculate totals
    totals = cart.total()
    
    context = {
        'products': products,
        'quantities': quantities,
        'totals': totals
    }
    return render(request, 'cart_summary.html', context)


def cart_add(request):
    # Get cart
    cart = Cart(request)
    if request.POST.get('action') == 'post':
        # Get product
        product_id = int(request.POST.get('product_id'))
        product_qty = str(request.POST.get('product_qty'))
        
        # Lookup product in DB
        product = get_object_or_404(Product, id=product_id)
        
        # Save to session
        cart.add(product=product, quantity=product_qty)
        
        # Get Cart Quantity
        cart_quantity = cart.__len__()
        
        # Return response
        response = JsonResponse({
            'qty': cart_quantity,
            'Product Name ': product.name
        })
        messages.success(
            request,
            ("Product added to cart")
        )
        return response
    else:
        context = {}
        return render(request, 'cart_add.html', context)


def cart_delete(request):
    # Get cart
    cart = Cart(request)
    if request.POST.get('action') == 'post':
        # Get product
        product_id = int(request.POST.get('product_id'))
        
        # Lookup product in DB
        # product = get_object_or_404(Product, id=product_id)
        
        # Save to session
        cart.delete(product=product_id)

        response = JsonResponse({
            'product': product_id
        })
        messages.success(
            request,
            ("Item removed from your cart")
        )
        return response
    else:
        context = {}
        return render(request, 'cart_delete.html', context)


def cart_update(request):
    # Get cart
    cart = Cart(request)
    if request.POST.get('action') == 'post':
        # Get product
        product_id = int(request.POST.get('product_id'))
        product_qty = int(request.POST.get('product_qty'))
        
        # Lookup product in DB
        product = get_object_or_404(Product, id=product_id)
        
        # Save to session
        cart.update(product=product, quantity=product_qty)

        response = JsonResponse({
            'qty': product_qty
        })
        messages.success(
            request,
            ("Your cart is successfully updated")
        )
        return response
    else:
        context = {}
        return render(request, 'cart_update.html', context)