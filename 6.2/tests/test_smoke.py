import unittest


class TestSmoke(unittest.TestCase):
    def test_smoke(self):
        self.assertEqual(1 + 2, 3)


if __name__ == "__main__":
    unittest.main()
