import re
from typing import Tuple

class ClueClassifier:
    """Simple classifier that categorizes puzzle clues by type."""
    
    def __init__(self):
        # Compile patterns for each clue type
        self.patterns = {
            'POSITION_ABSOLUTE': re.compile(r'(?:is\s+)?in\s+the\s+(\w+)\s+house', re.IGNORECASE),
            'POSITION_ABSOLUTE_NEGATIVE': re.compile(r'is\s+not\s+in\s+the\s+(\w+)\s+house', re.IGNORECASE),
            'NEXT_TO': re.compile(r'(?:and|are)\s+next\s+to\s+each\s+other', re.IGNORECASE),
            'DIRECT_LEFT': re.compile(r'(?:is\s+)?directly\s+(?:left|to\s+the\s+left)\s+of', re.IGNORECASE),
            'DIRECT_RIGHT': re.compile(r'(?:is\s+)?directly\s+(?:right|to\s+the\s+right)\s+of', re.IGNORECASE),
            'LEFT': re.compile(r'(?:is\s+)?(?:somewhere\s+)?to\s+the\s+left\s+of', re.IGNORECASE),
            'RIGHT': re.compile(r'(?:is\s+)?(?:somewhere\s+)?to\s+the\s+right\s+of', re.IGNORECASE),
            'DISTANCE': re.compile(r'(?:there\s+)?(?:is|are)\s+(?:\w+\s+)?house[s]?\s+between', re.IGNORECASE),
            'IDENTITY': re.compile(r'is\s+', re.IGNORECASE),
        }
    
    def classify(self, clue: str) -> Tuple[str, str]:
        """
        Classify a clue and return (clue, type).
        
        Args:
            clue: The clue text to classify
            
        Returns:
            Tuple of (clue, type_string) where type_string is one of:
            - 'POSITION_ABSOLUTE': X is in the Nth house
            - 'POSITION_ABSOLUTE_NEGATIVE': X is not in the Nth house
            - 'DISTANCE': N house(s) between X and Y
            - 'NEXT_TO': X and Y are next to each other
            - 'DIRECT_LEFT': X is directly left of Y
            - 'DIRECT_RIGHT': X is directly right of Y
            - 'LEFT': X is somewhere left of Y
            - 'RIGHT': X is somewhere right of Y
            - 'IDENTITY': X is Y (attribute assignment)
            - 'UNKNOWN': Could not classify
        """
        clue = clue.strip()
        
        # Check patterns in order of specificity (most specific first)
        if self.patterns['POSITION_ABSOLUTE_NEGATIVE'].search(clue):
            return (clue, 'POSITION_ABSOLUTE_NEGATIVE')
        
        if self.patterns['DISTANCE'].search(clue):
            return (clue, 'DISTANCE')
        
        if self.patterns['NEXT_TO'].search(clue):
            return (clue, 'NEXT_TO')
        
        if self.patterns['DIRECT_LEFT'].search(clue):
            return (clue, 'DIRECT_LEFT')
        
        if self.patterns['DIRECT_RIGHT'].search(clue):
            return (clue, 'DIRECT_RIGHT')
        
        if self.patterns['LEFT'].search(clue):
            return (clue, 'LEFT')
        
        if self.patterns['RIGHT'].search(clue):
            return (clue, 'RIGHT')
        
        if self.patterns['POSITION_ABSOLUTE'].search(clue):
            return (clue, 'POSITION_ABSOLUTE')
        
        if self.patterns['IDENTITY'].search(clue):
            return (clue, 'IDENTITY')
        
        return (clue, 'UNKNOWN')
