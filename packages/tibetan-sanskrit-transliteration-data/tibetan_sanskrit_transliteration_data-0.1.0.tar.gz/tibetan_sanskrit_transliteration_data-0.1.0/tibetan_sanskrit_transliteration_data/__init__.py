"""
Tibetan Sanskrit Transliteration Data

Provides the replacement map for transliterating Tibetan-encoded Sanskrit.
"""

import csv
from pathlib import Path
from typing import List, Dict

__version__ = "1.0.0"

_PACKAGE_DIR = Path(__file__).parent
_CSV_PATH = _PACKAGE_DIR / "replacements.csv"


def load_replacements() -> List[Dict[str, str]]:
    """
    Load and parse the replacements CSV file.
    
    Returns:
        List of dicts with 'tibetan', 'transliteration', 'phonetics' keys.
    """
    csv_path = _CSV_PATH
    replacements = []
    
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            replacements.append({
                'tibetan': row['tibetan'],
                'transliteration': row['transliteration'],
                'phonetics': row.get('phonetics', '') or ''
            })
    
    return replacements


def get_replacements_path() -> Path:
    """
    Get the path to the replacements CSV file.
    
    Returns:
        Path to replacements.csv
    """
    return _CSV_PATH
