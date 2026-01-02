"""
Color associations with numbers.
"""

from typing import Optional
from ancient_science_of_numbers.data import NUMBER_TO_COLOR
from ancient_science_of_numbers.core import reduce_number


def get_color_for_number(number: int, preserve_master: bool = True) -> Optional[str]:
    """
    Get the color associated with a number.
    
    Args:
        number: The number (can be any number, will be reduced if needed)
        preserve_master: If True, preserve master numbers for color lookup
        
    Returns:
        The color name, or None if not found
    """
    # First try direct lookup
    if number in NUMBER_TO_COLOR:
        return NUMBER_TO_COLOR[number]
    
    # Reduce if needed
    reduced = reduce_number(number, preserve_master)
    return NUMBER_TO_COLOR.get(reduced)


def get_all_colors() -> dict:
    """
    Get all number-to-color mappings.
    
    Returns:
        Dictionary mapping numbers to colors
    """
    return NUMBER_TO_COLOR.copy()

