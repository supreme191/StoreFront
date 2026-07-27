from decimal import Decimal
from django.db import transaction
from Store.models import OrderItem, Product, Collection, Review, Cart, CartItem, Customer, Orders, ProductImage
from rest_framework import serializers

from .signals import order_created


class CollectionSerializer(serializers.ModelSerializer) :
    product_count = serializers.IntegerField(read_only= True)
    class Meta :
        model = Collection
        fields = ['id', 'title', 'product_count']


class ReviewSerializer(serializers.ModelSerializer) :
    class Meta :
        model = Review
        fields = ['id', 'name', 'description', 'date']

    def create(self, validated_data):
        product_id = self.context['product_id']
        return Review.objects.create(product_id=product_id, **validated_data)


class ProductImageSerializer(serializers.ModelSerializer) :
    def create(self, validated_data):
        product_id = self.context['product_id']
        return ProductImage.objects.create(product_id= product_id, **validated_data)

    class Meta :
        model = ProductImage
        fields = ['id', 'image']


class ProductSerializer(serializers.ModelSerializer) :
    images = ProductImageSerializer(many= True, read_only= True)
    price_after_tax = serializers.SerializerMethodField(method_name='calculate_tax')
    collection = serializers.PrimaryKeyRelatedField(
        queryset= Collection.objects.all())

    class Meta :
        model = Product
        fields = ["id", "title", "description", "slug", "inventory", "price", "price_after_tax", "collection", "images"]


    def calculate_tax(self, product : Product) :
        return product.price * Decimal(1.1)
    

class SimpleProductSerializer(serializers.ModelSerializer) :
    class Meta :
        model = Product
        fields = ['id', 'title', 'price']


class CartItemSerializer(serializers.ModelSerializer) :
    product = SimpleProductSerializer()
    total_price = serializers.SerializerMethodField(method_name='get_total_price')

    def get_total_price(self, cart_item:CartItem) :
        return cart_item.quantity * cart_item.product.price

    class Meta :
        model = CartItem
        fields = ['id', 'product', 'quantity', 'total_price']


class CartSerializer(serializers.ModelSerializer) :
    id = serializers.UUIDField(read_only= True)
    items = CartItemSerializer(many= True, read_only = True)
    total = serializers.SerializerMethodField(method_name='get_total')

    def get_total(self, cart: Cart) :
        return sum([item.quantity * item.product.price for item in cart.items.all()])

    class Meta :
        model = Cart
        fields = ['id', 'items', 'total']


class AddItemSerializer(serializers.ModelSerializer) :
    product_id = serializers.IntegerField()

    def validate_product_id(self, value) :
        if not Product.objects.filter(pk= value).exists() :
            raise serializers.ValidationError("Invalid Product Id")
        return value

    def save(self, **kwargs):
        cart_id = self.context['cart_id']
        product_id = self.validated_data['product_id']
        quantity = self.validated_data['quantity']

        try :
            cart_item = CartItem.objects.get(cart_id= cart_id, product_id= product_id)
            cart_item.quantity += quantity
            cart_item.save()
            self.instance = cart_item
        
        except CartItem.DoesNotExist :
            self.instance = CartItem.objects.create(cart_id= cart_id, product_id= product_id, quantity= quantity)
        
        return self.instance

    class Meta :
        model = CartItem
        fields = ['id', 'product_id', 'quantity']


class UpdateItemSerializer(serializers.ModelSerializer) :
    class Meta :
        model = CartItem
        fields = ['quantity']


class CustomerSerializer(serializers.ModelSerializer) :
    user_id = serializers.IntegerField(read_only= True)
    class Meta :
        model = Customer
        fields = ['id', 'user_id', 'phone', 'birthdate', 'membership']


class OrderItemSerializer(serializers.ModelSerializer) :
    product = SimpleProductSerializer()
    class Meta :
        model = OrderItem
        fields = ['id', 'product', 'unit_price', 'qunatity']



class OrderSerializer(serializers.ModelSerializer) :
    orderitems = OrderItemSerializer(many= True)
    class Meta :
        model = Orders
        fields = ['id', 'customer', 'placed_at', 'payment_status', 'orderitems']



class CreateOrderSerializer(serializers.Serializer) :
    cart_id = serializers.UUIDField()

    def validate_cart_id(self, cart_id) :
        if not Cart.objects.filter(pk= cart_id).exists() :
            raise serializers.ValidationError('No cart with the given Id exists.')
        if CartItem.objects.filter(cart_id= cart_id).count() == 0 :
            raise serializers.ValidationError('THe cart is Empty.')
        return cart_id

    def save(self, **kwargs):
        with transaction.atomic() :
            customer = Customer.objects.get(user_id= self.context['user_id'])
            order = Orders.objects.create(customer= customer)

            cart_items = CartItem.objects \
                                .select_related('product') \
                                .filter(cart_id= self.validated_data['cart_id'])

            order_items = [
                OrderItem(
                    order= order,
                    product= item.product,
                    unit_price= item.product.price,
                    qunatity= item.quantity
                ) 
                for item in cart_items
            ]

            OrderItem.objects.bulk_create(order_items)
            Cart.objects.filter(pk= self.validated_data['cart_id']).delete()
            order_created.send_robust(self.__class__, order= order)
            return order



class UpdateOrderSerializer(serializers.ModelSerializer) :
    class Meta :
        model = Orders
        fields = ['payment_status']