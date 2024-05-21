from django.contrib import admin
from django.urls import path
from django.contrib.auth.decorators import login_required
from . import views 

urlpatterns = [
    path('', views.access, name='access'),  # Set access as the first page to show up
    path('index/', login_required(views.HomeView.as_view()), name='index'),  # Apply login_required to the index page
    path('add_customer/', views.AddCustomerView.as_view(), name='add_customer'),
    path('add-invoice/', views.AddInvoiceView.as_view(), name='add-invoice'),
    path('view-invoice/<int:pk>/', views.InvoiceVisualizationView.as_view(), name='view-invoice' ),
    path('invoice-pdf/<int:pk>/', views.get_invoice_pdf, name="invoice-pdf"),
    path('signup/', views.signup, name="signup"),
    path('signin/', views.signin, name="signin"),
    path('signout/', views.signout, name="signout"),
    path('change_password/', views.change_password, name='change_password'),
    path('generate-pdf/<int:invoice_id>/', views.generate_pdf, name='generate_pdf'),
    path('admin/', admin.site.urls),
    path('commande/', views.AddCommandeView.as_view(), name='commande'),
    path('commande_list/', views.CommandeListView.as_view(), name='commande_list'),
    path('view-commande/<int:pk>', views.CommandeVisualizationView.as_view(), name='view-commande'),
    path('delete_commande/<int:commande_number>', views.delete_commande, name='delete_commande'),



   
      



  
    

]