"""
Data constants and mappings for the Ancient Science of Numbers system.
"""

# Letter to number mapping (1-9 repeating)
# Standard numerology mapping: A=1, B=2, C=3, D=4, E=5, F=6, G=7, H=8, I=9
# Then repeats: J=1, K=2, L=3, M=4, N=5, O=6, P=7, Q=8, R=9, S=1, T=2, U=3, V=4, W=5, X=6, Y=7, Z=8
LETTER_TO_NUMBER = {
    'A': 1, 'B': 2, 'C': 3, 'D': 4, 'E': 5, 'F': 6, 'G': 7, 'H': 8, 'I': 9,
    'J': 1, 'K': 2, 'L': 3, 'M': 4, 'N': 5, 'O': 6, 'P': 7, 'Q': 8, 'R': 9,
    'S': 1, 'T': 2, 'U': 3, 'V': 4, 'W': 5, 'X': 6, 'Y': 7, 'Z': 8,
}

# Harmony groups (Triads)
HARMONY_GROUPS = {
    1: [1, 5, 7],  # First Triad
    2: [2, 4, 8],  # Second Triad
    3: [3, 6, 9],  # Third Triad
    5: [1, 5, 7],
    7: [1, 5, 7],
    4: [2, 4, 8],
    8: [2, 4, 8],
    6: [3, 6, 9],
    9: [3, 6, 9],
}

# Master numbers that should not be reduced
MASTER_NUMBERS = [11, 22, 33]

# Number to color mappings (from Chapter V)
# Based on standard numerology color associations
NUMBER_TO_COLOR = {
    1: "Red",
    2: "Orange",
    3: "Yellow",
    4: "Green",
    5: "Blue",
    6: "Indigo",
    7: "Violet",
    8: "Rose",
    9: "Gold",
    11: "Silver",
    22: "Platinum",
    33: "Diamond",
}

# Number to musical note/keynote mappings (from Chapter VI)
# Based on standard numerology note associations
NUMBER_TO_KEYNOTE = {
    1: "Do (C)",
    2: "Re (D)",
    3: "Mi (E)",
    4: "Fa (F)",
    5: "Sol (G)",
    6: "La (A)",
    7: "Ti (B)",
    8: "Do (C)",
    9: "Re (D)",
    11: "Mi (E)",
    22: "Fa (F)",
    33: "Sol (G)",
}

# Letter characteristics (from examples in the book)
# Living Letters - letters that have special properties
LIVING_LETTERS = ['L', 'M', 'N', 'R', 'S', 'T']

# Letter characteristics based on examples in the document
LETTER_CHARACTERISTICS = {
    'A': {
        'number': 1,
        'harmony': [1, 5, 7],
        'characteristics': ['intellectuality', 'originality in beginnings', 'change', 'ability to plan and direct'],
    },
    'B': {
        'number': 2,
        'harmony': [2, 4, 8],
        'characteristics': ['cooperation', 'diplomacy'],
    },
    'C': {
        'number': 3,
        'harmony': [3, 6, 9],
        'characteristics': ['generosity', 'honesty', 'conscientiousness', 'scattering', 'difficulty saving money'],
    },
    'D': {
        'number': 4,
        'harmony': [2, 4, 8],
        'characteristics': ['poise', 'equilibrium', 'stability'],
    },
    'E': {
        'number': 5,
        'harmony': [1, 5, 7],
        'characteristics': ['love of humanity', 'mystic leanings', 'ease in attracting material comforts', 'disintegration'],
    },
    'F': {
        'number': 6,
        'harmony': [3, 6, 9],
        'characteristics': ['harmony', 'balance'],
    },
    'G': {
        'number': 7,
        'harmony': [1, 5, 7],
        'characteristics': ['intensity to power of completion', 'intellectuality', 'love for study of occult'],
    },
    'H': {
        'number': 8,
        'harmony': [2, 4, 8],
        'characteristics': ['antagonistic to 7', 'discordant'],
    },
    'I': {
        'number': 9,
        'harmony': [3, 6, 9],
        'characteristics': ['universal spirit', 'humanitarianism'],
    },
    'J': {
        'number': 1,
        'harmony': [1, 5, 7],
        'characteristics': ['leadership', 'independence'],
    },
    'K': {
        'number': 2,
        'harmony': [2, 4, 8],
        'characteristics': ['cooperation', 'sensitivity'],
    },
    'L': {
        'number': 3,
        'harmony': [3, 6, 9],
        'living': True,
        'characteristics': ['breadth and expansion', 'executive ability', 'power in leadership', 'gather and retain material things'],
    },
    'M': {
        'number': 4,
        'harmony': [2, 4, 8],
        'living': True,
        'characteristics': ['practicality', 'organization'],
    },
    'N': {
        'number': 5,
        'harmony': [1, 5, 7],
        'living': True,
        'characteristics': ['material', 'jealousy', 'hatred', 'spite', 'intrigue'],
    },
    'O': {
        'number': 6,
        'harmony': [3, 6, 9],
        'characteristics': ['system and order', 'completion'],
    },
    'P': {
        'number': 7,
        'harmony': [1, 5, 7],
        'characteristics': ['impatient at restriction', 'aspirations to leadership', 'originality', 'eccentricity'],
    },
    'Q': {
        'number': 8,
        'harmony': [2, 4, 8],
        'characteristics': ['mystery', 'hidden knowledge'],
    },
    'R': {
        'number': 9,
        'harmony': [3, 6, 9],
        'living': True,
        'characteristics': ['literary ability', 'intellectual pursuits'],
    },
    'S': {
        'number': 1,
        'harmony': [1, 5, 7],
        'living': True,
        'characteristics': ['spirituality', 'intense spirituality', 'love', 'peace', 'benefaction'],
    },
    'T': {
        'number': 2,
        'harmony': [2, 4, 8],
        'living': True,
        'characteristics': ['intellectuality', 'righteousness', 'dictatorial qualities', 'desire to control others'],
    },
    'U': {
        'number': 3,
        'harmony': [3, 6, 9],
        'characteristics': ['intensifies name number characteristics', 'universal spirit', 'multiplicity of interests', 'generosity', 'hopeful temperament'],
    },
    'V': {
        'number': 4,
        'harmony': [2, 4, 8],
        'characteristics': ['practicality', 'efficiency'],
    },
    'W': {
        'number': 5,
        'harmony': [1, 5, 7],
        'characteristics': ['versatility', 'freedom'],
    },
    'X': {
        'number': 6,
        'harmony': [3, 6, 9],
        'characteristics': ['balance', 'harmony'],
    },
    'Y': {
        'number': 7,
        'harmony': [1, 5, 7],
        'characteristics': ['spiritual', 'mystical'],
    },
    'Z': {
        'number': 8,
        'harmony': [2, 4, 8],
        'characteristics': ['material success', 'authority'],
    },
}


