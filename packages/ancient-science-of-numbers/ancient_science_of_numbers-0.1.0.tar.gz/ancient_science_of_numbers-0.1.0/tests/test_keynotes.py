"""
Tests for keynote/musical note associations.
"""

import unittest
from ancient_science_of_numbers.keynotes import (
    get_keynote_for_number,
    get_all_keynotes,
)


class TestKeynotes(unittest.TestCase):
    
    def test_get_keynote_for_number(self):
        """Test getting keynote for number."""
        self.assertEqual(get_keynote_for_number(1), 'Do (C)')
        self.assertEqual(get_keynote_for_number(2), 'Re (D)')
        self.assertEqual(get_keynote_for_number(3), 'Mi (E)')
        self.assertEqual(get_keynote_for_number(11), 'Mi (E)')
        
        # Large number should reduce
        keynote = get_keynote_for_number(38)  # 3+8=11, then 1+1=2
        self.assertIsNotNone(keynote)
    
    def test_get_all_keynotes(self):
        """Test getting all keynote mappings."""
        keynotes = get_all_keynotes()
        self.assertIsInstance(keynotes, dict)
        self.assertGreater(len(keynotes), 0)
        self.assertIn(1, keynotes)
        self.assertIn(11, keynotes)


if __name__ == '__main__':
    unittest.main()

