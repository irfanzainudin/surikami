from django.contrib import admin
from . import models


admin.site.register(models.ShippingAddress)
admin.site.register(models.Order)
admin.site.register(models.OrderItem)

# Mix Order and OrderItem info
class OrderItemInline(admin.StackedInline):
    model = models.OrderItem
    extra = 0

# Extend our Order model
class OrderAdmin(admin.ModelAdmin):
    model = models.Order
    inlines = [OrderItemInline]
    readonly_fields = ['date_ordered']
    # fields = ['user', 'shipping_full_name', 'shipping_email', 'shipping_address', 'amount_paid', 'date_ordered']

# NOTE: Code below is just a feature (?) of Django
# that you need to make to ensure the changes
# are reflected on the admin page

# Unregister the old way
admin.site.unregister(models.Order)

# Re-register the new way
admin.site.register(models.Order, OrderAdmin)