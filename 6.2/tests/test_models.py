import unittest
from datetime import date
from src.reservation_system.models import (Customer,
                                           Hotel,
                                           Reservation,
                                           date_from_iso,
                                           date_to_iso)


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


class TestReservation(unittest.TestCase):
    def test_reservation_dates(self):
        with self.assertRaises(ValueError):
            Reservation.create("c", "h", date(2024, 1, 10), date(2024, 1, 10))

        r = Reservation.create("c", "h", date(2024, 1, 10), date(2024, 1, 11))
        self.assertTrue(r.overlaps(Reservation.create("c", "h",
                                   date(2024, 1, 10),
                                   date(2024, 1, 12))))
        self.assertFalse(r.overlaps(Reservation.create("c", "h",
                                    date(2024, 1, 11), date(2024, 1, 12))))

    def test_date_helpers(self):
        d = date_from_iso("2024-02-29")
        self.assertEqual(date_to_iso(d), "2024-02-29")
        with self.assertRaises(ValueError):
            date_from_iso("2024/02/29")


if __name__ == "__main__":
    unittest.main()
