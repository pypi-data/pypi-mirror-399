"""
Tests for high-level analysis classes.
"""

import unittest
from ancient_science_of_numbers.analysis import (
    analyze_name,
    analyze_birth,
    full_analysis,
    NameAnalysis,
    BirthAnalysis,
    FullAnalysis,
)


class TestAnalysis(unittest.TestCase):
    
    def test_analyze_name(self):
        """Test name analysis."""
        result = analyze_name('John Doe')
        self.assertIsInstance(result, NameAnalysis)
        self.assertEqual(result.name, 'John Doe')
        self.assertGreater(result.name_number, 0)
        self.assertIsNotNone(result.cornerstone)
        self.assertIsNotNone(result.capstone)
        self.assertGreater(len(result.cycles), 0)
        self.assertIsNotNone(result.color)
        self.assertIsNotNone(result.keynote)
    
    def test_analyze_birth(self):
        """Test birth analysis."""
        result = analyze_birth(15, 8, 1769)
        self.assertIsInstance(result, BirthAnalysis)
        self.assertEqual(result.day, 15)
        self.assertEqual(result.month, 8)
        self.assertEqual(result.year, 1769)
        self.assertGreater(result.birth_number, 0)
        self.assertIsNotNone(result.color)
        self.assertIsNotNone(result.keynote)
        
        # Day only
        result = analyze_birth(8)
        self.assertEqual(result.day, 8)
        self.assertIsNone(result.month)
        self.assertIsNone(result.year)
    
    def test_full_analysis(self):
        """Test full analysis combining name and birth."""
        result = full_analysis('John Doe', 15, 8, 1769)
        self.assertIsInstance(result, FullAnalysis)
        self.assertIsInstance(result.name_analysis, NameAnalysis)
        self.assertIsInstance(result.birth_analysis, BirthAnalysis)
        self.assertIsInstance(result.are_in_harmony, bool)
        self.assertIsInstance(result.recommendations, list)
        self.assertGreater(len(result.recommendations), 0)
    
    def test_to_dict_methods(self):
        """Test conversion to dictionary."""
        name_result = analyze_name('John')
        name_dict = name_result.to_dict()
        self.assertIsInstance(name_dict, dict)
        self.assertIn('name', name_dict)
        self.assertIn('name_number', name_dict)
        
        birth_result = analyze_birth(15)
        birth_dict = birth_result.to_dict()
        self.assertIsInstance(birth_dict, dict)
        self.assertIn('day', birth_dict)
        self.assertIn('birth_number', birth_dict)
        
        full_result = full_analysis('John', 15)
        full_dict = full_result.to_dict()
        self.assertIsInstance(full_dict, dict)
        self.assertIn('name_analysis', full_dict)
        self.assertIn('birth_analysis', full_dict)
        self.assertIn('are_in_harmony', full_dict)


if __name__ == '__main__':
    unittest.main()

