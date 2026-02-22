import tempfile
import unittest
from src.reservation_system.storage import JsonStorage
from src.reservation_system.services import HotelService


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


if __name__ == "__main__":
    unittest.main()
