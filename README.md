# Inventory Reservation and Order Management System

## Project Overview
This Django-based project implements an **Inventory Reservation Management System**.  
It handles:
- Product inventory with `available_stock` and `reserved_stock`
- Reservation management with automatic expiration
- Order state transitions via a **state machine**
- Concurrency-safe reservations
- Audit logging for key actions
- Optimized queries for performance

---

## Table of Contents
1. [Architecture](#architecture)  
2. [Models](#models)  
3. [Services](#services)  
4. [API Endpoints](#api-endpoints)  
5. [Concurrency Handling](#concurrency-handling)  
6. [Reservation Cleanup](#reservation-cleanup)  
7. [Order State Machine](#order-state-machine)  
8. [Audit Logging](#audit-logging)  
9. [Performance Optimization](#performance-optimization)  
10. [Testing](#testing)  

---

## Architecture
<img width="367" height="397" alt="work flow diagram" src="https://github.com/user-attachments/assets/61a82435-3a39-4daa-aba9-8a716b50d435" />

### Explanation:
1. **User/API** sends a request to create a reservation or order.  
2. **DB Transaction (select_for_update)** ensures stock updates are concurrency-safe.  
3. **Reservation Handling**:
   - On success: `reserved_stock` is updated and reservation becomes active.  
   - On expiration (via cron or Celery): reserved stock is released back to `available_stock` and reservation is marked inactive.  
4. **Order Fulfillment**:
   - When order is confirmed, the reservation is fulfilled.  
   - `reserved_stock` is deducted from `total_stock`.  
5. **Audit Logging**: Every action (create, expire, fulfill) is logged in the `AuditLog` table for traceability.

---

## Models

### Product
- `total_stock`, `available_stock`, `reserved_stock`, `price`
- Invariant: `available_stock + reserved_stock = total_stock`

### Order
- `status`, `quantity`, `total`, `product`
- Indexed fields: `created_at`, `status`, `total`

### Reservation
- `quantity`, `expires_at`, `is_active`, `confirm`, `order`

### AuditLog
- Records `actor`, `action`, `object_type`, `object_id`, `old_value`, `new_value`, `timestamp`

---

## Services

- `create_reservation(product_id, qty, actor)`
- `create_order_and_reservation(product_id, qty, actor)`
- `release_reservation(reservation_id, actor)`
- `fulfill_reservation(reservation_id, actor)`
- `transition_order(order, new_status)`

**Highlights:**
- Uses `transaction.atomic()` + `select_for_update()` for safe concurrent updates.
- Raises `ValueError` for invalid state transitions or insufficient stock.
- Logs all changes to `AuditLog`.

---

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/products/` | GET/POST | List/Create products |
| `/api/orders/` | GET | List orders (filter/sort/cursor pagination) |
| `/api/create-order/` | POST | Create order + reservation |
| `/api/orders/{id}/transition/` | POST | Transition order state |
| `/api/reservations/` | POST | Create reservation |

**All API responses include a `request_id` (UUID) for tracing.**

---

## Concurrency Handling

- **DB-level locking:** `select_for_update()` ensures no two reservations reduce stock simultaneously beyond available stock.
- **Atomic transactions:** Ensure stock updates and reservation creation are all-or-nothing.
- **Chaos test:** 50 parallel reservation attempts on a 5-stock product → exactly 5 succeed, remaining fail.

**Example Output:**
- --- Chaos Test Results ---
  Succeeded: 5
  Failed: 45


---

## Reservation Cleanup
- Implemented via **Management Command**: 
```bash
python manage.py clean_expired_reservations
```
Logic:
- Fetch expired reservations (expires_at < now())
- Release reserved stock back to available_stock
- Cancel associated order if present
- Log cleanup in AuditLog

---

## Order State Machine
- Allowed transitions:
```
ORDER_STATE_TRANSITIONS = {
    "pending": ["confirmed", "cancelled"],
    "confirmed": ["processing", "cancelled"],
    "processing": ["shipped"],
    "shipped": ["delivered"],
    "delivered": set(),
    "cancelled": set(),
}
```
Invalid transitions raise errors and are tested. </br>
Dictionary-based transitions avoid if-else complexity.

---

## Audit Logging
- Reservation created, expired, released, fulfilled
- Order created
- Status changed
- Stock adjusted
Sample Entry:
```
{
  "actor": "system",
  "action": "RESERVATION_FULFILLED",
  "object_type": "Reservation",
  "object_id": 1,
  "old_value": {"qty": 1},
  "new_value": {"qty": 1},
  "timestamp": "2025-12-18T23:00:00Z"
}
```

---

## Performance Optimization
**Indexes Added:**  
- `Order.created_at`  
- `Order.status`  
- `Order.total`  

**Query Optimizations:**  
- Used `select_related('product')` to reduce N+1 queries  
- `prefetch_related()` can be applied for reverse relations to optimize queries  

**API Enhancements:**  
- Filtering and sorting supported on the orders endpoint  
- Cursor pagination implemented for efficient retrieval of large datasets  

---

## Testing

**Unit Tests (8–12 tests) cover:**  
- Reservation creation  
- Reservation expiration  
- Concurrency chaos test  

**Run tests:**
```bash
python manage.py test reservations.tests.InventoryReservedChaosTest
```
Chaos Test:
```bash
python reservations/chaos_test.py
```
demonstrates concurrent reservation handling.

---


## Design Questions
This section explains key design decisions for the Inventory Reservation System

### 1. Crash Recovery after Reservation
**Design Choice:**  
- We use database transactions with `select_for_update` locks to ensure atomic updates on inventory and reservations.  
- In case of a crash, incomplete reservations are automatically rolled back by the database.  

**Trade-offs:**  
- Reliable consistency: avoids overbooking  
- Slight performance overhead due to row-level locking  
- Requires careful handling in high-concurrency scenarios  

---

### 2. Cleanup Strategy + Frequency
**Design Choice:**  
- Expired reservations are cleared using a scheduled task (Celery Beat or cron).  
- Frequency: every 1 minute for small-to-medium datasets; scalable with batch processing for large inventories.  

**Trade-offs:**  
- Keeps database clean and prevents stock from being artificially locked  
- Too frequent cleanup may cause unnecessary DB load  
- Too infrequent may block stock availability  

---

### 3. Multi-Warehouse Design Choices
**Design Choice:**  
- Inventory is tracked per warehouse.  
- Orders can reserve stock from a single warehouse or split across multiple warehouses if needed.  

**Trade-offs:**  
- Supports realistic business scenarios with multiple stock locations  
- Enables region-based fulfillment optimization  
- Increased query complexity and joins  
- Requires careful handling of partial reservations  

---

### 4. Caching Strategy
**Design Choice:**  
- Cache frequently accessed data like product details and available stock using Redis or in-memory Django cache.  
- Cache invalidation occurs on inventory changes (reservation creation, expiration, or stock update).  

**Trade-offs:**  
- Reduces database load and improves response time  
- Can serve large-scale read-heavy endpoints efficiently  
- Risk of stale data if invalidation is delayed  
- Adds additional infrastructure dependency  



