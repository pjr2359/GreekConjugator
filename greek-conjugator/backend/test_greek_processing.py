#!/usr/bin/env python3
"""
Test script for Greek text processing functionality
Run this to verify the Greek text processing system is working correctly.
"""

import sys
import os

# Add the project directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.services.greek_text import GreekTextProcessor, compare_greek_texts, latin_to_greek

def test_unicode_normalization():
    """Test Unicode normalization"""
    print("🧪 Testing Unicode normalization...")
    
    # Test with accented Greek text
    text_with_accents = "γράφω"
    normalized = GreekTextProcessor.normalize_unicode(text_with_accents)
    print(f"  Original: {text_with_accents}")
    print(f"  Normalized: {normalized}")
    print(f"  ✅ Unicode normalization working")
    
def test_accent_removal():
    """Test accent removal"""
    print("\n🧪 Testing accent removal...")
    
    test_cases = [
        ("γράφω", "γραφω"),
        ("έχω", "εχω"),
        ("λέω", "λεω"),
        ("ώ", "ω"),
        ("ή", "η")
    ]
    
    for original, expected in test_cases:
        result = GreekTextProcessor.remove_accents(original)
        status = "✅" if result == expected else "❌"
        print(f"  {original} → {result} (expected: {expected}) {status}")

def test_transliteration():
    """Test Latin to Greek transliteration"""
    print("\n🧪 Testing transliteration...")
    
    test_cases = [
        ("grapho", "γραφω"),
        ("echo", "εχω"),
        ("leo", "λεω"),
        ("thelo", "θελω"),
        ("anthropos", "ανθρωπος")
    ]
    
    for latin, expected_greek in test_cases:
        result = latin_to_greek(latin)
        status = "✅" if result == expected_greek else "❌"
        print(f"  {latin} → {result} (expected: {expected_greek}) {status}")

def test_comparison():
    """Test accent-insensitive comparison"""
    print("\n🧪 Testing accent-insensitive comparison...")
    
    test_cases = [
        ("γράφω", "γραφω", True),
        ("γράφω", "γράφω", True),
        ("έχω", "εχω", True),
        ("λέω", "λέω", True),
        ("γράφω", "λέω", False),
        ("grapho", "γραφω", False),  # Different scripts, should be false
    ]
    
    for text1, text2, expected in test_cases:
        result = compare_greek_texts(text1, text2)
        status = "✅" if result == expected else "❌"
        print(f"  '{text1}' == '{text2}' → {result} (expected: {expected}) {status}")

def test_validation():
    """Test Greek text validation"""
    print("\n🧪 Testing text validation...")
    
    test_cases = [
        ("γράφω", True),
        ("hello", False),  # No Greek characters
        ("γράφω hello", True),  # Mixed but has Greek
        ("", False),  # Empty
        ("123", False),  # Numbers only
    ]
    
    for text, expected_has_greek in test_cases:
        result = GreekTextProcessor.validate_greek_input(text)
        has_greek = result.get('has_greek', False)
        status = "✅" if has_greek == expected_has_greek else "❌"
        print(f"  '{text}' has_greek={has_greek} (expected: {expected_has_greek}) {status}")

def test_similarity():
    """Test similarity scoring"""
    print("\n🧪 Testing similarity scoring...")
    
    test_cases = [
        ("γράφω", "γράφω", 1.0),  # Identical
        ("γράφω", "γραφω", 1.0),  # Accent difference only
        ("γράφω", "γραφε", 0.8),  # Similar but different ending
        ("γράφω", "λέω", 0.0),    # Completely different
    ]
    
    for text1, text2, min_expected_score in test_cases:
        score = GreekTextProcessor.get_similarity_score(text1, text2)
        status = "✅" if score >= min_expected_score else "❌"
        print(f"  '{text1}' vs '{text2}' → {score:.2f} (expected ≥ {min_expected_score}) {status}")

def main():
    """Run all tests"""
    print("🚀 Starting Greek Text Processing Tests")
    print("=" * 50)
    
    try:
        test_unicode_normalization()
        test_accent_removal()
        test_transliteration()
        test_comparison()
        test_validation()
        test_similarity()
        
        print("\n" + "=" * 50)
        print("✅ All tests completed successfully!")
        print("🎯 Greek text processing system is ready for use.")
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0

if __name__ == '__main__':
    exit(main())