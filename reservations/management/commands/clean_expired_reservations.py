from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils.timezone import now
from reservations.models import Reservation
from core.audit import audit_log

class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        expired_reservations = Reservation.objects.filter(expires_at__lt=now(), is_active=True, confirm=False)
        for reservation in expired_reservations:
            with transaction.atomic():
                product = reservation.product
                product.available_stock += reservation.quantity
                product.reserved_stock -= reservation.quantity
                product.save()
                reservation.is_active = False
                reservation.save()
                
                if reservation.order:
                    reservation.order.status = 'cancelled'
                    reservation.order.save()
                
                audit_log(actor='system', action='RESERVATION_EXPIRED_CLEANUP', obj=reservation,)
                self.stdout.write(self.style.SUCCESS(f"Reservation {reservation.id} cleaned up."))
