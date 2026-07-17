from django.db import models
from uuid import uuid4

# Create your models here.
class Promotions(models.Model) :
    description = models.TextField(max_length=255)
    discount = models.FloatField()

    def __str__(self) -> str :
        return self.description


class Collection(models.Model) :
    title = models.CharField(max_length=255)
    featured_product = models.ForeignKey('Product', on_delete=models.SET_NULL, null=True, related_name='+')

    def __str__(self) -> str :
        return self.title
    
    class Meta :
        ordering = ['title']


class Product(models.Model) :
    title = models.CharField(max_length=255)
    slug = models.SlugField(default='-')
    description = models.TextField()
    price = models.DecimalField(max_digits=6, decimal_places=2)
    inventory = models.IntegerField()
    last_update = models.DateTimeField(auto_now=True)
    collection = models.ForeignKey(Collection, on_delete=models.PROTECT, related_name='products')
    promotions = models.ManyToManyField(Promotions)

    def __str__(self) -> str :
        return self.title
    
    class Meta :
        ordering = ['title']


class Customer(models.Model) :
    BRONZE_MEMBERSHIP = "B"
    GOLD_MEMBERSHIP = "G"
    PLATINUM_MEMBERSHIP = "P"

    MEMBERSHIP_CHOICES = [
        (BRONZE_MEMBERSHIP, "Bronze"),
        (GOLD_MEMBERSHIP, "Gold"),
        (PLATINUM_MEMBERSHIP, "Platinum"),
    ]

    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=10)
    birthdate = models.DateField(null=True)
    membership = models.CharField(max_length=1, choices=MEMBERSHIP_CHOICES, default=BRONZE_MEMBERSHIP)

    def __str__(self) -> str :
        return f'{self.first_name} {self.last_name}'

class Address(models.Model) :
    street = models.CharField(max_length=255)
    city = models.CharField(max_length=255)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    zip = models.CharField(max_length=6)


class Orders(models.Model) :
    PAYMENT_PENDING = "P"
    PAYMENT_COMPLETE = "C"
    PAYMENT_FAILED = "F"

    PAYMNET_STATUS = [
        (PAYMENT_PENDING, 'Pending'),
        (PAYMENT_COMPLETE, 'Complete'),
        (PAYMENT_FAILED, 'Failed')
    ]

    placed_at = models.DateTimeField(auto_now_add=True)
    payment_status = models.CharField(max_length=1, choices=PAYMNET_STATUS, default=PAYMENT_PENDING)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)


class OrderItem(models.Model) :
    order=models.ForeignKey(Orders, on_delete=models.PROTECT)
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    qunatity = models.PositiveSmallIntegerField()
    unit_price = models.DecimalField(max_digits=6, decimal_places=2)


class Cart(models.Model) :
    id = models.UUIDField(primary_key=True, default=uuid4)
    created_at = models.DateTimeField(auto_now_add=True)

class CartItem(models.Model) :
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveSmallIntegerField()

    class Meta :
        unique_together = [['cart', 'product']]


class Review(models.Model) :
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='reviews')
    name = models.CharField(max_length=255)
    description = models.TextField()
    date = models.DateField(auto_now=True)