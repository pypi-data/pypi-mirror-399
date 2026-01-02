"""
Tests for letter analysis functions.
"""

import unittest
from ancient_science_of_numbers.letters import (
    get_cornerstone,
    get_keystone,
    get_capstone,
    is_living_letter,
    get_letter_characteristics,
    analyze_name_structure,
)


class TestLetters(unittest.TestCase):
    
    def test_get_cornerstone(self):
        """Test getting cornerstone (first letter)."""
        self.assertEqual(get_cornerstone('John'), 'J')
        self.assertEqual(get_cornerstone('John Doe'), 'J')
        self.assertEqual(get_cornerstone('A'), 'A')
        self.assertIsNone(get_cornerstone(''))
        self.assertIsNone(get_cornerstone('123'))
    
    def test_get_keystone(self):
        """Test getting keystone (middle letter)."""
        self.assertEqual(get_keystone('John'), 'O')  # Middle of 4 letters
        self.assertEqual(get_keystone('A'), 'A')  # Single letter
        self.assertEqual(get_keystone('John Doe'), 'N')  # Middle of "JohnDoe"
        self.assertIsNone(get_keystone(''))
    
    def test_get_capstone(self):
        """Test getting capstone (last letter)."""
        self.assertEqual(get_capstone('John'), 'N')
        self.assertEqual(get_capstone('John Doe'), 'E')
        self.assertEqual(get_capstone('A'), 'A')
        self.assertIsNone(get_capstone(''))
    
    def test_is_living_letter(self):
        """Test checking if letter is a Living Letter."""
        self.assertTrue(is_living_letter('L'))
        self.assertTrue(is_living_letter('M'))
        self.assertTrue(is_living_letter('N'))
        self.assertTrue(is_living_letter('R'))
        self.assertTrue(is_living_letter('S'))
        self.assertTrue(is_living_letter('T'))
        self.assertFalse(is_living_letter('A'))
        self.assertFalse(is_living_letter('Z'))
        self.assertTrue(is_living_letter('l'))  # Case insensitive
        self.assertTrue(is_living_letter('L'))  # Uppercase
    
    def test_get_letter_characteristics(self):
        """Test getting letter characteristics."""
        char_a = get_letter_characteristics('A')
        self.assertIn('number', char_a)
        self.assertEqual(char_a['number'], 1)
        self.assertIn('characteristics', char_a)
        
        char_l = get_letter_characteristics('L')
        self.assertIn('living', char_l)
        self.assertTrue(char_l.get('living', False))
        
        # Non-existent letter
        self.assertEqual(get_letter_characteristics('?'), {})
    
    def test_analyze_name_structure(self):
        """Test analyzing name structure."""
        structure = analyze_name_structure('John')
        self.assertEqual(structure['cornerstone'], 'J')
        self.assertEqual(structure['capstone'], 'N')
        self.assertIsNotNone(structure['keystone'])
        self.assertIsNotNone(structure['cornerstone_number'])
        self.assertIsNotNone(structure['capstone_number'])
        self.assertIsInstance(structure['is_perfect'], bool)
        
        # Empty name
        structure_empty = analyze_name_structure('')
        self.assertIsNone(structure_empty['cornerstone'])


if __name__ == '__main__':
    unittest.main()

