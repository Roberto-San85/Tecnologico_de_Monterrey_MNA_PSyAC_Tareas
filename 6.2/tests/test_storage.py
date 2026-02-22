import os
import json
import tempfile
import unittest
from src.reservation_system.storage import JsonStorage
from src.reservation_system.models import Hotel


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


if __name__ == "__main__":
    unittest.main()
