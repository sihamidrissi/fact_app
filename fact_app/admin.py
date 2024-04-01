from django.contrib import admin
from .models import *


class AdminCustomer(admin.ModelAdmin):
    list_display=('name', 'address', 'ICE','city','zip_code')

class AdminInvoice(admin.ModelAdmin):
    list_display=('customer','save_by','invoice_date_time','total','last_updated_date','paid','invoice_type')

admin.site.register(Customer, AdminCustomer)
admin.site.register(Invoice, AdminInvoice)
admin.site.register(Article)