from celery import shared_task
from django.utils import timezone
from .models import Reservation
from django.db import transaction
from datetime import datetime
from core.audit import audit_log


@shared_task
def clean_expired_reservations():
    expired_reservations = Reservation.objects.filter(
        expires_at__lt=datetime.now(), is_active=True
    )
    for reservation in expired_reservations:
        with transaction.atomic():
            product = reservation.product
            product.available_stock += reservation.quantity
            product.reserved_stock -= reservation.quantity
            product.save()
            reservation.is_active = False
            reservation.save()
    return f"{expired.count()} reservations released"


@shared_task
def release_expired_reservations():
    expired_reservations = Reservation.objects.select_for_update().filter(
        is_active=True, expires_at__lt=timezone.now()
    )
    for reservation in expired_reservations:
        with transaction.atomic():
            product = reservation.product
            
            product.available_stock += reservation.quantity
            product.reserved_stock -= reservation.quantity
            product.save()
            
            reservation.is_active = False
            reservation.save()
            
            if reservation.order and reservation.order.status == "pending":
                reservation.order.status = "cancelled"
                reservation.order.save()
            
            audit_log(actor='system', action='RESERVATION_EXPIRED_CLEANUP', obj=reservation,)
    return f"Released {expired_reservations.count()} expired reservations."