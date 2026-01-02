"""
Tests for cycle calculations.
"""

import unittest
from ancient_science_of_numbers.cycles import (
    calculate_cycles,
    get_current_cycle,
    get_cycle_by_letter,
)


class TestCycles(unittest.TestCase):
    
    def test_calculate_cycles(self):
        """Test calculating cycles from name."""
        cycles = calculate_cycles('John')
        self.assertEqual(len(cycles), 4)  # 4 letters
        self.assertEqual(cycles[0]['letter'], 'J')
        self.assertEqual(cycles[1]['letter'], 'O')
        self.assertEqual(cycles[2]['letter'], 'H')
        self.assertEqual(cycles[3]['letter'], 'N')
        
        # Each cycle should have required fields
        for cycle in cycles:
            self.assertIn('letter', cycle)
            self.assertIn('number', cycle)
            self.assertIn('position', cycle)
            self.assertIn('characteristics', cycle)
    
    def test_get_current_cycle(self):
        """Test getting current cycle."""
        # By position
        cycle = get_current_cycle('John', cycle_position=1)
        self.assertEqual(cycle['letter'], 'J')
        self.assertEqual(cycle['position'], 1)
        
        cycle = get_current_cycle('John', cycle_position=2)
        self.assertEqual(cycle['letter'], 'O')
        
        # By age (approximate)
        cycle = get_current_cycle('John', age=0)
        self.assertIsNotNone(cycle)
        
        cycle = get_current_cycle('John', age=7)
        self.assertIsNotNone(cycle)
        
        # Wrap around
        cycle = get_current_cycle('John', cycle_position=10)
        self.assertIsNotNone(cycle)
        
        # Empty name
        self.assertIsNone(get_current_cycle(''))
    
    def test_get_cycle_by_letter(self):
        """Test getting cycles for specific letter."""
        cycles = get_cycle_by_letter('John Doe', 'O')
        # 'O' appears twice in "John Doe"
        self.assertGreaterEqual(len(cycles), 1)
        self.assertEqual(cycles[0]['letter'], 'O')
        
        # Letter not in name
        cycles = get_cycle_by_letter('John', 'Z')
        self.assertEqual(len(cycles), 0)


if __name__ == '__main__':
    unittest.main()

