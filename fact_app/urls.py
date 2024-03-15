from django.contrib import admin
from django.urls import path


from . import views 
urlpatterns = [
  #  path('admin/', admin.site.urls, name='admin_site'),  # Change the namespace to 'admin_site'
    path('', views.HomeView.as_view(), name='home'),
    path('add_customer', views.AddCustomerView.as_view(), name='add_customer'),
]
   