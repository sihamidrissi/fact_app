from django.contrib import admin
from django.urls import path


from . import views 
urlpatterns = [
  #  path('admin/', admin.site.urls, name='admin_site'),  # Change the namespace to 'admin_site'
    path('', views.HomeView.as_view(), name='home'),
    path('add_customer', views.AddCustomerView.as_view(), name='add_customer'),
    path('add-invoice', views.AddInvoiceView.as_view(), name='add-invoice'),
    path('view-invoice/<int:pk>', views.InvoiceVisualizationView.as_view(), name='view-invoice' ),
    path('invoice-pdf/<int:pk>', views.get_invoice_pdf, name="invoice-pdf"),
    
]
   