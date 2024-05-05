# views.py

from decimal import Decimal
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.core.mail import send_mail
from django.db import transaction
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import redirect, render
from django.template import RequestContext
from django.template.loader import get_template
from django.urls import reverse
from django.views import View
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import update_session_auth_hash

from fact_app import settings
from .decorators import superuser_required
from .models import *
from .utils import pagination, get_invoice

import datetime
import pdfkit
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.decorators.csrf import csrf_protect
from django.db.models import Q
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.http import QueryDict
from django.contrib.auth.decorators import login_required
from django.contrib.auth import update_session_auth_hash
from io import BytesIO
    

from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
class HomeView( View):
    """ Main view """

    templates_name = 'index.html'

    invoices = Invoice.objects.select_related('customer', 'save_by').all().order_by('-invoice_date_time')

    context = {
        'invoices': invoices
    }

    def get(self, request, *args, **kwags):

        items = pagination(request, self.invoices)

        self.context['invoices'] = items

        return render(request, self.templates_name, self.context)


    def post(self, request, *args, **kwagrs):

        # modify an invoice

        if request.POST.get('id_modified'):

            paid = request.POST.get('modified')

            try: 

                obj = Invoice.objects.get(id=request.POST.get('id_modified'))

                if paid == 'True':

                    obj.paid = True

                else:

                    obj.paid = False 

                obj.save() 

                messages.success(request,  ("Modification effectuée avec succès.")) 

            except Exception as e:   

                messages.error(request, f"Désolé, l'erreur suivante s'est produite {e}.")      

        # deleting an invoice    

        if request.POST.get('id_supprimer'):

            try:

                obj = Invoice.objects.get(pk=request.POST.get('id_supprimer'))

                obj.delete()

                messages.success(request, ("La suppression a réussi."))   
            except Exception as e:

                messages.error(request, f"Désolé, l'erreur suivante s'est produite {e}.")      

        items = pagination(request, self.invoices)

        self.context['invoices'] = items

        return render(request, self.templates_name, self.context)    
class AddCustomerView(LoginRequiredMixin, View):
    """Add new customer view"""

    template_name = 'add_customer.html'

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name)

    def post(self, request, *args, **kwargs):
        data = {
            'name': request.POST.get('name'),
            'address': request.POST.get('address'),
            'ICE': request.POST.get('ICE'),
            'city': request.POST.get('city'),
            'zip_code': request.POST.get('zip'),
            'CP': request.POST.get('CP'),
            'CIF': request.POST.get('CIF'),
            'save_by': request.user
        }

        try:
            created = Customer.objects.create(**data)

            if created:
                messages.success(request, "Client enregistré avec succès.")
            else:
                messages.error(request, "Désolé, veuillez réessayer. Les données envoyées sont corrompues.")
        except Exception as e:
            messages.error(request, f"Désolé, notre système a détecté les problèmes suivants: {e}.")

        return render(request, self.template_name)

from django.views.generic import TemplateView

class AddCommandeView(TemplateView):
     """Add a new commande view"""
     template_name="commande.html"
     customers = Customer.objects.select_related('save_by').all()

     def get(self, request, *args, **kwargs):
         context = {'customers': self.customers}  # Use self.customers
         return render(request, self.template_name, context)
        

     def post(self, request, *args, **kwargs):
        data = {
            'customer': request.POST.get('customer'),
            'commande_number': request.POST.get('commande_number'),
            'ref': request.POST.get('ref'),
            'designation': request.POST.get('designation'),
            'Poids': request.POST.get('Poids'),
            'Qt': request.POST.get('Qt'),
            'Prix ': request.POST.get('Prix'),
            'Montant_HT': request.POST.get('Montant_HT'),
            'Total_HT': request.POST.get('Total_HT'),
            'Total_TTC': request.POST.get('Total_TTC'),
            'save_by': request.user
        }

        try:
            created = Commande.objects.create(**data)

            if created:
                messages.success(request, "Le bon de commande est enregistré avec succès.")
            else:
                messages.error(request, "Désolé, veuillez réessayer. Les données envoyées sont corrompues.")
        except Exception as e:
            messages.error(request, f"Désolé, notre système a détecté les problèmes suivants: {e}.")

        return render(request, self.template_name)




     


