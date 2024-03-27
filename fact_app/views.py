# views.py

from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.core.mail import send_mail
from django.db import transaction
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import redirect, render
from django.template import RequestContext
from django.template.loader import get_template
from django.urls import reverse
from django.views import View

from fact_app import settings
from .decorators import superuser_required
from .models import *
from .utils import pagination, get_invoice

import datetime
import pdfkit

class HomeView(LoginRequiredMixin, View):
    """Main view"""

    template_name = 'index.html'
    invoices = Invoice.objects.select_related('customer', 'save_by').all().order_by('-invoice_date_time')
    context = {'invoices': invoices}

    def index(request):
        # Check if the user is logged in
        if request.user.is_authenticated:
            # If the user is logged in, render the index.html page
            return render(request, 'index.html')
        else:
            # If the user is not logged in, redirect to the login page
            return redirect('access')

    def get(self, request, *args, **kwargs):
        items = pagination(request, self.invoices)
        self.context['invoices'] = items
        return render(request, self.template_name, self.context)

class AddCustomerView(LoginRequiredMixin, View):
    """Add new customer view"""

    template_name = 'add_customer.html'

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name)

    def post(self, request, *args, **kwargs):
        data = {
            'name': request.POST.get('name'),
            'email': request.POST.get('email'),
            'phone': request.POST.get('phone'),
            'city': request.POST.get('city'),
            'zip_code': request.POST.get('zip'),
            'save_by': request.user
        }

        try:
            created = Customer.objects.create(**data)

            if created:
                messages.success(request, "Customer registered successfully.")
            else:
                messages.error(request, "Sorry, please try again. The data sent is corrupt.")
        except Exception as e:
            messages.error(request, f"Sorry, our system detected the following issues: {e}.")

        return render(request, self.template_name)

class AddInvoiceView(LoginRequiredMixin, View):
    """Add a new invoice view"""

    template_name = 'add_invoice.html'

    def get(self, request, *args, **kwargs):
        customers = Customer.objects.select_related('save_by').all()
        context = {'customers': customers}
        return render(request, self.template_name, context)

    @transaction.atomic()
    def post(self, request, *args, **kwargs):
        items = []
        try:
            customer = request.POST.get('customer')
            type = request.POST.get('invoice_type')
            articles = request.POST.getlist('article')
            qties = request.POST.getlist('qty')
            units = request.POST.getlist('unit')
            total_a = request.POST.getlist('total-a')
            total = request.POST.get('total')
            comment = request.POST.get('comment')

            invoice_object = {
                'customer_id': customer,
                'save_by': request.user,
                'total': total,
                'invoice_type': type,
                'comments': comment
            }

            invoice = Invoice.objects.create(**invoice_object)

            for index, article in enumerate(articles):
                data = Article(
                    invoice_id=invoice.id,
                    name=article,
                    quantity=qties[index],
                    unit_price=units[index],
                    total=total_a[index],
                )
                items.append(data)

            created = Article.objects.bulk_create(items)

            if created:
                messages.success(request, "Data saved successfully.")
            else:
                messages.error(request, "Sorry, please try again. The data sent is corrupt.")
        except Exception as e:
            messages.error(request, f"Sorry, the following error has occurred: {e}")

        customers = Customer.objects.select_related('save_by').all()
        context = {'customers': customers}
        return render(request, self.template_name, context)

class InvoiceVisualizationView(LoginRequiredMixin, View):
    """View to visualize the invoice"""

    template_name = 'invoice.html'

    def get(self, request, *args, **kwargs):
        pk = kwargs.get('pk')
        context = get_invoice(pk)
        return render(request, self.template_name, context)

@superuser_required
def get_invoice_pdf(request, *args, **kwargs):
    """Generate PDF file from HTML file"""

    pk = kwargs.get('pk')
    context = get_invoice(pk)
    context['date'] = datetime.datetime.today()

    template = get_template('invoice-pdf.html')
    html = template.render(context)
    options = {'page-size': 'Letter', 'encoding': 'UTF-8', "enable-local-file-access": ""}
    pdf = pdfkit.from_string(html, False, options)

    response = HttpResponse(pdf, content_type='application/pdf')
    response['Content-Disposition'] = "attachment"
    return response

# Login
def access(request):
    if request.method == "POST":
        if 'login' in request.POST:
            username = request.POST.get('username')
            password = request.POST.get('password')
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('index')
            else:
                error_message = "Error: Invalid username or password."
                return render(request, 'authentication/access.html', {'error_message': error_message})
        elif 'signup' in request.POST:
            form = UserCreationForm(request.POST)
            if form.is_valid():
                form.save()
                username = form.cleaned_data.get('username')
                raw_password = form.cleaned_data.get('password1')
                user = authenticate(username=username, password=raw_password)
                login(request, user)
                return redirect('index')
            else:
                error_message = "Error: Please correct the errors in the form."
                return render(request, 'authentication/access.html', {'error_message': error_message})
    return render(request, 'authentication/access.html')

def signup(request):
    if request.method == "POST":
        username = request.POST.get('username')
        fname = request.POST['fname']
        lname = request.POST['lname']
        email = request.POST['email']
        pass1 = request.POST['pass1']
        pass2 = request.POST['pass2']

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists! Please try another username.")
            return redirect('access')

        if User.objects.filter(email=email).exists():
            messages.error(request, "Email already exists! Please try another email.")
            return redirect('access')

        if len(username) > 10:
            messages.error(request, "Username must be under 10 characters.")

        if pass1 != pass2:
            messages.error(request, "Passwords didn't match!")

        myuser = User.objects.create_user(username, email, pass1)
        myuser.first_name = fname
        myuser.last_name = lname
        myuser
        myuser.save()
        messages.success(request, "Your account has been successfully created. We have sent you a confirmation email.")

        # Welcome email
        subject = "Welcome to BRUMARTEX invoice system"
        message = f"Hello {myuser.first_name}!!\nWelcome to BRUMARTEX invoice system. We have sent you a confirmation email, please confirm your email address in order to activate your account."
        from_email = settings.EMAIL_HOST_USER
        to_list = [myuser.email]

        try:
            send_mail(subject, message, from_email, to_list, fail_silently=True)
        except Exception as e:
            messages.warning(request, f"Failed to send confirmation email: {e}")

        return redirect('signin')

    return render(request, "authentication/signup.html")

def signin(request):
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect('index')
        else:
            messages.error(request, "Error: This username is unrecognized.")
            return render(request, "authentication/access.html")

    return render(request, "authentication/access.html", context_instance=RequestContext(request))

def signout(request):
    logout(request)
    messages.success(request, "Logged out successfully!")
    return redirect('index')
