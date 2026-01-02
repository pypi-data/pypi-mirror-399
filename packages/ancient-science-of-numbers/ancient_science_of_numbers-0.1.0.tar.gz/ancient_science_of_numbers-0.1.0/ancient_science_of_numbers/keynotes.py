"""
Musical note/keynote associations with numbers.
"""

from typing import Optional
from ancient_science_of_numbers.data import NUMBER_TO_KEYNOTE
from ancient_science_of_numbers.core import reduce_number


def get_keynote_for_number(number: int, preserve_master: bool = True) -> Optional[str]:
    """
    Get the musical note/keynote associated with a number.
    
    Args:
        number: The number (can be any number, will be reduced if needed)
        preserve_master: If True, preserve master numbers for keynote lookup
        
    Returns:
        The keynote/musical note, or None if not found
    """
    # First try direct lookup
    if number in NUMBER_TO_KEYNOTE:
        return NUMBER_TO_KEYNOTE[number]
    
    # Reduce if needed
    reduced = reduce_number(number, preserve_master)
    return NUMBER_TO_KEYNOTE.get(reduced)


def get_all_keynotes() -> dict:
    """
    Get all number-to-keynote mappings.
    
    Returns:
        Dictionary mapping numbers to keynotes
    """
    return NUMBER_TO_KEYNOTE.copy()

