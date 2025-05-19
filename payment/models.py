from django.db import models
from django.contrib.auth.models import User
from store.models import Product
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
import datetime


class ShippingAddress(models.Model):
    user = models.ForeignKey(to=User, on_delete=models.CASCADE, null=True, blank=True, related_name="user_shipping_address")
    shipping_full_name = models.CharField(max_length=255)
    shipping_email = models.EmailField()
    shipping_address1 = models.CharField(max_length=255)
    shipping_address2 = models.CharField(max_length=255, null=True, blank=True)
    shipping_city = models.CharField(max_length=255)
    shipping_state = models.CharField(max_length=255, null=True, blank=True)
    shipping_zipcode = models.CharField(max_length=255, null=True, blank=True)
    shipping_country = models.CharField(max_length=255)

    class Meta:
        verbose_name_plural = "Shipping Address"

    def __str__(self):
        return f"Shipping Address - {str(self.id)}"

# Function to create a user's Profile
def create_shipping_address(sender, instance, created, **kwargs):
    if created:
        shipping_address = ShippingAddress(user=instance)
        shipping_address.save()

# Automate the creation of a user's Profile
post_save.connect(create_shipping_address, sender=User)
        

class Order(models.Model):
    user = models.ForeignKey(to=User, on_delete=models.CASCADE, null=True, blank=True, related_name="user_order")
    shipping_full_name = models.CharField(max_length=255)
    shipping_email = models.EmailField()
    shipping_address = models.TextField(max_length=15000)
    amount_paid = models.DecimalField(max_digits=7, decimal_places=2)
    date_ordered = models.DateTimeField(auto_now_add=True)
    shipped = models.BooleanField(default=False)
    date_shipped = models.DateTimeField(blank=True, null=True)
    
    def __str__(self):
        return f"Order #{self.id}"


# Auto add shipping date
@receiver(pre_save, sender=Order)
def set_shipping_date_on_update(sender, instance, **kwargs):
    if instance.pk:
        datetime_now = datetime.datetime.now()
        # obj == thing we need to save
        obj = sender._default_manager.get(pk=instance.pk)
        if instance.shipped and not obj.shipped:
            instance.date_shipped = datetime_now


class OrderItem(models.Model):
    # Foreign keys
    user = models.ForeignKey(to=User, on_delete=models.CASCADE, null=True, blank=True, related_name="user_order_items")
    order = models.ForeignKey(to=Order, on_delete=models.CASCADE, null=True, blank=True, related_name="order_of_order_items")
    product = models.ForeignKey(to=Product, on_delete=models.CASCADE, null=True, blank=True, related_name="product_of_order_items")

    quantity = models.PositiveBigIntegerField(default=1)
    price = models.DecimalField(max_digits=7, decimal_places=2)

    def __str__(self):
        return f"Order items of Order #{self.order.id}"
    