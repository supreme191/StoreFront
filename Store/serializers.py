from decimal import Decimal
from Store.models import Product, Collection, Review
from rest_framework import serializers


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


class ProductSerializer(serializers.ModelSerializer) :
    price_after_tax = serializers.SerializerMethodField(method_name='calculate_tax')
    collection = serializers.PrimaryKeyRelatedField(
        queryset= Collection.objects.all()
    )

    class Meta :
        model = Product
        fields = ["id", "title", "description", "slug", "inventory", "price", "price_after_tax", "collection"]


    def calculate_tax(self, product : Product) :
        return product.price * Decimal(1.1)