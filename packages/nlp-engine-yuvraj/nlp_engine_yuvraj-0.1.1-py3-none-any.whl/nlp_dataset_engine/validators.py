from typing import Dict, Any
from langdetect import detect, LangDetectException

class DataValidator:
    """
    Validates dictionary rows from the stream.
    """
    def __init__(self, min_length: int = 10, check_english: bool = True,max_symbol_ratio: float = 0.3):
        self.min_length = min_length
        self.check_english = check_english
        self.max_symbol_ratio = max_symbol_ratio

    def validate(self, item: Dict[str, Any]) -> bool:
        """
        Returns True if item is valid.
        Checks:
        1. 'text' field exists & is string
        2. Length >= min_length
        3. characters don't account for more than 30% in text
        4. Language is English (optional)
        """
        text = item.get("text", "")
        
        # Check 1: Type and Emptiness
        if not isinstance(text, str) or not text.strip():
            return False
            
        # Check 2: Length
        if len(text) < self.min_length:
            return False
        
        # Check 3: Alphabetic character ratio
        alpha_count = sum(1 for c in text if c.isalpha())
        total_chars = len(text)
        if total_chars == 0:
           return False
        non_alpha_ratio = 1 - (alpha_count / total_chars)
        if non_alpha_ratio > 0.30:
           return False
 
        # Check 4: Language (only if enabled)
        if self.check_english:
            try:
                if detect(text) != 'en':
                    return False
            except LangDetectException:
                # If langdetect can't figure it out (e.g. "123"), decide to drop or keep.
                # Usually dropping is safer for NLP.
                return False
            
        return True