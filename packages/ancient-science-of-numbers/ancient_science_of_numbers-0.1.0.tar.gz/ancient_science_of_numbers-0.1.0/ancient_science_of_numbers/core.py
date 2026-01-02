"""
Core calculation functions for name numbers and birth numbers.
"""

from ancient_science_of_numbers.data import LETTER_TO_NUMBER, MASTER_NUMBERS


def letter_to_number(letter: str) -> int:
    """
    Convert a letter to its numerical value.
    
    Args:
        letter: A single letter (A-Z, case-insensitive)
        
    Returns:
        The numerical value (1-9)
        
    Raises:
        ValueError: If the input is not a valid letter
    """
    letter = letter.upper().strip()
    if not letter or len(letter) != 1:
        raise ValueError(f"Invalid letter: {letter}")
    if letter not in LETTER_TO_NUMBER:
        raise ValueError(f"Letter '{letter}' is not in the mapping")
    return LETTER_TO_NUMBER[letter]


def reduce_number(number: int, preserve_master: bool = True) -> int:
    """
    Reduce a number to a single digit, preserving master numbers if specified.
    
    Args:
        number: The number to reduce
        preserve_master: If True, preserve master numbers (11, 22, 33)
        
    Returns:
        The reduced number (single digit or master number)
    """
    if preserve_master and number in MASTER_NUMBERS:
        return number
    
    while number > 9 and number not in MASTER_NUMBERS:
        number = sum(int(digit) for digit in str(number))
        if preserve_master and number in MASTER_NUMBERS:
            return number
    
    return number


def calculate_name_number(name: str, preserve_master: bool = True) -> int:
    """
    Calculate the name number from a full name.
    
    Args:
        name: Full name (can include spaces, will be processed)
        preserve_master: If True, preserve master numbers (11, 22, 33)
        
    Returns:
        The name number (single digit or master number)
    """
    # Remove spaces and convert to uppercase
    name = ''.join(name.upper().split())
    
    if not name:
        raise ValueError("Name cannot be empty")
    
    # Sum all letter values
    total = 0
    for letter in name:
        if letter.isalpha():
            total += letter_to_number(letter)
    
    # Reduce to single digit or master number
    return reduce_number(total, preserve_master)


def calculate_birth_number(day: int, month: int = None, year: int = None, 
                          preserve_master: bool = True) -> int:
    """
    Calculate the birth number from a birth date.
    
    According to the book, the birth number is primarily derived from the day.
    However, we can also calculate from full date if needed.
    
    Args:
        day: Day of birth (1-31)
        month: Month of birth (1-12, optional)
        year: Year of birth (optional)
        preserve_master: If True, preserve master numbers (11, 22, 33)
        
    Returns:
        The birth number (single digit or master number)
    """
    if not (1 <= day <= 31):
        raise ValueError(f"Invalid day: {day}. Must be between 1 and 31")
    
    # Primary calculation: reduce day to single digit
    birth_num = reduce_number(day, preserve_master)
    
    # If month and year are provided, we can calculate a more comprehensive number
    # But the book primarily uses the day, so we'll return that
    # For full date calculation, sum day + month + year and reduce
    if month is not None and year is not None:
        if not (1 <= month <= 12):
            raise ValueError(f"Invalid month: {month}. Must be between 1 and 12")
        full_date_sum = day + month + year
        full_birth_num = reduce_number(full_date_sum, preserve_master)
        # Return the full date number, but day number is also available
        return full_birth_num
    
    return birth_num


def get_name_letters(name: str) -> list[str]:
    """
    Extract all letters from a name, removing spaces and non-alphabetic characters.
    
    Args:
        name: Full name
        
    Returns:
        List of uppercase letters
    """
    return [char.upper() for char in name if char.isalpha()]

