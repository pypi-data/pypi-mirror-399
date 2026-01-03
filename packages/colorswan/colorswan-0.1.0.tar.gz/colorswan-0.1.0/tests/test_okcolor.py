import unittest
from colorswan import OkColor

class TestOkColor(unittest.TestCase):
    def setUp(self):
        self.converter = OkColor()

    def test_srgb_white_conversion(self):
        # White should be roughly L=1, a=0, b=0
        result = self.converter.convert("#FFFFFF")
        oklab = result['oklab']
        
        self.assertAlmostEqual(oklab.L, 1.0, places=3)
        self.assertAlmostEqual(oklab.a, 0.0, places=3)
        self.assertAlmostEqual(oklab.b, 0.0, places=3)

    def test_srgb_black_conversion(self):
        # Black should be L=0, a=0, b=0
        result = self.converter.convert("#000000")
        oklab = result['oklab']
        
        self.assertAlmostEqual(oklab.L, 0.0, places=3)
        self.assertAlmostEqual(oklab.a, 0.0, places=3)
        self.assertAlmostEqual(oklab.b, 0.0, places=3)

    def test_red_conversion_approx(self):
        # Red #FF0000
        # Expected approx: L=0.62796, a=0.22486, b=0.12585 (Source: bottosson.github.io)
        result = self.converter.convert("#FF0000")
        oklab = result['oklab']
        
        self.assertAlmostEqual(oklab.L, 0.62796, places=2)
        self.assertAlmostEqual(oklab.a, 0.22486, places=2)
        self.assertAlmostEqual(oklab.b, 0.12585, places=2)

    def test_tuple_input(self):
        result = self.converter.convert((255, 255, 255))
        self.assertAlmostEqual(result['oklab'].L, 1.0, places=3)

    def test_invalid_input(self):
        with self.assertRaises(ValueError):
            self.converter.convert("invalid")
