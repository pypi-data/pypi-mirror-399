"""
Tests for color associations.
"""

import unittest
from ancient_science_of_numbers.colors import (
    get_color_for_number,
    get_all_colors,
)


class TestColors(unittest.TestCase):
    
    def test_get_color_for_number(self):
        """Test getting color for number."""
        self.assertEqual(get_color_for_number(1), 'Red')
        self.assertEqual(get_color_for_number(2), 'Orange')
        self.assertEqual(get_color_for_number(3), 'Yellow')
        self.assertEqual(get_color_for_number(11), 'Silver')
        self.assertEqual(get_color_for_number(22), 'Platinum')
        
        # Large number should reduce
        color = get_color_for_number(38)  # 3+8=11, then 1+1=2
        self.assertIsNotNone(color)
    
    def test_get_all_colors(self):
        """Test getting all color mappings."""
        colors = get_all_colors()
        self.assertIsInstance(colors, dict)
        self.assertGreater(len(colors), 0)
        self.assertIn(1, colors)
        self.assertIn(11, colors)


if __name__ == '__main__':
    unittest.main()

