from django.contrib import admin
from django.urls import path
from django.contrib.auth.decorators import login_required
from . import views 

urlpatterns = [
    path('', views.access, name='access'),  # Set access as the first page to show up
    path('dashboard/', login_required(views.HomeView.as_view()), name='index'),  # Apply login_required to the index page
    path('add_customer/', views.AddCustomerView.as_view(), name='add_customer'),
    path('add-invoice/', views.AddInvoiceView.as_view(), name='add-invoice'),
    path('view-invoice/<int:pk>/', views.InvoiceVisualizationView.as_view(), name='view-invoice' ),
    path('invoice-pdf/<int:pk>/', views.get_invoice_pdf, name="invoice-pdf"),
    path('signup/', views.signup, name="signup"),
    path('signin/', views.signin, name="signin"),
    path('signout/', views.signout, name="signout"),
    path('change_password/', views.change_password, name='change_password'),
    
    path('generate-pdf/<int:invoice_id>/', views.generate_pdf, name='generate_pdf')

]
