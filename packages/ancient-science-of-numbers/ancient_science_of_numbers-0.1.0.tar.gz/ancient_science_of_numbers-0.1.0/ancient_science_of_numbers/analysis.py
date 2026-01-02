"""
High-level analysis classes combining all components.
"""

from typing import Optional, Dict, Any
from dataclasses import dataclass, field
from ancient_science_of_numbers.core import (
    calculate_name_number,
    calculate_birth_number,
    get_name_letters,
)
from ancient_science_of_numbers.harmonies import are_in_harmony, get_harmony_group
from ancient_science_of_numbers.letters import analyze_name_structure
from ancient_science_of_numbers.cycles import calculate_cycles, get_current_cycle
from ancient_science_of_numbers.colors import get_color_for_number
from ancient_science_of_numbers.keynotes import get_keynote_for_number


@dataclass
class NameAnalysis:
    """Analysis results for a name."""
    name: str
    name_number: int
    name_number_reduced: int
    letters: list[str] = field(default_factory=list)
    cornerstone: Optional[str] = None
    keystone: Optional[str] = None
    capstone: Optional[str] = None
    cornerstone_number: Optional[int] = None
    keystone_number: Optional[int] = None
    capstone_number: Optional[int] = None
    is_perfect: bool = False
    cycles: list[Dict[str, Any]] = field(default_factory=list)
    color: Optional[str] = None
    keynote: Optional[str] = None
    harmony_group: Optional[int] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'name': self.name,
            'name_number': self.name_number,
            'name_number_reduced': self.name_number_reduced,
            'letters': self.letters,
            'cornerstone': self.cornerstone,
            'keystone': self.keystone,
            'capstone': self.capstone,
            'cornerstone_number': self.cornerstone_number,
            'keystone_number': self.keystone_number,
            'capstone_number': self.capstone_number,
            'is_perfect': self.is_perfect,
            'cycles': self.cycles,
            'color': self.color,
            'keynote': self.keynote,
            'harmony_group': self.harmony_group,
        }


@dataclass
class BirthAnalysis:
    """Analysis results for a birth date."""
    day: int
    month: Optional[int] = None
    year: Optional[int] = None
    birth_number: int = 0
    birth_number_reduced: int = 0
    color: Optional[str] = None
    keynote: Optional[str] = None
    harmony_group: Optional[int] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'day': self.day,
            'month': self.month,
            'year': self.year,
            'birth_number': self.birth_number,
            'birth_number_reduced': self.birth_number_reduced,
            'color': self.color,
            'keynote': self.keynote,
            'harmony_group': self.harmony_group,
        }


@dataclass
class FullAnalysis:
    """Complete analysis combining name and birth information."""
    name_analysis: NameAnalysis
    birth_analysis: BirthAnalysis
    are_in_harmony: bool = False
    recommendations: list[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'name_analysis': self.name_analysis.to_dict(),
            'birth_analysis': self.birth_analysis.to_dict(),
            'are_in_harmony': self.are_in_harmony,
            'recommendations': self.recommendations,
        }


def analyze_name(name: str, preserve_master: bool = True) -> NameAnalysis:
    """
    Perform a complete analysis of a name.
    
    Args:
        name: Full name to analyze
        preserve_master: If True, preserve master numbers (11, 22, 33)
        
    Returns:
        NameAnalysis object with all name-related calculations
    """
    # Calculate name number
    name_number = calculate_name_number(name, preserve_master)
    
    # Get letters
    letters = get_name_letters(name)
    
    # Analyze structure (cornerstone, keystone, capstone)
    structure = analyze_name_structure(name)
    
    # Calculate cycles
    cycles = calculate_cycles(name)
    
    # Get color and keynote
    color = get_color_for_number(name_number, preserve_master)
    keynote = get_keynote_for_number(name_number, preserve_master)
    
    # Get harmony group
    harmony_group = get_harmony_group(name_number)
    
    return NameAnalysis(
        name=name,
        name_number=name_number,
        name_number_reduced=name_number if name_number <= 9 else sum(int(d) for d in str(name_number)),
        letters=letters,
        cornerstone=structure['cornerstone'],
        keystone=structure['keystone'],
        capstone=structure['capstone'],
        cornerstone_number=structure['cornerstone_number'],
        keystone_number=structure['keystone_number'],
        capstone_number=structure['capstone_number'],
        is_perfect=structure['is_perfect'],
        cycles=cycles,
        color=color,
        keynote=keynote,
        harmony_group=harmony_group,
    )


def analyze_birth(day: int, month: Optional[int] = None, 
                  year: Optional[int] = None, 
                  preserve_master: bool = True) -> BirthAnalysis:
    """
    Perform a complete analysis of a birth date.
    
    Args:
        day: Day of birth (1-31)
        month: Month of birth (1-12, optional)
        year: Year of birth (optional)
        preserve_master: If True, preserve master numbers (11, 22, 33)
        
    Returns:
        BirthAnalysis object with all birth-related calculations
    """
    # Calculate birth number
    birth_number = calculate_birth_number(day, month, year, preserve_master)
    
    # Get color and keynote
    color = get_color_for_number(birth_number, preserve_master)
    keynote = get_keynote_for_number(birth_number, preserve_master)
    
    # Get harmony group
    harmony_group = get_harmony_group(birth_number)
    
    return BirthAnalysis(
        day=day,
        month=month,
        year=year,
        birth_number=birth_number,
        birth_number_reduced=birth_number if birth_number <= 9 else sum(int(d) for d in str(birth_number)),
        color=color,
        keynote=keynote,
        harmony_group=harmony_group,
    )


def full_analysis(name: str, day: int, month: Optional[int] = None,
                  year: Optional[int] = None,
                  preserve_master: bool = True) -> FullAnalysis:
    """
    Perform a complete analysis combining name and birth information.
    
    Args:
        name: Full name to analyze
        day: Day of birth (1-31)
        month: Month of birth (1-12, optional)
        year: Year of birth (optional)
        preserve_master: If True, preserve master numbers (11, 22, 33)
        
    Returns:
        FullAnalysis object with complete analysis and recommendations
    """
    # Analyze name and birth separately
    name_analysis = analyze_name(name, preserve_master)
    birth_analysis = analyze_birth(day, month, year, preserve_master)
    
    # Check harmony
    in_harmony = are_in_harmony(name_analysis.name_number, birth_analysis.birth_number)
    
    # Generate recommendations
    recommendations = []
    
    if in_harmony:
        recommendations.append("Name and birth numbers are in harmony - favorable conditions")
    else:
        recommendations.append("Name and birth numbers are not in harmony - consider name adjustments")
    
    if name_analysis.is_perfect:
        recommendations.append("Name structure is perfect (Cornerstone, Keystone, Capstone in harmony)")
    else:
        recommendations.append("Name structure could be improved for better harmony")
    
    if name_analysis.harmony_group == birth_analysis.harmony_group:
        recommendations.append("Name and birth belong to the same harmony group")
    
    return FullAnalysis(
        name_analysis=name_analysis,
        birth_analysis=birth_analysis,
        are_in_harmony=in_harmony,
        recommendations=recommendations,
    )

