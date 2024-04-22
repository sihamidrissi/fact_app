from django.contrib import admin
from .models import *


class AdminCustomer(admin.ModelAdmin):
    list_display=('name', 'address', 'ICE','CP','CIF','city','zip_code')

class AdminInvoice(admin.ModelAdmin):
    list_display=('customer','save_by','invoice_date_time','total','last_updated_date','paid','invoice_type')
    readonly_fields = ('total_nbre_gb', 'total_weight')  # Make these fields read-only

    def total_nbre_gb(self, obj):
        # Calculate and return the total number of GB for the invoice
        return sum(article.nbre_GB for article in obj.article_set.all())
    
    def total_weight(self, obj):
        # Calculate and return the total weight for the invoice
        return sum(article.quantity for article in obj.article_set.all())

admin.site.register(Customer, AdminCustomer)
admin.site.register(Invoice, AdminInvoice)
admin.site.register(Article)