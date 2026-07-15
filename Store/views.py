from rest_framework.response import Response
from rest_framework import status
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter
from rest_framework.viewsets import ModelViewSet
from django.db.models import Count

from Store.filters import ProductFilter
from .models import OrderItem, Product, Collection, Review
from . import serializers


class ProductViewSet(ModelViewSet) :
    queryset = Product.objects.all()
    serializer_class = serializers.ProductSerializer

    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_class = ProductFilter
    search_fields = ['title', 'description']

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