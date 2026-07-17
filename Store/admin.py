from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html, urlencode
from django.contrib.contenttypes.admin import GenericTabularInline

from Tags.models import TaggedItem
from . import models
from django.db.models.aggregates import Count
from django.contrib import admin



class InventoryFilter(admin.SimpleListFilter):
    title = "Inventory"
    parameter_name = "inventory"

    def lookups(self, request, model_admin):
        return [
            ("<60", "Low Stock"),
            (">=60", "In Stock"),
        ]

    def queryset(self, request, queryset):
        if self.value() == "<60":
            return queryset.filter(inventory__lt=60)

        if self.value() == ">=60":
            return queryset.filter(inventory__gte=60)

        return queryset
    

class TagInline(GenericTabularInline) :
    model = TaggedItem
    autocomplete_fields = ['tag']


@admin.register(models.Product)
class ProductAdmin(admin.ModelAdmin) :
    inlines = [TagInline]
    list_display = ['title', 'price', 'collection_title', 'inventory_status']
    list_per_page = 20
    list_editable = ['price']
    list_filter = ['collection', InventoryFilter]
    
    list_select_related = ['collection']
    def collection_title(self, obj) :
        return obj.collection.title

    def inventory_status(self, product) :
        return 'Low' if product.inventory < 60 else "OK"


@admin.register(models.Customer)
class CustomerAdmin(admin.ModelAdmin) :
    list_display = ['name', 'membership']
    list_editable = ['membership']
    list_select_related = ['user']
    ordering = ['user__first_name', 'user__last_name']
    list_per_page = 10

    @admin.display(ordering='user__first_name')
    def name(self, customer) :
        return (f'{customer.user.first_name} {customer.user.last_name}')

    
@admin.register(models.Orders)
class OrderAdmin(admin.ModelAdmin) :
    list_display = ['id', 'placed_at', 'customer_']
    list_select_related = ['customer']

    def customer_(self, order) :
        url = (
            reverse('admin:Store_orders_changelist')
            + '?'
            + urlencode({
                'customer__id' : str(order.customer.id)
            })
        )

        return format_html('<a href="{}">{}</a>', url, order.customer)


@admin.register(models.Collection)
class CollectionAdmin(admin.ModelAdmin) :
    list_display = ['title', 'product_count']

    @admin.display(ordering='product_count')
    def product_count(self, collection) -> int :
        return collection.product_count
    
    def get_queryset(self, request):
        return super().get_queryset(request).annotate(
            product_count = Count('products')
        )