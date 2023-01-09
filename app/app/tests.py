from django.test import SimpleTestCase

from app import calc


class CalcTest(SimpleTestCase):
    def test_add_numers(self):
        res: int = calc.add(10, 5)

        self.assertEqual(res, 15)
    
    def test_subtract_numbers(self):
        res: int = calc.subtract(10, 5)

        self.assertEqual(res, 5)
