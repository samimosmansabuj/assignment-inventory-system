.PHONY: run migrate test shell clean-expired

setup:
	pip install -r requirements.txt

run:
	python manage.py runserver

migrate:
	python manage.py makemigrations
	python manage.py migrate

test:
	python manage.py test reservations.tests.InventoryReservedChaosTest

chaos-test:
	python scripts/chaos_test.py

shell:
	python manage.py shell

clean-expired:
	python manage.py clean_expired_reservations


