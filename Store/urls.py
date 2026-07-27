from django.urls import path
from . import views
from rest_framework.routers import SimpleRouter
from rest_framework_nested import routers

router = routers.DefaultRouter()
router.register('products', views.ProductViewSet, basename='products')
router.register('collections', views.CollectionViewSet)
router.register('cart', views.CartViewSet, basename='cart')
router.register('customer', views.CustomerViewSet)
router.register('orders', viewset=views.OrderViewSet, basename='orders')

products_router = routers.NestedDefaultRouter(router, 'products', lookup='product')
products_router.register('reviews', views.ReviewViewSet, basename='product-reviews')
products_router.register('images', views.ProductImageViewSet, basename= 'product-images')

cart_router = routers.NestedDefaultRouter(router, 'cart', lookup= 'cart')
cart_router.register('items', views.CartItemViewSet, basename= 'cart-items')

urlpatterns = router.urls + products_router.urls + cart_router.urls
