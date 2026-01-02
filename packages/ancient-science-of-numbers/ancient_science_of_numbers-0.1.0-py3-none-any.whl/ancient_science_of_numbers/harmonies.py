"""
Harmony calculations for the Ancient Science of Numbers system.
"""

from typing import Optional
from ancient_science_of_numbers.data import HARMONY_GROUPS


def get_harmony_group(number: int) -> Optional[int]:
    """
    Get the harmony group (triad) that a number belongs to.
    
    Harmony groups:
    - First Triad: 1, 5, 7
    - Second Triad: 2, 4, 8
    - Third Triad: 3, 6, 9
    
    Args:
        number: The number to check (should be 1-9 or master number)
        
    Returns:
        The harmony group number (1, 2, or 3), or None if not in any group
    """
    # Reduce master numbers to their essence for harmony checking
    reduced = number
    if number > 9:
        # Master numbers: reduce to single digit for harmony
        while reduced > 9:
            reduced = sum(int(digit) for digit in str(reduced))
    
    if reduced in HARMONY_GROUPS:
        harmony_list = HARMONY_GROUPS[reduced]
        # Return the group number (1, 2, or 3)
        if reduced in [1, 5, 7]:
            return 1
        elif reduced in [2, 4, 8]:
            return 2
        elif reduced in [3, 6, 9]:
            return 3
    
    return None


def are_in_harmony(number1: int, number2: int) -> bool:
    """
    Check if two numbers are in harmony (belong to the same triad).
    
    Args:
        number1: First number
        number2: Second number
        
    Returns:
        True if both numbers belong to the same harmony group, False otherwise
    """
    group1 = get_harmony_group(number1)
    group2 = get_harmony_group(number2)
    
    if group1 is None or group2 is None:
        return False
    
    return group1 == group2


def get_harmony_numbers(group: int) -> list[int]:
    """
    Get all numbers in a specific harmony group.
    
    Args:
        group: Harmony group number (1, 2, or 3)
        
    Returns:
        List of numbers in that harmony group
        
    Raises:
        ValueError: If group is not 1, 2, or 3
    """
    if group == 1:
        return [1, 5, 7]
    elif group == 2:
        return [2, 4, 8]
    elif group == 3:
        return [3, 6, 9]
    else:
        raise ValueError(f"Invalid harmony group: {group}. Must be 1, 2, or 3")

