"""
Letter analysis functions for Cornerstone, Keystone, and Capstone.
"""

from typing import Optional, Dict, Any
from ancient_science_of_numbers.core import get_name_letters, letter_to_number
from ancient_science_of_numbers.data import LETTER_CHARACTERISTICS, LIVING_LETTERS


def get_cornerstone(name: str) -> Optional[str]:
    """
    Get the Cornerstone (first letter) of a name.
    
    Args:
        name: Full name
        
    Returns:
        The first letter (uppercase), or None if name has no letters
    """
    letters = get_name_letters(name)
    return letters[0] if letters else None


def get_keystone(name: str) -> Optional[str]:
    """
    Get the Keystone (middle letter) of a name.
    
    Args:
        name: Full name
        
    Returns:
        The middle letter (uppercase), or None if name has no letters
    """
    letters = get_name_letters(name)
    if not letters:
        return None
    
    if len(letters) == 1:
        return letters[0]  # For single letter, it's both cornerstone and keystone
    
    # Middle letter
    middle_index = len(letters) // 2
    return letters[middle_index]


def get_capstone(name: str) -> Optional[str]:
    """
    Get the Capstone (last letter) of a name.
    
    Args:
        name: Full name
        
    Returns:
        The last letter (uppercase), or None if name has no letters
    """
    letters = get_name_letters(name)
    return letters[-1] if letters else None


def is_living_letter(letter: str) -> bool:
    """
    Check if a letter is a "Living Letter" (has special properties).
    
    Living Letters: L, M, N, R, S, T
    
    Args:
        letter: A single letter (case-insensitive)
        
    Returns:
        True if the letter is a Living Letter, False otherwise
    """
    if not letter:
        return False
    return letter.upper() in LIVING_LETTERS


def get_letter_characteristics(letter: str) -> Dict[str, Any]:
    """
    Get the characteristics and properties of a letter.
    
    Args:
        letter: A single letter
        
    Returns:
        Dictionary containing letter characteristics, or empty dict if not found
    """
    letter = letter.upper()
    return LETTER_CHARACTERISTICS.get(letter, {})


def analyze_name_structure(name: str) -> Dict[str, Any]:
    """
    Analyze the structural elements of a name (Cornerstone, Keystone, Capstone).
    
    Args:
        name: Full name
        
    Returns:
        Dictionary containing:
        - cornerstone: First letter
        - keystone: Middle letter
        - capstone: Last letter
        - cornerstone_number: Numerical value of cornerstone
        - keystone_number: Numerical value of keystone
        - capstone_number: Numerical value of capstone
        - is_perfect: Whether name structure is considered "perfect"
    """
    letters = get_name_letters(name)
    
    if not letters:
        return {
            'cornerstone': None,
            'keystone': None,
            'capstone': None,
            'cornerstone_number': None,
            'keystone_number': None,
            'capstone_number': None,
            'is_perfect': False,
        }
    
    cornerstone = letters[0]
    capstone = letters[-1]
    keystone = letters[len(letters) // 2] if len(letters) > 1 else cornerstone
    
    cornerstone_num = letter_to_number(cornerstone)
    keystone_num = letter_to_number(keystone)
    capstone_num = letter_to_number(capstone)
    
    # A name is considered "perfect" if cornerstone, keystone, and capstone
    # are all in harmony with each other
    from ancient_science_of_numbers.harmonies import are_in_harmony
    
    is_perfect = (
        are_in_harmony(cornerstone_num, keystone_num) and
        are_in_harmony(keystone_num, capstone_num)
    )
    
    return {
        'cornerstone': cornerstone,
        'keystone': keystone,
        'capstone': capstone,
        'cornerstone_number': cornerstone_num,
        'keystone_number': keystone_num,
        'capstone_number': capstone_num,
        'is_perfect': is_perfect,
        'cornerstone_is_living': is_living_letter(cornerstone),
        'keystone_is_living': is_living_letter(keystone),
        'capstone_is_living': is_living_letter(capstone),
    }