class AddInvoiceView(LoginRequiredMixin, View):
    """Add a new invoice view"""

    template_name = 'add_invoice.html'
    customers = Customer.objects.select_related('save_by').all() 

    def get(self, request, *args, **kwargs):
        context = {'customers': self.customers}  # Use self.customers
        return render(request, self.template_name, context)

    @transaction.atomic
    def post(self, request, *args, **kwargs):
        try:
            with transaction.atomic():
                customer_id = request.POST.get('customer')
                invoice_type = request.POST.get('invoice_type')
                articles = request.POST.getlist('article')
                qties = request.POST.getlist('qty')
                units = request.POST.getlist('unit')
                total_a = request.POST.getlist('total-a')
                nbre_GB = request.POST.getlist('nbre_GB')  # Retrieve total GB values
                invoice_number = request.POST.get('invoice_number')
                order_number = request.POST.get('order_number')  # Retrieve order_number
                remorque_number = request.POST.get('remorque_number')

                # Initialize total invoice amount, total GB, and total weight
                total_invoice_amount = Decimal(0)
                total_GB = sum(int(nbre_GB) for nbre_GB in nbre_GB)
                total_weight = sum(int(qty) for qty in qties)

                # Create the invoice object
                invoice = Invoice.objects.create(
                    customer_id=customer_id,
                    save_by=request.user,
                    total=total_invoice_amount,  # Initialize with 0
                    invoice_type=invoice_type,
                    invoice_number=invoice_number,
                    order_number=order_number,  # Pass order_number to the invoice object
                    remorque_number=remorque_number,
                    total_nbre_gb=total_GB,  # Assign total GB value to the invoice object
                    total_poid_kg=total_weight  # Assign total weight value to the invoice object
                )

                # Create article objects and calculate totals
                for index, article in enumerate(articles):
                    nbre_GB_value = nbre_GB[index] if index < len(nbre_GB) else 0
                    qty_value = qties[index] if index < len(qties) else 0
                    unit_value = units[index] if index < len(units) else 0
                    total_value = total_a[index] if index < len(total_a) else 0

                    data = Article(
                        invoice=invoice,
                        name=article,
                        nbre_GB=nbre_GB_value,
                        quantity=qty_value,
                        unit_price=unit_value,
                        total=total_value,
                        order_number=order_number  # Pass order_number to the article object
                    )
                    data.save()

                    # Update total invoice amount
                    total_invoice_amount += Decimal(total_value)

                invoice.total = total_invoice_amount  # Update total amount
                invoice.save()

                messages.success(request, "Données enregistrées avec succès.")
                context = {
                    'customers': self.customers,  # Use self.customers
                    'total_GB': total_GB,
                    'total_weight': total_weight,
                    'order_number': order_number  # Pass order_number to the context
                }
                return render(request, self.template_name, context)

        except Exception as e:
            messages.error(request, f"Désolé, l'erreur suivante s'est produite: {e}")

        context = {'customers': self.customers, 'total_GB': total_GB, 'total_weight': total_weight}  # Use self.customers
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
@csrf_protect
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
                error_message = "Erreur! Identifiant ou mot de passe invalide."
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
                error_message = "Erreur : Veuillez corriger les erreurs dans le formulaire."
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
            messages.error(request, "Ce nom d'utilisateur existe déjà! Veuillez essayer un autre nom d'utilisateur.")
            return redirect('access')

        if User.objects.filter(email=email).exists():
            messages.error(request, "L'email existe déjà! Veuillez essayer un autre e-mail.")
            return redirect('access')

        if len(username) > 10:
            messages.error(request, "Le nom d'utilisateur doit comporter moins de 10 caractères.")

        if pass1 != pass2:
            messages.error(request, "Les mots de passe ne correspondent pas!")

        myuser = User.objects.create_user(username, email, pass1)
        myuser.first_name = fname
        myuser.last_name = lname
        myuser
        myuser.save()
        messages.success(request, "Votre compte à été créé avec succès. Nous vous avons envoyé un e-mail de confirmation.")

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
           messages.error(request, "Erreur: Ce nom d'utilisateur/mot de passe n'est pas reconnu.")
           return render(request, "authentication/access.html")

    return render(request, "authentication/access.html")

def signout(request):
    logout(request)
    messages.success(request, "Déconnexion réussie!")
    return redirect('index')

@login_required
def change_password(request):
    if request.method == 'POST':
        print(request.POST)  # Debug: Print form data to console
        form = PasswordChangeForm(user=request.user, data=request.POST)
        if form.is_valid():
            user = form.save()
            # Updating the session with the new password hash to keep the user logged in
            update_session_auth_hash(request, user)
            messages.success(request, 'Votre mot de passe a été mis à jour avec succès!')
            return redirect('change_password')  # Redirect to the same page after successful password change
        else:
            # Display form errors
            print(form.errors)  # Debug: Print form errors to console
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}")
    else:
        form = PasswordChangeForm(user=request.user)
    
    return render(request, 'change_password.html', {'form': form})

from django.http import HttpResponse
from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

def generate_pdf(request, invoice_number):
    # Replace these lines with actual code to retrieve invoice data
    obj = Invoice.objects.get(pk=invoice_number)  # Assuming you have a model named Invoice
    articles = Article.objects.filter(invoice=obj)  # Assuming Article is a related model

    # Create a buffer to store the PDF content
    buffer = BytesIO()

    # Create a PDF document
    doc = SimpleDocTemplate(buffer, pagesize=letter)

    # Define styles for the document
    styles = getSampleStyleSheet()
    style_normal = styles['Normal']
    style_heading = styles['Heading1']

    # Add content to the PDF
    elements = []

    # Add the invoice heading
    elements.append(Paragraph(f"Invoice #{invoice_number}", style_heading))

    # Add customer information
    elements.append(Paragraph(f"Customer: {obj.customer.name}", style_normal))
    elements.append(Paragraph(f"Address: {obj.customer.address}, {obj.customer.city}", style_normal))
    elements.append(Paragraph("", style_normal))  # Add empty line for spacing

    # Create a table for the invoice items
    data = [["Items", "Product ID", "Quantities", "Unit Price", "Subtotal"]]
    for article in articles:
        data.append([article.name, article.id, article.quantity, article.unit_price, article.get_total])
    table_style = TableStyle([('GRID', (0,0), (-1,-1), 1, (0.5,0.5,0.5))])
    t = Table(data)
    t.setStyle(table_style)
    elements.append(t)
    elements.append(Paragraph("", style_normal))  # Add empty line for spacing

    # Add total amount
    elements.append(Paragraph(f"Total: {obj.get_total}", style_normal))

    # Build the PDF document
    doc.build(elements)

    # Set the buffer position to the beginning
    buffer.seek(0)

    # Create a Django response and return the PDF file
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="invoice_{}.pdf"'.format(invoice_number)
    response.write(buffer.getvalue())
    buffer.close()
    return response


