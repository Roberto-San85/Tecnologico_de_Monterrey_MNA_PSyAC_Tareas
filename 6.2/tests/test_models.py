import unittest
from src.reservation_system.models import Hotel


class TestHotel(unittest.TestCase):
    def test_hotel_create_valid(self):
        h = Hotel.create("Hotel Test", 3)
        self.assertEqual(h.name, "Hotel Test")
        self.assertEqual(h.total_rooms, 3)
        self.assertTrue(h.id)

    def test_hotel_create_invalid(self):
        with self.assertRaises(ValueError):
            Hotel.create("", 1)
        with self.assertRaises(ValueError):
            Hotel.create("X", 0)


if __name__ == "__main__":
    unittest.main()
