"""
Cycle calculations based on letters in a name.
"""

from typing import List, Dict, Any, Optional
from ancient_science_of_numbers.core import get_name_letters, letter_to_number
from ancient_science_of_numbers.data import LETTER_CHARACTERISTICS


def calculate_cycles(name: str) -> List[Dict[str, Any]]:
    """
    Calculate life cycles based on letters in the name.
    
    Each letter in the name represents a cycle period. The cycles progress
    through the letters of the name in order.
    
    Args:
        name: Full name
        
    Returns:
        List of cycle dictionaries, each containing:
        - letter: The letter for this cycle
        - number: The numerical value of the letter
        - position: The position in the name (1-based)
        - characteristics: Letter characteristics
    """
    letters = get_name_letters(name)
    cycles = []
    
    for idx, letter in enumerate(letters, start=1):
        number = letter_to_number(letter)
        characteristics = LETTER_CHARACTERISTICS.get(letter, {})
        
        cycles.append({
            'letter': letter,
            'number': number,
            'position': idx,
            'characteristics': characteristics.get('characteristics', []),
            'harmony': characteristics.get('harmony', []),
            'is_living': characteristics.get('living', False),
        })
    
    return cycles


def get_current_cycle(name: str, age: Optional[int] = None, 
                     cycle_position: Optional[int] = None) -> Optional[Dict[str, Any]]:
    """
    Get the current cycle based on age or cycle position.
    
    Note: The exact calculation method for determining current cycle
    based on age is not fully detailed in the source material, so this
    is an approximation. Typically, cycles might last 7-9 years each.
    
    Args:
        name: Full name
        age: Current age (optional)
        cycle_position: Direct cycle position (1-based, optional)
        
    Returns:
        Current cycle dictionary, or None if unable to determine
    """
    cycles = calculate_cycles(name)
    
    if not cycles:
        return None
    
    if cycle_position is not None:
        # Direct position specified
        if 1 <= cycle_position <= len(cycles):
            return cycles[cycle_position - 1]
        # Wrap around if beyond length
        return cycles[(cycle_position - 1) % len(cycles)]
    
    if age is not None:
        # Approximate: each cycle lasts about 7-9 years
        # Using 7 years per cycle as a default
        cycle_duration = 7
        cycle_index = (age // cycle_duration) % len(cycles)
        return cycles[cycle_index]
    
    # Default to first cycle if no age/position specified
    return cycles[0]


def get_cycle_by_letter(name: str, letter: str) -> List[Dict[str, Any]]:
    """
    Get all cycles that correspond to a specific letter in the name.
    
    Args:
        name: Full name
        letter: Letter to find cycles for
        
    Returns:
        List of cycle dictionaries for that letter
    """
    cycles = calculate_cycles(name)
    letter = letter.upper()
    return [cycle for cycle in cycles if cycle['letter'] == letter]

