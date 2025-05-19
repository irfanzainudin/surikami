from django.contrib import admin
from . import models
from django.contrib.auth.models import User

admin.site.register(models.Category)
admin.site.register(models.Customer)
admin.site.register(models.Product)
admin.site.register(models.Order)
admin.site.register(models.Profile)

# Mix Profile and User info
class ProfileInline(admin.StackedInline):
    model = models.Profile

class UserAdmin(admin.ModelAdmin):
    model = User
    field = ["username", "first_name", "last_name", "email"]
    inlines = [ProfileInline]

# NOTE: Code below is just a feature (?) of Django
# that you need to make to ensure the changes
# are reflected on the admin page

# Unregister the old way
admin.site.unregister(User)

# Re-register the new way
admin.site.register(User, UserAdmin)