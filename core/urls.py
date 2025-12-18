from django.urls import path, include
from .views import OrderCreateAPI, OrderTransitionAPI, ProductAPIViews, OrderAPIViews
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r"product", ProductAPIViews, basename="product")
router.register(r"order", OrderAPIViews, basename="order")


urlpatterns = [
    path('create-order/', OrderCreateAPI.as_view()),
    path('orders/<int:pk>/transition/', OrderTransitionAPI.as_view()),
    
    
    path('', include(router.urls)),
]