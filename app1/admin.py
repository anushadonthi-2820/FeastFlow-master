from django.contrib import admin
from app1.models import Cart, Fooditem, Order

# Register your models here.

admin.site.register(Fooditem)
admin.site.register(Cart)
@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ("id", "usern", "item", "quantity", "payment_method", "payment_status", "transaction_id", "razorpay_order_id", "created_at")
    list_filter = ("payment_method", "payment_status", "created_at")
    search_fields = ("usern__username", "transaction_id", "phno", "addr")
