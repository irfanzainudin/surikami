from store.models import Profile, Product


class Cart():
    def __init__(self, request):
        self.session = request.session
        self.request = request

        # Get the current session key if it exists
        cart = self.session.get('session_key')

        # If the user is new, no session key! Create one!
        if 'session_key' not in request.session:
            cart = self.session['session_key'] = {}
        
        # Make sure cart is available on all pages of website
        self.cart = cart
    
    def __len__(self):
        return len(self.cart)
    
    def deal_with_logged_in_user(self):
        # Deal with logged in user
        if self.request.user.is_authenticated:
            # Get the current user profile
            current_profile = Profile.objects.filter(user__id=self.request.user.id)
            # Convert {'3': 1, '4': 2} to {"3": 1, "4": 2}
            current_cart = str(self.cart).replace("\'", "\"")
            current_profile.update(old_cart=current_cart)
    
    def add(self, product, quantity):
        product_id = str(product.id)
        product_qty = str(quantity)
        
        # Logic
        if product_id in self.cart:
            pass
        else:
            # self.cart[product_id] = {'price': str(product.price)}
            self.cart[product_id] = int(product_qty)
        
        self.session.modified = True

        # Deal with logged in user
        self.deal_with_logged_in_user()
    
    def delete(self, product):
        product_id = str(product)
        
        # Logic
        if product_id in self.cart:
            # self.cart.pop(product_id)
            del self.cart[product_id]
        
        self.session.modified = True

        # Deal with logged in user
        self.deal_with_logged_in_user()
    
    def update(self, product, quantity):
        product_id = str(product.id)
        product_qty = int(quantity)

        # Get cart
        cart = self.cart

        # Update cart
        cart[product_id] = product_qty
        
        self.session.modified = True

        # Deal with logged in user
        self.deal_with_logged_in_user()

        return self.cart
    
    def get_products(self):
        # Get IDs of Products from cart
        product_ids = self.cart.keys()
        
        # Use IDs to lookup products in DB
        products = Product.objects.filter(id__in=product_ids)
        
        return products
    
    def get_quantities(self):
        # Get quantities of Products from cart
        quantities = self.cart
        
        return quantities
    
    def total(self):
        # Get product IDs
        product_ids = self.cart.keys()
        products = Product.objects.filter(id__in=product_ids)
        # Get quantities
        quantities = self.cart

        total_sum = 0
        for key, value in quantities.items():
            key = int(key)
            for product in products:
                if product.id == key:
                    if product.is_on_sale:
                        total_sum += (product.sale_price * value)
                    else:
                        total_sum += (product.price * value)
                else:
                    continue
        
        return float(total_sum)
    
    def db_add(self, product, quantity):
        product_id = product
        product_qty = str(quantity)
        
        # Logic
        if product_id in self.cart:
            pass
        else:
            # self.cart[product_id] = {'price': str(product.price)}
            self.cart[product_id] = int(product_qty)
        
        self.session.modified = True

        # Deal with logged in user
        self.deal_with_logged_in_user()


# ...
