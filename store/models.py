import uuid
from django.db import models
from django.db.models import Q
from django.core.validators import MinValueValidator

class Customer(models.Model):
    name = models.CharField(max_length=150)
    email = models.EmailField(unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    def __str__(self): return self.email

class Book(models.Model):
    title = models.CharField(max_length=240)
    author = models.CharField(max_length=300)
    category = models.CharField(max_length=80)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    cover_url = models.URLField(blank=True)
    is_active = models.BooleanField(default=True)
    class Meta:
        ordering = ['title']
        constraints = [models.CheckConstraint(condition=Q(price__gte=0), name='book_price_nonnegative')]
    def __str__(self): return self.title

class SalesOrder(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.PROTECT)
    order_number = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    customer_name = models.CharField(max_length=150)
    customer_email = models.EmailField()
    total_amount = models.DecimalField(max_digits=12, decimal_places=2)
    status = models.CharField(max_length=20, default='confirmed', choices=[('confirmed','Confirmed'),('cancelled','Cancelled')])
    checkout_key = models.UUIDField(unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    def __str__(self): return str(self.order_number)

class OrderItem(models.Model):
    order = models.ForeignKey(SalesOrder, related_name='items', on_delete=models.CASCADE)
    book = models.ForeignKey(Book, on_delete=models.PROTECT)
    book_title = models.CharField(max_length=240)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    class Meta:
        constraints = [models.UniqueConstraint(fields=['order','book'],name='one_book_per_order')]

class EmailDelivery(models.Model):
    order = models.ForeignKey(SalesOrder, related_name='deliveries', on_delete=models.CASCADE)
    recipient_email = models.EmailField()
    attachment_name = models.CharField(max_length=200)
    status = models.CharField(max_length=20, default='pending', choices=[('pending','Pending'),('sent','Sent'),('failed','Failed')])
    attempt_count = models.PositiveIntegerField(default=0)
    last_error = models.TextField(blank=True)
    sent_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
