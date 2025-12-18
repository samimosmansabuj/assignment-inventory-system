import threading
import os
import sys
import django

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "inventory_system_assignment.settings")
django.setup()

from reservations.services import create_reservation
from core.models import Product
from django.db import transaction
from threading import Lock

success = 0
fail = 0
lock = Lock()

def run():
    global success, fail
    try:
        with lock:
            create_reservation(4, 1, "chaos")
            success += 1
    except:
        with lock:
            fail += 1

threads = [threading.Thread(target=run) for _ in range(50)]
[t.start() for t in threads]
[t.join() for t in threads]


print("------ CHAOS TEST RESULT ------")
print("Success:", success)
print("Fail:", fail)

