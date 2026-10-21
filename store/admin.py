from django.contrib import admin
from .models import Book, Customer, SalesOrder, OrderItem, EmailDelivery
from .services import send_delivery
@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ['title','author','category','price','is_active']
    list_filter = ['category','is_active']
    search_fields = ['title','author']
class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ['book','book_title','unit_price']
    can_delete = False
    def has_add_permission(self,request,obj=None): return False
@admin.register(SalesOrder)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['order_number','customer_email','total_amount','status','created_at']
    readonly_fields = ['customer','order_number','customer_name','customer_email','total_amount','status','checkout_key','created_at']
    inlines = [OrderItemInline]
    def has_add_permission(self,request): return False
    def has_delete_permission(self,request,obj=None): return False
@admin.action(description='Retry pending or failed email deliveries')
def retry_email(modeladmin,request,queryset):
    for delivery in queryset.exclude(status='sent'): send_delivery(delivery.pk)
@admin.register(EmailDelivery)
class EmailAdmin(admin.ModelAdmin):
    list_display = ['order','recipient_email','status','attempt_count','sent_at']
    list_filter = ['status']
    readonly_fields = [f.name for f in EmailDelivery._meta.fields]
    actions = [retry_email]
    def has_add_permission(self,request): return False
    def has_delete_permission(self,request,obj=None): return False
@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ['name','email','created_at']
    search_fields = ['name','email']
admin.site.site_header = 'Leaf & Lore · Administration'
