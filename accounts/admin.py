from django.contrib import admin

from accounts.models import Customers, Vendors

# Register your models here.
admin.site.register(Vendors)
admin.site.register(Customers)

