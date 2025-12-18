from django.test import TransactionTestCase
from threading import Thread
from reservations.services import create_reservation
from core.models import Product
from django.db import transaction
from threading import Lock

lock = Lock()

class InventoryReservedChaosTest(TransactionTestCase):
    reset_sequences = True

    def setUp(self):
        self.product = Product.objects.create(
            name="ChaosProduct",
            total_stock=20,
            available_stock=20,
            reserved_stock=0,
            price=100,
        )
        self.success = 0
        self.failed = 0

    def attempt_reservation(self):
        try:
            with lock:
                with transaction.atomic():
                    create_reservation(self.product.id, 1, "chaos_test")
                self.success += 1
        except:
            with lock:
                self.failed += 1

    def test_parallel_reservations(self):
        threads = [Thread(target=self.attempt_reservation) for _ in range(50)]

        for t in threads:
            t.start()
        for t in threads:
            t.join()

        self.product.refresh_from_db()
        print("--- Chaos Test Results ---")
        print("Succeeded:", self.success)
        print("Failed:", self.failed)
