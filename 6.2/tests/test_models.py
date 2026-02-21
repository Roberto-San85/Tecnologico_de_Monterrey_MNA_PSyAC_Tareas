import unittest
from src.reservation_system.models import Customer, Hotel


class TestHotel(unittest.TestCase):
    def test_hotel_create_valid(self):
        h = Hotel.create("Hotel Test", 3)
        self.assertEqual("Hotel Test", h.name)
        self.assertEqual(3, h.total_rooms)
        self.assertTrue(h.id)

    def test_hotel_create_invalid(self):
        with self.assertRaises(ValueError):
            Hotel.create("", 1)
        with self.assertRaises(ValueError):
            Hotel.create("X", 0)


class TestCustomer(unittest.TestCase):
    def test_customer_create_valid(self):
        c = Customer.create("Alice", "alice@example.com")
        self.assertIn("@", c.email)

    def test_customer_create_invalid(self):
        with self.assertRaises(ValueError):
            Customer.create("", "a@b.com")
        with self.assertRaises(ValueError):
            Customer.create("Bob", "not-an-email")


if __name__ == "__main__":
    unittest.main()
