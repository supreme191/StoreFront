from rest_framework.response import Response
from rest_framework import status
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.viewsets import ModelViewSet, GenericViewSet
from rest_framework.mixins import CreateModelMixin, RetrieveModelMixin, DestroyModelMixin
from django.db.models import Count

from Store.filters import ProductFilter
from .models import OrderItem, Product, Collection, Review, Cart, CartItem
from . import serializers
from .pagination import DefaultPagination


class ProductViewSet(ModelViewSet) :
    queryset = Product.objects.all()
    serializer_class = serializers.ProductSerializer

    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = ProductFilter
    pagination_class = DefaultPagination
    search_fields = ['title', 'description']
    ordering_fields = ['price', 'last_update']

    def get_serializer_context(self):
        return {'request' : self.request}

    def destroy(self, request, *args, **kwargs):
        if OrderItem.objects.filter(product_id=kwargs['pk']).count() > 0 :
            return Response({'error' : 'Cannot delete this product.'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)
        return super().destroy(request, *args, **kwargs)
    
    

class CollectionViewSet(ModelViewSet) :
    queryset = Collection.objects.annotate(product_count= Count('products')).all()
    serializer_class = serializers.CollectionSerializer
    
    def get_serializer_context(self):
        return {'request' : self.request}

    def destroy(self, request, *args, **kwargs):
        if Collection.objects.filter(pk=kwargs['pk']).count() > 0 :
            return Response({'error' : 'Collection cannot be deleted'}, status=status.HTTP_409_CONFLICT)
        return super().destroy(request, *args, **kwargs)



class ReviewViewSet(ModelViewSet) :
    serializer_class = serializers.ReviewSerializer

    def get_queryset(self):
        return Review.objects.filter(product_id=self.kwargs['product_pk'])

    def get_serializer_context(self):
        return {'product_id' : self.kwargs['product_pk']}
    


class CartViewSet(
    CreateModelMixin,
    RetrieveModelMixin,
    DestroyModelMixin,
    GenericViewSet
) :
    queryset = Cart.objects.prefetch_related('items__product').all()
    serializer_class = serializers.CartSerializer



class CartItemViewSet(ModelViewSet) :
    http_method_names = ['get', 'post', 'patch', 'delete']

    def get_serializer_class(self):
        if self.request.method == 'GET' :
            return serializers.CartItemSerializer
        elif self.request.method == 'POST' :
            return serializers.AddItemSerializer
        elif self.request.method == 'PATCH' :
            return serializers.UpdateItemSerializer

    def get_queryset(self):
        return CartItem.objects.filter(cart_id= self.kwargs['cart_pk']).select_related('product')
    
    def get_serializer_context(self):
        return {'cart_id' : self.kwargs['cart_pk']}