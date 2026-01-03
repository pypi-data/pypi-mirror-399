"""Tests for cli.style module"""
import unittest
from fileindex.cli.style import Style


class TestStyle(unittest.TestCase):
    """Test cases for Style class"""

    def setUp(self):
        self.style = Style()

    def test_style_constants_exist(self):
        """Test that all style constants are defined"""
        # Reset and modifiers
        self.assertTrue(hasattr(Style, 'RESET'))
        self.assertTrue(hasattr(Style, 'BOLD'))
        self.assertTrue(hasattr(Style, 'DIM'))

        # Colors
        self.assertTrue(hasattr(Style, 'RED'))
        self.assertTrue(hasattr(Style, 'GREEN'))
        self.assertTrue(hasattr(Style, 'BLUE'))

        # Presets
        self.assertTrue(hasattr(Style, 'SUCCESS'))
        self.assertTrue(hasattr(Style, 'ERROR'))
        self.assertTrue(hasattr(Style, 'WARNING'))
        self.assertTrue(hasattr(Style, 'INFO'))

    def test_apply_method(self):
        """Test Style.apply combines styles correctly"""
        result = Style.apply(Style.BOLD, Style.RED)
        self.assertEqual(result, Style.BOLD + Style.RED)
        self.assertIn('\033[1m', result)  # BOLD
        self.assertIn('\033[31m', result)  # RED

    def test_pretty_method_exists(self):
        """Test that pretty method exists and is callable"""
        self.assertTrue(hasattr(self.style, 'pretty'))
        self.assertTrue(callable(self.style.pretty))

    def test_style_presets_contain_codes(self):
        """Test that semantic presets contain style codes"""
        # ERROR contains bold and bright red
        self.assertIn(Style.BOLD, Style.ERROR)
        self.assertIn(Style.BRIGHT_RED, Style.ERROR)
        # SUCCESS contains bright green
        self.assertIn(Style.BRIGHT_GREEN, Style.SUCCESS)
        # INFO contains bright cyan
        self.assertIn(Style.BRIGHT_CYAN, Style.INFO)


class TestStyleColors(unittest.TestCase):
    """Test color definitions"""

    def test_foreground_colors_defined(self):
        """Test standard foreground colors are defined"""
        colors = ['BLACK', 'RED', 'GREEN', 'YELLOW', 'BLUE', 'MAGENTA', 'CYAN', 'WHITE']
        for color in colors:
            self.assertTrue(hasattr(Style, color))
            self.assertIsInstance(getattr(Style, color), str)
            self.assertTrue(len(getattr(Style, color)) > 0)

    def test_background_colors_defined(self):
        """Test background colors are defined"""
        self.assertTrue(hasattr(Style, 'BG_BLACK'))
        self.assertTrue(hasattr(Style, 'BG_RED'))
        self.assertTrue(hasattr(Style, 'BG_GREEN'))

    def test_bright_colors_defined(self):
        """Test bright colors are defined"""
        self.assertTrue(hasattr(Style, 'BRIGHT_RED'))
        self.assertTrue(hasattr(Style, 'BRIGHT_GREEN'))


if __name__ == '__main__':
    unittest.main()
