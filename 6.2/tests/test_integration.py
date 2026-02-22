import tempfile
import unittest

from src.reservation_system.storage import JsonStorage
from src.reservation_system.services import HotelService, CustomerService


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


if __name__ == "__main__":
    unittest.main()
