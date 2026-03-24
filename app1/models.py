from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

# Create your models here.

class Fooditem(models.Model):
    
    itempic = models.ImageField(upload_to="images")
    itemname = models.CharField(max_length=100)
    price = models.FloatField()
    itemtype = models.CharField(max_length=100)
    rating = models.FloatField()
    availability = models.BooleanField()
    
    def __str__(self) -> str:
        return self.itemname
    
    
    
class Cart(models.Model):
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    item = models.ForeignKey("Fooditem", on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    
    def __str__(self) -> str:
        return f"{self.item.itemname} x {self.quantity}"
    
    
    
class Order(models.Model):
    PAYMENT_METHODS = [
        ("online", "Online"),
        ("cod", "Cash on Delivery"),
    ]
    PAYMENT_STATUSES = [
        ("paid", "Paid"),
        ("pending", "Pending"),
    ]
    
    usern = models.ForeignKey("auth.User", on_delete=models.CASCADE)
    items = models.ForeignKey("Cart", on_delete=models.SET_NULL, null=True, blank=True)
    item = models.ForeignKey("Fooditem", on_delete=models.SET_NULL, null=True, blank=True)
    quantity = models.PositiveIntegerField(default=1)
    price_at_purchase = models.FloatField(default=0)
    addr = models.TextField()
    phno = models.CharField(max_length=10)
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHODS, default="online")
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUSES, default="paid")
    transaction_id = models.CharField(max_length=100, blank=True)
    razorpay_order_id = models.CharField(max_length=100, blank=True)
    razorpay_signature = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    
    def __str__(self) -> str:
        return str(self.id)
