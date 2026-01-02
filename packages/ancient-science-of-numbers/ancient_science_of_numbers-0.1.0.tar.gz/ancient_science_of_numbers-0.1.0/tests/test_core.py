"""
Tests for core calculation functions.
"""

import unittest
from ancient_science_of_numbers.core import (
    letter_to_number,
    reduce_number,
    calculate_name_number,
    calculate_birth_number,
    get_name_letters,
)


class TestCore(unittest.TestCase):
    
    def test_letter_to_number(self):
        """Test letter to number conversion."""
        self.assertEqual(letter_to_number('A'), 1)
        self.assertEqual(letter_to_number('a'), 1)
        self.assertEqual(letter_to_number('B'), 2)
        self.assertEqual(letter_to_number('Z'), 8)
        self.assertEqual(letter_to_number('J'), 1)  # J = 1 (repeats)
        self.assertEqual(letter_to_number('S'), 1)  # S = 1 (repeats)
        
        with self.assertRaises(ValueError):
            letter_to_number('')
        with self.assertRaises(ValueError):
            letter_to_number('1')
    
    def test_reduce_number(self):
        """Test number reduction."""
        self.assertEqual(reduce_number(5), 5)
        self.assertEqual(reduce_number(10), 1)
        self.assertEqual(reduce_number(38), 2)  # 3+8=11, 1+1=2
        self.assertEqual(reduce_number(11, preserve_master=True), 11)
        self.assertEqual(reduce_number(11, preserve_master=False), 2)
        self.assertEqual(reduce_number(22, preserve_master=True), 22)
        self.assertEqual(reduce_number(33, preserve_master=True), 33)
    
    def test_calculate_name_number(self):
        """Test name number calculation."""
        # Simple name
        self.assertEqual(calculate_name_number('John'), reduce_number(1+6+8+5))  # J=1, O=6, H=8, N=5
        
        # Name with spaces
        self.assertEqual(calculate_name_number('John Doe'), calculate_name_number('JohnDoe'))
        
        # Empty name
        with self.assertRaises(ValueError):
            calculate_name_number('')
        
        # Test with master number preservation
        # Note: actual values depend on letter mapping
    
    def test_calculate_birth_number(self):
        """Test birth number calculation."""
        # Day only
        self.assertEqual(calculate_birth_number(15), 6)  # 1+5=6
        self.assertEqual(calculate_birth_number(8), 8)
        
        # Full date
        birth_num = calculate_birth_number(15, 8, 1769)
        self.assertIsInstance(birth_num, int)
        self.assertGreater(birth_num, 0)
        self.assertLessEqual(birth_num, 9)
        
        # Invalid day
        with self.assertRaises(ValueError):
            calculate_birth_number(0)
        with self.assertRaises(ValueError):
            calculate_birth_number(32)
        
        # Invalid month
        with self.assertRaises(ValueError):
            calculate_birth_number(15, 13, 1900)
    
    def test_get_name_letters(self):
        """Test extracting letters from name."""
        self.assertEqual(get_name_letters('John Doe'), ['J', 'O', 'H', 'N', 'D', 'O', 'E'])
        self.assertEqual(get_name_letters('John-Doe'), ['J', 'O', 'H', 'N', 'D', 'O', 'E'])
        self.assertEqual(get_name_letters('John123Doe'), ['J', 'O', 'H', 'N', 'D', 'O', 'E'])
        self.assertEqual(get_name_letters(''), [])


if __name__ == '__main__':
    unittest.main()

