from django.urls import path, include
from .views import OrderCreateAPI, OrderTransitionAPI, ProductAPIViews
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r"product", ProductAPIViews, basename="product")


urlpatterns = [
    path('orders/', OrderCreateAPI.as_view()),
    path('orders/<int:pk>/transition/', OrderTransitionAPI.as_view()),
    
    
    path('', include(router.urls)),
]