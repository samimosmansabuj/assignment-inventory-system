from core.audit import audit_log
from reservations.services import fulfill_reservation

ORDER_STATE_TRANSITIONS = {
    "pending": ["confirmed", "cancelled"],
    "confirmed": ["processing", "cancelled"],
    "processing": ["shipped"],
    "shipped": ["delivered"],
    "delivered": set(),
    "cancelled": set(),
}

def transition_order(order, new_status):
    print("new status: ", ORDER_STATE_TRANSITIONS[order.status])
    if new_status not in ORDER_STATE_TRANSITIONS[order.status]:
        raise ValueError("Invalid transition")
    old = order.status
    if old == "pending":
        reservation = order.reservation_set.filter(is_active=True).first()
        if not reservation:
            raise ValueError("No active reservation found for this order")
        if reservation.is_expired:
            raise ValueError("Reservation has expired")

        fulfill_reservation(reservation.id, actor="system")
    
    order.status = new_status
    order.save()

    audit_log(
        "system",
        "ORDER_STATUS_CHANGED",
        order,
        old_value={"status": old},
        new_value={"status": new_status},
    )
