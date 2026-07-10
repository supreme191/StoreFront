from django.shortcuts import get_object_or_404, render
from django.http import HttpResponse
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Count
from .models import Product, Collection
from . import serializers

# Create your views here.
@api_view(['GET', 'PUT', 'DELETE'])
def product_detail(request, id) :
    product = get_object_or_404(Product, pk = id)
    if request.method == 'GET' :
        serializer = serializers.ProductSerializer(product)
        return Response(serializer.data)

    elif request.method == 'PUT' :
        serializer = serializers.ProductSerializer(product, data= request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    elif request.method == 'DELETE' :
        if product.orderitem_set.count() > 0 :
            return Response({'error' : 'Cannot delete this product.'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)
        product.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(['GET', 'POST'])
def product_list(request) :
    if request.method == 'GET' :
        products = Product.objects.select_related('collection').all()
        serializer = serializers.ProductSerializer(products, many=True, context={'request' : request})
        return Response(serializer.data)

    elif request.method == 'POST' :
        serializer = serializers.ProductSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

        
@api_view(['GET', 'POST', 'DELETE'])
def collection_detail(request, pk) :
    collection = get_object_or_404(
        Collection.objects.annotate(
            product_count = Count('products')
        ), pk = pk
    )

    if request.method == 'GET' :
        serializer = serializers.CollectionSerializer(collection)
        return Response(serializer.data)
    elif request.method == 'POST' :
        serializer = serializers.CollectionSerializer(collection, data= request.data)
        serializer.is_valid(raise_exception= True)
        serializer.save()
        return Response(status=status.HTTP_201_CREATED)
    elif request.method == 'DELETE' :
        if collection.products.count() > 0 :
            return Response({'error' : 'Collection cannot be deleted'}, status=status.HTTP_409_CONFLICT)
        collection.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    

@api_view(['GET', 'POST'])
def collection_list(request) :
    if request.method == 'GET' :
        collections = Collection.objects.annotate(product_count= Count('products')).all()
        serializer = serializers.CollectionSerializer(collections, many=True)
        return Response(serializer.data)
    
    elif request.method == 'POST' :
        serializer = serializers.CollectionSerializer(data= request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(status=status.HTTP_201_CREATED)