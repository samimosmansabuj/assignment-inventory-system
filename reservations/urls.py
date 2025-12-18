from django.urls import path
from .views import ReservationCreateAPI


urlpatterns = [
    path('reservations/', ReservationCreateAPI.as_view()),
]