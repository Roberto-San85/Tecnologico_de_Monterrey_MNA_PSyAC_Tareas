import tempfile
import unittest
from datetime import date

from src.reservation_system.storage import JsonStorage
from src.reservation_system.services import (HotelService,
                                             CustomerService,
                                             ReservationService)


class TestIntegrationHotels(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        storage = JsonStorage(self.tmp.name)
        self.hotels = HotelService(storage)

    def test_hotel_crud(self):
        h = self.hotels.create("Hotel X", 2)
        self.assertIsNotNone(self.hotels.get(h.id))
        updated = self.hotels.update(h.id, name="Hotel Y", total_rooms=3)
        self.assertEqual(updated.name, "Hotel Y")
        self.assertTrue(self.hotels.delete(h.id))
        self.assertIsNone(self.hotels.get(h.id))


class TestIntegrationCustomers(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        storage = JsonStorage(self.tmp.name)
        self.customers = CustomerService(storage)

    def test_customer_crud(self):
        c = self.customers.create("Alice", "alice@example.com")
        self.assertIsNotNone(self.customers.get(c.id))
        updated = self.customers.update(c.id, name="Alicia")
        self.assertEqual(updated.name, "Alicia")
        self.assertTrue(self.customers.delete(c.id))
        self.assertIsNone(self.customers.get(c.id))


class TestIntegrationReservations(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        storage = JsonStorage(self.tmp.name)
        self.hotels = HotelService(storage)
        self.customers = CustomerService(storage)
        self.res = ReservationService(storage)

    def test_create_cancel_reservation(self):
        h = self.hotels.create("HX", 1)
        c = self.customers.create("C1", "c1@example.com")
        r = self.res.create(c.id, h.id, date(2024, 5, 1), date(2024, 5, 3))
        self.assertIsNotNone(self.res.get(r.id))
        self.assertTrue(self.res.cancel(r.id))
        self.assertFalse(self.res.cancel(r.id))  # ya no existe

    def test_capacity_enforced(self):
        h = self.hotels.create("Cap", 1)
        c1 = self.customers.create("C1", "c1@example.com")
        c2 = self.customers.create("C2", "c2@example.com")
        self.res.create(c1.id, h.id, date(2024, 6, 1), date(2024, 6, 3))
        with self.assertRaises(ValueError):
            self.res.create(c2.id, h.id, date(2024, 6, 2), date(2024, 6, 4))

    def test_nonexistent_refs(self):
        h = self.hotels.create("H", 1)
        with self.assertRaises(ValueError):
            self.res.create("no-client", h.id,
                            date(2024, 1, 1),
                            date(2024, 1, 2))


if __name__ == "__main__":
    unittest.main()
