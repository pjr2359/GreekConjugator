#!/usr/bin/env python3
"""
Greek Text Processing Utilities

Comprehensive utilities for handling Greek text processing including:
- Unicode normalization
- Accent-insensitive comparison
- Latin to Greek transliteration
- Text validation
"""

import unicodedata
import re
from typing import Dict, List, Optional, Tuple


class GreekTextProcessor:
    """Main class for Greek text processing operations"""
    
    # Greek Unicode ranges
    GREEK_BASIC_RANGE = (0x0370, 0x03FF)  # Greek and Coptic
    GREEK_EXTENDED_RANGE = (0x1F00, 0x1FFF)  # Greek Extended
    
    # Transliteration mapping from Latin to Greek
    TRANSLITERATION_MAP = {
        # Basic vowels
        'a': 'α', 'e': 'ε', 'i': 'ι', 'o': 'ο', 'u': 'υ',
        'A': 'Α', 'E': 'Ε', 'I': 'Ι', 'O': 'Ο', 'U': 'Υ',
        
        # Diphthongs (order matters - longer first)
        'ai': 'αι', 'au': 'αυ', 'ei': 'ει', 'eu': 'ευ', 'oi': 'οι', 'ou': 'ου',
        'ui': 'υι', 'Ai': 'Αι', 'Au': 'Αυ', 'Ei': 'Ει', 'Eu': 'Ευ', 'Oi': 'Οι',
        'Ou': 'Ου', 'Ui': 'Υι',
        
        # Consonants
        'b': 'β', 'g': 'γ', 'd': 'δ', 'z': 'ζ', 'th': 'θ', 'k': 'κ', 'l': 'λ',
        'm': 'μ', 'n': 'ν', 'x': 'ξ', 'p': 'π', 'r': 'ρ', 's': 'σ', 't': 'τ',
        'f': 'φ', 'ch': 'χ', 'ps': 'ψ', 'w': 'ω',
        
        'B': 'Β', 'G': 'Γ', 'D': 'Δ', 'Z': 'Ζ', 'Th': 'Θ', 'K': 'Κ', 'L': 'Λ',
        'M': 'Μ', 'N': 'Ν', 'X': 'Ξ', 'P': 'Π', 'R': 'Ρ', 'S': 'Σ', 'T': 'Τ',
        'F': 'Φ', 'Ch': 'Χ', 'Ps': 'Ψ', 'W': 'Ω',
        
        # Special cases
        'h': 'η', 'H': 'Η',  # eta
        'y': 'υ', 'Y': 'Υ',  # upsilon alternative
        'c': 'κ', 'C': 'Κ',  # kappa alternative
        'j': 'ι', 'J': 'Ι',  # iota alternative
        'v': 'β', 'V': 'Β',  # beta alternative
        'q': 'κ', 'Q': 'Κ',  # kappa alternative
    }
    
    # Reverse mapping for Greek to Latin
    REVERSE_TRANSLITERATION = {
        'α': 'a', 'β': 'b', 'γ': 'g', 'δ': 'd', 'ε': 'e', 'ζ': 'z', 'η': 'h',
        'θ': 'th', 'ι': 'i', 'κ': 'k', 'λ': 'l', 'μ': 'm', 'ν': 'n', 'ξ': 'x',
        'ο': 'o', 'π': 'p', 'ρ': 'r', 'σ': 's', 'ς': 's', 'τ': 't', 'υ': 'u',
        'φ': 'f', 'χ': 'ch', 'ψ': 'ps', 'ω': 'w',
        
        'Α': 'A', 'Β': 'B', 'Γ': 'G', 'Δ': 'D', 'Ε': 'E', 'Ζ': 'Z', 'Η': 'H',
        'Θ': 'Th', 'Ι': 'I', 'Κ': 'K', 'Λ': 'L', 'Μ': 'M', 'Ν': 'N', 'Ξ': 'X',
        'Ο': 'O', 'Π': 'P', 'Ρ': 'R', 'Σ': 'S', 'Τ': 'T', 'Υ': 'U', 'Φ': 'F',
        'Χ': 'Ch', 'Ψ': 'Ps', 'Ω': 'W'
    }
    
    # Common Greek diacritical marks
    DIACRITICS = {
        'acute': '\u0301',      # ́ (combining acute accent)
        'grave': '\u0300',      # ̀ (combining grave accent)
        'circumflex': '\u0342', # ͂ (combining perispomeni)
        'diaeresis': '\u0308',  # ̈ (combining diaeresis)
        'rough': '\u0314',      # ̔ (combining reversed comma above)
        'smooth': '\u0313',     # ̓ (combining comma above)
        'iota_subscript': '\u0345'  # ͅ (combining iota subscript)
    }
    
    @classmethod
    def normalize_unicode(cls, text: str) -> str:
        """
        Normalize Greek text to NFC (Canonical Decomposition, followed by Canonical Composition)
        This ensures consistent representation of accented characters.
        """
        if not text:
            return ""
        
        # First normalize to NFD (decomposed form)
        nfd_text = unicodedata.normalize('NFD', text)
        
        # Then normalize to NFC (composed form)
        nfc_text = unicodedata.normalize('NFC', nfd_text)
        
        return nfc_text
    
    @classmethod
    def remove_accents(cls, text: str) -> str:
        """
        Remove all diacritical marks from Greek text while preserving base characters.
        Useful for accent-insensitive comparisons.
        """
        if not text:
            return ""
        
        # Normalize to NFD to separate base characters from diacritics
        nfd_text = unicodedata.normalize('NFD', text)
        
        # Remove combining characters (diacritics)
        no_accents = ''.join(
            char for char in nfd_text 
            if unicodedata.category(char) != 'Mn'  # Mn = Nonspacing_Mark
        )
        
        # Handle final sigma conversion
        no_accents = cls._handle_final_sigma(no_accents)
        
        return unicodedata.normalize('NFC', no_accents)
    
    @classmethod
    def _handle_final_sigma(cls, text: str) -> str:
        """Convert final sigma (ς) to regular sigma (σ) for comparison purposes"""
        return text.replace('ς', 'σ')
    
    @classmethod
    def compare_accent_insensitive(cls, text1: str, text2: str) -> bool:
        """
        Compare two Greek texts ignoring accents and case.
        Returns True if texts are equivalent.
        """
        if not text1 and not text2:
            return True
        if not text1 or not text2:
            return False
        
        # Normalize both texts
        norm1 = cls.normalize_unicode(text1.lower().strip())
        norm2 = cls.normalize_unicode(text2.lower().strip())
        
        # Remove accents
        clean1 = cls.remove_accents(norm1)
        clean2 = cls.remove_accents(norm2)
        
        return clean1 == clean2
    
    @classmethod
    def transliterate_to_greek(cls, latin_text: str) -> str:
        """
        Convert Latin text to Greek using transliteration mapping.
        Processes longer sequences first to handle digraphs correctly.
        """
        if not latin_text:
            return ""
        
        result = latin_text
        
        # Sort by length (descending) to handle longer sequences first
        sorted_mappings = sorted(cls.TRANSLITERATION_MAP.items(), key=lambda x: len(x[0]), reverse=True)
        
        for latin, greek in sorted_mappings:
            result = result.replace(latin, greek)
        
        return result
    
    @classmethod
    def transliterate_to_latin(cls, greek_text: str) -> str:
        """
        Convert Greek text to Latin using reverse transliteration mapping.
        """
        if not greek_text:
            return ""
        
        # Remove accents first for cleaner transliteration
        clean_greek = cls.remove_accents(greek_text)
        result = clean_greek
        
        # Sort by length (descending) to handle longer sequences first
        sorted_mappings = sorted(cls.REVERSE_TRANSLITERATION.items(), key=lambda x: len(x[0]), reverse=True)
        
        for greek, latin in sorted_mappings:
            result = result.replace(greek, latin)
        
        return result
    
    @classmethod
    def is_greek_text(cls, text: str) -> bool:
        """
        Check if text contains Greek characters.
        Returns True if at least one Greek character is found.
        """
        if not text:
            return False
        
        for char in text:
            code_point = ord(char)
            if (cls.GREEK_BASIC_RANGE[0] <= code_point <= cls.GREEK_BASIC_RANGE[1] or
                cls.GREEK_EXTENDED_RANGE[0] <= code_point <= cls.GREEK_EXTENDED_RANGE[1]):
                return True
        
        return False
    
    @classmethod
    def validate_greek_input(cls, text: str) -> Dict[str, any]:
        """
        Validate Greek text input and return validation results.
        Returns a dictionary with validation status and details.
        """
        if not text:
            return {
                'valid': False,
                'error': 'Empty text',
                'normalized': '',
                'has_greek': False,
                'character_count': 0
            }
        
        try:
            # Normalize the text
            normalized = cls.normalize_unicode(text.strip())
            
            # Check for Greek characters
            has_greek = cls.is_greek_text(normalized)
            
            # Count characters (excluding spaces)
            char_count = len(normalized.replace(' ', ''))
            
            # Check for invalid characters (optional strict validation)
            invalid_chars = cls._find_invalid_characters(normalized)
            
            validation_result = {
                'valid': True,
                'normalized': normalized,
                'has_greek': has_greek,
                'character_count': char_count,
                'invalid_characters': invalid_chars,
                'warnings': []
            }
            
            # Add warnings for mixed scripts
            if has_greek and cls._has_latin_characters(normalized):
                validation_result['warnings'].append('Mixed Greek and Latin characters detected')
            
            # Add warning for very long input
            if char_count > 200:
                validation_result['warnings'].append('Text is unusually long')
            
            return validation_result
            
        except Exception as e:
            return {
                'valid': False,
                'error': f'Validation error: {str(e)}',
                'normalized': '',
                'has_greek': False,
                'character_count': 0
            }
    
    @classmethod
    def _find_invalid_characters(cls, text: str) -> List[str]:
        """Find characters that are not Greek, Latin, spaces, or punctuation"""
        invalid_chars = []
        
        for char in text:
            if char.isspace():
                continue
            
            code_point = ord(char)
            
            # Allow Greek characters
            if (cls.GREEK_BASIC_RANGE[0] <= code_point <= cls.GREEK_BASIC_RANGE[1] or
                cls.GREEK_EXTENDED_RANGE[0] <= code_point <= cls.GREEK_EXTENDED_RANGE[1]):
                continue
            
            # Allow basic Latin characters (for mixed input)
            if (0x0020 <= code_point <= 0x007F):  # Basic Latin
                continue
            
            # Allow basic punctuation
            if unicodedata.category(char).startswith('P'):
                continue
            
            if char not in invalid_chars:
                invalid_chars.append(char)
        
        return invalid_chars
    
    @classmethod
    def _has_latin_characters(cls, text: str) -> bool:
        """Check if text contains Latin characters"""
        for char in text:
            if 0x0041 <= ord(char) <= 0x005A or 0x0061 <= ord(char) <= 0x007A:  # A-Z, a-z
                return True
        return False
    
    @classmethod
    def get_similarity_score(cls, text1: str, text2: str) -> float:
        """
        Calculate similarity score between two Greek texts (0.0 to 1.0).
        Uses accent-insensitive comparison and character-level similarity.
        """
        if not text1 and not text2:
            return 1.0
        if not text1 or not text2:
            return 0.0
        
        # Normalize and clean both texts
        clean1 = cls.remove_accents(cls.normalize_unicode(text1.lower().strip()))
        clean2 = cls.remove_accents(cls.normalize_unicode(text2.lower().strip()))
        
        # Exact match
        if clean1 == clean2:
            return 1.0
        
        # Calculate character-level similarity using longest common subsequence
        return cls._calculate_lcs_similarity(clean1, clean2)
    
    @classmethod
    def _calculate_lcs_similarity(cls, text1: str, text2: str) -> float:
        """Calculate similarity using Longest Common Subsequence algorithm"""
        if not text1 or not text2:
            return 0.0
        
        m, n = len(text1), len(text2)
        
        # Create DP table
        dp = [[0] * (n + 1) for _ in range(m + 1)]
        
        # Fill the DP table
        for i in range(1, m + 1):
            for j in range(1, n + 1):
                if text1[i-1] == text2[j-1]:
                    dp[i][j] = dp[i-1][j-1] + 1
                else:
                    dp[i][j] = max(dp[i-1][j], dp[i][j-1])
        
        # Calculate similarity ratio
        lcs_length = dp[m][n]
        max_length = max(m, n)
        
        return lcs_length / max_length if max_length > 0 else 0.0
    
    @classmethod
    def suggest_corrections(cls, input_text: str, target_text: str) -> List[str]:
        """
        Suggest corrections for Greek text input based on target text.
        Returns a list of suggested corrections.
        """
        if not input_text or not target_text:
            return []
        
        suggestions = []
        
        # Check if it's just an accent issue
        if cls.compare_accent_insensitive(input_text, target_text):
            suggestions.append(f"Check accents: {target_text}")
        
        # Check if it's a case issue
        if cls.remove_accents(input_text.lower()) == cls.remove_accents(target_text.lower()):
            suggestions.append(f"Check capitalization: {target_text}")
        
        # Check for common transliteration mistakes
        transliterated = cls.transliterate_to_greek(input_text)
        if cls.compare_accent_insensitive(transliterated, target_text):
            suggestions.append(f"Try Greek characters: {target_text}")
        
        return suggestions


# Convenience functions for common operations
def normalize_greek(text: str) -> str:
    """Normalize Greek text to standard Unicode form"""
    return GreekTextProcessor.normalize_unicode(text)


def compare_greek_texts(text1: str, text2: str) -> bool:
    """Compare two Greek texts ignoring accents and case"""
    return GreekTextProcessor.compare_accent_insensitive(text1, text2)


def latin_to_greek(text: str) -> str:
    """Convert Latin text to Greek using transliteration"""
    return GreekTextProcessor.transliterate_to_greek(text)


def greek_to_latin(text: str) -> str:
    """Convert Greek text to Latin using reverse transliteration"""
    return GreekTextProcessor.transliterate_to_latin(text)


def validate_greek(text: str) -> Dict[str, any]:
    """Validate Greek text input"""
    return GreekTextProcessor.validate_greek_input(text)


def get_text_similarity(text1: str, text2: str) -> float:
    """Get similarity score between two Greek texts"""
    return GreekTextProcessor.get_similarity_score(text1, text2)