from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _
from django.core.validators import MaxValueValidator
from django.db import models




class Customer(models.Model):
    """
    Name: Customer model definition
    """
    
    name = models.CharField(max_length=132)

    #email = models.EmailField()

    #phone = models.CharField(max_length=132)
    address = models.CharField(max_length=300, default='Unknown Address')



    city = models.CharField(max_length=32)

    zip_code = models.CharField(max_length=16)
    ICE = models.IntegerField(default=0)
    CP = models.IntegerField(default=0)
    CIF= models.IntegerField(default=0)

    created_date = models.DateTimeField(auto_now_add=True)

    save_by = models.ForeignKey(User, on_delete=models.PROTECT)

    class Meta: 
        verbose_name = "Customer"
        verbose_name_plural = "Customers"

    def __str__(self):
        return self.name     



class Invoice(models.Model):
    """
    Name: Invoice model definition
    Description: 
    Author: elidrissisiham2@gmail.com
    """

    INVOICE_TYPE = (
        ('I', _('Import')),
        ('V', _('Vente TFZ'))
    )

    customer = models.ForeignKey(Customer, on_delete=models.PROTECT)

    save_by = models.ForeignKey(User, on_delete=models.PROTECT)

    invoice_date_time = models.DateTimeField(auto_now_add=True)

    total = models.DecimalField(max_digits=10000, decimal_places=2)

    last_updated_date = models.DateTimeField(null=True, blank=True)

    paid  = models.BooleanField(default=False)

    invoice_type = models.CharField(max_length=1, choices=INVOICE_TYPE)

    comments = models.TextField(null=True, max_length=1000, blank=True)

    invoice_number = models.PositiveIntegerField(
        unique=True,
        null=True,
        blank=True,
        validators=[MaxValueValidator(999999)] )
    
    order_number= models.CharField(default='',max_length=200000000)

    remorque_number=models.CharField(default='',max_length=1000)

    total_nbre_gb = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_poid_kg = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    class Meta:
        verbose_name = "Invoice"
        verbose_name_plural = "Invoices"

    def __str__(self):
           return f"{self.customer.name}_{self.invoice_date_time}"

    @property
    def get_total(self):
        articles = self.article_set.all()   
        total = sum(article.total for article in self.article_set.all())
        return total 
    
   
    
    def get_total_nbre_gb(self):
        total_nbre_gb = self.total_nbre_gb
        return total_nbre_gb

    def get_total_weight(self):
        total_weight = self.total_poid_kg
        return total_weight
    

class Commande(models.Model):
     """
    Name: Commande model definiton
    Descripiton: 
    Author: elidrissisiham2@gmail.com
    """
     customer = models.ForeignKey(Customer, on_delete=models.PROTECT)
     save_by = models.ForeignKey(User, on_delete=models.PROTECT)
     commande_date_time = models.DateTimeField(auto_now_add=True)

     

     last_updated_date = models.DateTimeField(null=True, blank=True)
     commande_number = models.PositiveIntegerField(
        unique=True,
        null=True,
        blank=True,
        validators=[MaxValueValidator(999999)] )
     
     ref = models.CharField(default='',max_length=200000000)
     designation = models.CharField(default='',max_length=200000000)
     Qt = models.IntegerField(default=0)
     Prix = models.DecimalField(max_digits=100, decimal_places=2, default=0)
     Montant_HT= models.DecimalField(max_digits=100, decimal_places=2, default=0)
     Total_HT = models.DecimalField(max_digits=100, decimal_places=2, default=0)
     Total_TTC= models.DecimalField(max_digits=100, decimal_places=2, default=0)
     Poids= models.DecimalField(max_digits=100, decimal_places=2, default=0)

     class Meta: 
        verbose_name = "Commande"
        verbose_name_plural = "Commandes"

     def __str__(self):
           return f"{self.customer.name}_{self.commande_date_time}"
     
     @property
     def get_Montant(self):
        Montant_HT = self.Poids* self.Qt * self.Prix  
        return Montant_HT
     
     @classmethod
     def get_totalHT(cls):
        Total_HT = cls.objects.aggregate(total=models.Sum('Montant_HT'))['total'] or 0
        return Total_HT
     
     @classmethod
     def get_totalTTC(cls):
        Total_TTC = cls.objects.aggregate(total=models.Sum('Montant_HT'))['total'] or 0
        return Total_TTC
     
     def delete(self, *args, **kwargs):
        # Delete related CommandeItem objects
        self.commandeitem_set.all().delete()
        # Call the delete method of the superclass to delete the Commande instance
        super().delete(*args, **kwargs)
     

class CommandeItem(models.Model):

    customer = models.ForeignKey(Customer, on_delete=models.PROTECT,null=True, blank=True)
    commande = models.ForeignKey(Commande, on_delete=models.PROTECT, null=True, blank=True)

    ref = models.CharField(default='',max_length=200000000)
    designation = models.CharField(default='',max_length=200000000)
    Qt = models.IntegerField(default=0)
    Prix = models.DecimalField(max_digits=100, decimal_places=2, default=0)
    Poids= models.DecimalField(max_digits=100, decimal_places=2, default=0)
    Montant_HT= models.DecimalField(max_digits=100, decimal_places=2, default=0)

    def get_Montant(self):
        Montant_HT = self.Poids* self.Qt * self.Prix  
        return Montant_HT


    class Meta:
        verbose_name = 'CommandeItem'
        verbose_name_plural = 'CommandeItems'
   









     



class Article(models.Model):
    """
    Name: Article model definiton
    Descripiton: 
    Author: elidrissisiham2@gmail.com
    """

    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE)

    name = models.CharField(max_length=32)
    nbre_GB= models.IntegerField(default=0)


    quantity = models.IntegerField()

    unit_price = models.DecimalField(max_digits=1000000000, decimal_places=2)

    total = models.DecimalField(max_digits=1000000000, decimal_places=2)

    order_number = models.CharField(default='', max_length=20000000) #colis
    remorque_number = models.CharField(default='', max_length=10000000)


   

    class Meta:
        verbose_name = 'Article'
        verbose_name_plural = 'Articles'

    @property
    def get_total(self):
        total = self.quantity * self.unit_price   
        return total 
    
        