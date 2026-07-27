from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import action
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.viewsets import ModelViewSet, GenericViewSet
from rest_framework.mixins import CreateModelMixin, RetrieveModelMixin, DestroyModelMixin, UpdateModelMixin
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from django.db.models import Count

from .filters import ProductFilter
from .permissions import IsAdminOrReadOnly, ViewCustomerHistoryPermission
from .models import OrderItem, Product, Collection, ProductImage, Review, Cart, CartItem, Customer, Orders
from . import serializers
from .pagination import DefaultPagination


class ProductViewSet(ModelViewSet) :
    queryset = Product.objects.prefetch_related('images').all()
    serializer_class = serializers.ProductSerializer

    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = ProductFilter
    pagination_class = DefaultPagination
    search_fields = ['title', 'description']
    ordering_fields = ['price', 'last_update']

    permission_classes = [IsAdminOrReadOnly]

    def get_serializer_context(self):
        return {'request' : self.request}

    def destroy(self, request, *args, **kwargs):
        if OrderItem.objects.filter(product_id=kwargs['pk']).count() > 0 :
            return Response({'error' : 'Cannot delete this product.'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)
        return super().destroy(request, *args, **kwargs)
    
    

class CollectionViewSet(ModelViewSet) :
    queryset = Collection.objects.annotate(product_count= Count('products')).all()
    serializer_class = serializers.CollectionSerializer
    permission_classes = [IsAdminOrReadOnly]
    
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
    


class CustomerViewSet(ModelViewSet) :
    queryset = Customer.objects.all()
    serializer_class = serializers.CustomerSerializer
    permission_classes = [IsAdminUser]

    @action(detail= True, permission_classes= [ViewCustomerHistoryPermission])
    def history(self, request, pk) :
        return Response('Ok')

    @action(detail=False, methods=['GET', 'PUT'], permission_classes= [IsAuthenticated])
    def me(self, request) :
        (customer, _) = Customer.objects.get(user_id= request.user.id)

        if request.method == 'GET' :
            serializer = serializers.CustomerSerializer(customer)
            return Response(serializer.data)
        
        elif request.method == 'PUT' :
            serializer = serializers.CustomerSerializer(customer, data= request.data)
            serializer.is_valid(raise_exception= True)
            serializer.save()
            return Response(serializer.data)
        


class OrderViewSet(ModelViewSet) :
    http_method_names = ['get', 'post', 'patch', 'delete', 'head', 'options']
    def get_permissions(self):
        if self.request.method in ['PATCH', 'DELETE'] :
            return [IsAdminUser()]
        return [IsAuthenticated()]

    def create(self, request, *args, **kwargs):
        serializer = serializers.CreateOrderSerializer(
            data= request.data,
            context= {'user_id' : self.request.user.id}
        )
        serializer.is_valid(raise_exception=True)
        order = serializer.save()
        serializer = serializers.OrderSerializer(order)
        return Response(serializer.data)

    def get_queryset(self):
        user = self.request.user
        if user.is_staff : return Orders.objects.all()

        customer_id = Customer.objects.only('id').get(user_id= user.id)
        return Orders.objects.filter(customer_id= customer_id)

    def get_serializer_class(self) :
        if self.request.method == 'POST' :
            return serializers.CreateOrderSerializer
        elif self.request.method == 'PATCH' :
            return serializers.UpdateOrderSerializer
        return serializers.OrderSerializer



class ProductImageViewSet(ModelViewSet) :
    serializer_class = serializers.ProductImageSerializer

    def get_serializer_context(self):
        return {'product_id' : self.kwargs['product_pk']}

    def get_queryset(self):
        return ProductImage.objects.filter(product_id= self.kwargs['product_pk'])