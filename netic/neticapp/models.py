from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.conf import settings
import uuid
from neticapp import data
import binascii
import os
from .services import calculated_paid_amount, remaining_amount
# Create your models here.
    
class UserManager(BaseUserManager):
    use_in_migrations = True
    def create_user(self, phone_number, password, **extra_fields):
        user = self.model(phone_number=phone_number, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, phone_number, password, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")
        return self.create_user(phone_number, password, **extra_fields)
    
class User(AbstractUser):
    id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True, primary_key=True)
    username = None
    first_name = None
    last_name = None
    phone_number = models.CharField(max_length=20, null=False, blank=False, unique=True)
    email = models.EmailField(max_length=100, blank=True, null=True)
    name = models.CharField(max_length=100,
                                 verbose_name='Full name',
                                 blank=True,
                                 null=True)
    lat = models.CharField(max_length=50, null=True, blank=True)
    long = models.CharField(max_length=50, null=True, blank=True)
    USERNAME_FIELD = "phone_number"
    objects = UserManager()


class Order(models.Model):
    id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True, primary_key=True)
    order_user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete = models.CASCADE, 
                                   related_name='order_of_user', verbose_name='Order of user')
    reference = models.CharField(max_length=8, null=True, blank=True,  editable=False, unique=True)
    product = models.IntegerField(choices=data.PRODUCTS, null=True, blank=True)
    vehicule = models.IntegerField(choices=data.VEHICULES, null=True, blank=True)
    quantity = models.IntegerField(null=True, blank=True)
    budget = models.FloatField(null=True, blank=True)
    departure_place = models.CharField(max_length=100, null=True, blank=True)
    arrival_place = models.CharField(max_length=100, null=True, blank=True)
    lat_departure_place = models.CharField(max_length=100, null=True, blank=True)
    long_departure_place = models.CharField(max_length=100, null=True, blank=True)
    lat_arrival_place = models.CharField(max_length=100, null=True, blank=True)
    long_arrival_place = models.CharField(max_length=100, null=True, blank=True)
    departure_town_place = models.CharField(max_length=100, null=True, blank=True)
    arrival_town_place = models.CharField(max_length=100, null=True, blank=True)
    devise = models.IntegerField(default=1,choices=data.AVAILABILITY_DEVISES)
    paid_amount = models.FloatField(null=True, blank=True)
    is_paid = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    message = models.CharField(max_length=255, null=True, blank=True)
    accepted = models.ManyToManyField(settings.AUTH_USER_MODEL, through="Jobs")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Order'
        verbose_name_plural = 'Orders'
    def __str__(self):
        return f"Thats is order #{self.reference} of user {self.order_user.phone_number}"
    
    @staticmethod
    def generate_reference():
        return  binascii.hexlify(os.urandom(16)).decode().upper()[0:8]
    
    def save(self, *args, **kwargs):
        if self._state.adding and (not self.reference or 
                                   Order.objects.filter(reference=self.reference).exists()):
            self.reference = self.generate_reference()
        self.paid_amount = calculated_paid_amount(self.devise, self.budget)
        super().save(*args, **kwargs)

class Jobs(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    job_status = models.BooleanField(default=True)
    accepted_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    class Meta:
        verbose_name = 'Job'
        verbose_name_plural = 'Jobs'
        unique_together = ('order', 'job_status')
    def __str__(self):
        return f"This job #{self.order.reference} is doing by {self.user.phone_number}"


class Invoice(models.Model):
    reference = models.CharField(max_length=10, null=True, blank=True,  editable=False, unique=True)
    invoice_user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    amount = models.FloatField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    class Meta:
        verbose_name = 'Invoice'
        verbose_name_plural = 'Invoices'
    def __str__(self):
        return f"This invoice #INV{self.id} belongs to {self.invoice_user.phone_number}"
    @staticmethod
    def generate_reference():
        return  binascii.hexlify(os.urandom(16)).decode().upper()[0:10]
    def save(self, *args, **kwargs):
        if self._state.adding and (not self.reference or 
                                   Invoice.objects.filter(reference=self.reference).exists()):
            self.reference = self.generate_reference()
        super().save(*args, **kwargs)

class Payment(models.Model):
    payment_invoice= models.ForeignKey(Invoice, on_delete=models.CASCADE, related_name = 'payment_info')
    pay_amount = models.FloatField(null=True, blank=True)
    remaining_amount = models.FloatField(null=True, blank=True)
    status = models.IntegerField(default=1, choices=data.INVOICE_STATUS)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    class Meta:
        verbose_name = 'Payment'
        verbose_name_plural = 'Payments'
    def __str__(self):
        return f"#PAY{self.id} belongs to {self.payment_invoice.invoice_user} the status is {self.status} the remaining amount is{self.remaining_amount}"

    def save(self, *args, **kwargs):
        self.remaining_amount = remaining_amount(self.payment_invoice.amount, self.pay_amount)
        if(self.remaining_amount <= 0):
            self.status = 3
        elif(self.remaining_amount<self.payment_invoice.amount):
            self.status = 2
        else:
            self.status = 1
        super().save(*args, **kwargs)
