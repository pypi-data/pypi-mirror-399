"""
Tests for harmony calculations.
"""

import unittest
from ancient_science_of_numbers.harmonies import (
    get_harmony_group,
    are_in_harmony,
    get_harmony_numbers,
)


class TestHarmonies(unittest.TestCase):
    
    def test_get_harmony_group(self):
        """Test getting harmony group for numbers."""
        self.assertEqual(get_harmony_group(1), 1)  # First Triad
        self.assertEqual(get_harmony_group(5), 1)  # First Triad
        self.assertEqual(get_harmony_group(7), 1)  # First Triad
        
        self.assertEqual(get_harmony_group(2), 2)  # Second Triad
        self.assertEqual(get_harmony_group(4), 2)  # Second Triad
        self.assertEqual(get_harmony_group(8), 2)  # Second Triad
        
        self.assertEqual(get_harmony_group(3), 3)  # Third Triad
        self.assertEqual(get_harmony_group(6), 3)  # Third Triad
        self.assertEqual(get_harmony_group(9), 3)  # Third Triad
        
        # Master numbers should reduce first
        self.assertEqual(get_harmony_group(11), 2)  # 1+1=2, Second Triad
        self.assertEqual(get_harmony_group(22), 4)  # 2+2=4, Second Triad
    
    def test_are_in_harmony(self):
        """Test harmony checking between two numbers."""
        # Same triad
        self.assertTrue(are_in_harmony(1, 5))  # Both First Triad
        self.assertTrue(are_in_harmony(1, 7))  # Both First Triad
        self.assertTrue(are_in_harmony(2, 4))  # Both Second Triad
        self.assertTrue(are_in_harmony(2, 8))  # Both Second Triad
        self.assertTrue(are_in_harmony(3, 6))  # Both Third Triad
        self.assertTrue(are_in_harmony(3, 9))  # Both Third Triad
        
        # Different triads
        self.assertFalse(are_in_harmony(1, 2))  # Different triads
        self.assertFalse(are_in_harmony(1, 3))  # Different triads
        self.assertFalse(are_in_harmony(2, 3))  # Different triads
    
    def test_get_harmony_numbers(self):
        """Test getting all numbers in a harmony group."""
        self.assertEqual(get_harmony_numbers(1), [1, 5, 7])
        self.assertEqual(get_harmony_numbers(2), [2, 4, 8])
        self.assertEqual(get_harmony_numbers(3), [3, 6, 9])
        
        with self.assertRaises(ValueError):
            get_harmony_numbers(4)


if __name__ == '__main__':
    unittest.main()

