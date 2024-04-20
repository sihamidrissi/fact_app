from django.core.paginator import (Paginator, EmptyPage, PageNotAnInteger)
from .models import *



from django.core.paginator import Paginator

def pagination(request, invoices):
    page_number = request.GET.get('page')
    if page_number == 'all':
        return invoices
    paginator = Paginator(invoices, 10)  # Assuming 10 items per page
    page_obj = paginator.get_page(page_number)
    return page_obj



def get_invoice(pk):
       """ get invoice fonction """
       
       obj = Invoice.objects.get(pk=pk)
       articles = obj.article_set.all()
       context= {
            'obj': obj,
            'articles' : articles
        }
       
       return context 