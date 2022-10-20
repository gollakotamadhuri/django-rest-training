from django.test import SimpleTestCase

from app.calc import add, subtract


class SampleTest(SimpleTestCase):
    def test_add(self):
        self.assertEqual(add(5, 6), 11)

    def test_sub(self):
        self.assertEqual(subtract(5, 6), -1)
