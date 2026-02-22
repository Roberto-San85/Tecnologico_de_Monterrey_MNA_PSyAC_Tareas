import os
import json
import tempfile
import unittest
from datetime import date

from src.reservation_system.storage import JsonStorage
from src.reservation_system.models import Hotel, Customer, Reservation


class TestStorageHotels(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.storage = JsonStorage(self.tmp.name)

    def test_empty_files_created(self):
        self.assertTrue(os.path.exists(os.path.join(self.tmp.name,
                                                    "hotels.json")))
        self.assertEqual(self.storage.load_hotels(), [])

    def test_save_and_load_hotels(self):
        hotels = [Hotel.create("H1", 2)]
        self.storage.save_hotels(hotels)
        loaded = self.storage.load_hotels()
        self.assertEqual(len(loaded), 1)
        self.assertEqual(loaded[0].name, "H1")

    def test_invalid_json_is_tolerated(self):
        bad_file = os.path.join(self.tmp.name, "hotels.json")
        with open(bad_file, "w", encoding="utf-8") as fh:
            fh.write("{ not json")
        # Debe tolerar y regresar lista vacía
        self.assertEqual(self.storage.load_hotels(), [])

    def test_invalid_object_skipped(self):
        path = os.path.join(self.tmp.name, "hotels.json")
        with open(path, "w", encoding="utf-8") as fh:
            json.dump([{"id": "x"}], fh)  # faltan campos
        self.assertEqual(self.storage.load_hotels(), [])


class TestStorageCustomersReservations(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.storage = JsonStorage(self.tmp.name)

    def test_save_and_load_all(self):
        hotels = [Hotel.create("H2", 2)]
        customers = [Customer.create("C1", "c1@example.com")]
        reservations = [
            Reservation.create(
                customers[0].id, hotels[0].id,
                date(2024, 1, 1), date(2024, 1, 2)
            )
        ]

        self.storage.save_hotels(hotels)
        self.storage.save_customers(customers)
        self.storage.save_reservations(reservations)

        self.assertEqual(len(self.storage.load_hotels()), 1)
        self.assertEqual(len(self.storage.load_customers()), 1)
        self.assertEqual(len(self.storage.load_reservations()), 1)


if __name__ == "__main__":
    unittest.main()
