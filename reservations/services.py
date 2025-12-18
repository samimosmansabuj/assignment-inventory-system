from django.db import transaction
from django.utils.timezone import now
from datetime import timedelta
from core.models import Product, Order
from .models import Reservation
from core.audit import audit_log

# Manually added code =======
@transaction.atomic
def create_reservation(product_id, qty, actor):
    product = Product.objects.select_for_update().get(id=product_id)
    if product.available_stock < int(qty):
        raise ValueError('Insufficient stock')

    product.available_stock -= int(qty)
    product.reserved_stock += int(qty)
    product.save()
    reservation = Reservation.objects.create(
        product=product,
        quantity=qty,
        expires_at=now() + timedelta(minutes=1)
    )
    audit_log(actor, 'RESERVATION_CREATED', reservation,
    new_value={'qty': qty})
    return reservation

@transaction.atomic
def create_order_and_reservation(product_id, qty, actor=None):
    product = Product.objects.select_for_update().get(id=product_id)
    if product.available_stock < int(qty):
        raise ValueError('Insufficient stock')
    
    order = Order.objects.create(
        product=product,
        quantity=qty
    )

    product.available_stock -= int(qty)
    product.reserved_stock += int(qty)
    product.save()

    reservation = Reservation.objects.create(
        product=product,
        order=order,
        quantity=qty,
        expires_at=now() + timedelta(minutes=1)
    )

    audit_log(
        actor, 'RESERVATION_CREATED', reservation, new_value={'qty': qty}
    )
    audit_log(
        actor, 'ORDER_CREATED', order, new_value={'qty': qty}
    )

    return order

@transaction.atomic
def release_reservation(reservation_id, actor):
    reservation = Reservation.objects.select_for_update().get(id=reservation_id)
    if not reservation.is_active:
        raise ValueError('Reservation already inactive')

    product = reservation.product
    product.available_stock += reservation.quantity
    product.reserved_stock -= reservation.quantity
    product.save()

    reservation.is_active = False
    reservation.save()

    audit_log(actor, 'RESERVATION_RELEASED', reservation,
    new_value={'qty': reservation.quantity})

    return reservation

@transaction.atomic
def fulfill_reservation(reservation_id, actor):
    reservation = Reservation.objects.select_for_update().get(id=reservation_id)
    if not reservation.is_active:
        raise ValueError('Reservation already inactive')

    product = reservation.product
    product.reserved_stock -= reservation.quantity
    product.total_stock -= reservation.quantity
    product.save()

    reservation.is_active = False
    reservation.confirm = True
    reservation.save()

    audit_log(actor, 'RESERVATION_FULFILLED', reservation,
    new_value={'qty': reservation.quantity})

    return reservation

