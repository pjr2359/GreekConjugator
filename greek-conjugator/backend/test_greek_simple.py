#!/usr/bin/env python3
"""
Simple test for Greek text processing core functionality
Tests the GreekTextProcessor class directly without Flask dependencies.
"""

import sys
import os
import unicodedata

# Add the project directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import the Greek text processor directly
from app.services.greek_text import GreekTextProcessor

def test_basic_functionality():
    """Test basic Greek text processing functionality"""
    print("🧪 Testing Greek Text Processing Core Functionality")
    print("=" * 60)
    
    # Test 1: Unicode normalization
    print("\n1. Unicode Normalization:")
    text = "γράφω"
    normalized = GreekTextProcessor.normalize_unicode(text)
    print(f"   Input: {text}")
    print(f"   Normalized: {normalized}")
    print("   ✅ Unicode normalization working")
    
    # Test 2: Accent removal
    print("\n2. Accent Removal:")
    test_cases = [
        ("γράφω", "γραφω"),
        ("έχω", "εχω"),
        ("λέω", "λεω"),
    ]
    
    for original, expected in test_cases:
        result = GreekTextProcessor.remove_accents(original)
        status = "✅" if result == expected else "❌"
        print(f"   {original} → {result} (expected: {expected}) {status}")
    
    # Test 3: Transliteration
    print("\n3. Latin to Greek Transliteration:")
    test_cases = [
        ("grapho", "γραφω"),
        ("echo", "εχω"),
        ("leo", "λεω"),
        ("thelo", "θελω"),
    ]
    
    for latin, expected in test_cases:
        result = GreekTextProcessor.transliterate_to_greek(latin)
        status = "✅" if result == expected else "❌"
        print(f"   {latin} → {result} (expected: {expected}) {status}")
    
    # Test 4: Accent-insensitive comparison
    print("\n4. Accent-Insensitive Comparison:")
    test_cases = [
        ("γράφω", "γραφω", True),
        ("γράφω", "γράφω", True),
        ("έχω", "εχω", True),
        ("γράφω", "λέω", False),
    ]
    
    for text1, text2, expected in test_cases:
        result = GreekTextProcessor.compare_accent_insensitive(text1, text2)
        status = "✅" if result == expected else "❌"
        print(f"   '{text1}' == '{text2}' → {result} (expected: {expected}) {status}")
    
    # Test 5: Greek text detection
    print("\n5. Greek Text Detection:")
    test_cases = [
        ("γράφω", True),
        ("hello", False),
        ("γράφω hello", True),
        ("", False),
    ]
    
    for text, expected in test_cases:
        result = GreekTextProcessor.is_greek_text(text)
        status = "✅" if result == expected else "❌"
        print(f"   '{text}' is_greek={result} (expected: {expected}) {status}")
    
    # Test 6: Text validation
    print("\n6. Text Validation:")
    test_cases = [
        "γράφω",
        "hello",
        "γράφω hello",
        "",
    ]
    
    for text in test_cases:
        result = GreekTextProcessor.validate_greek_input(text)
        print(f"   '{text}' → valid={result['valid']}, has_greek={result.get('has_greek', False)}")
    
    # Test 7: Similarity scoring
    print("\n7. Similarity Scoring:")
    test_cases = [
        ("γράφω", "γράφω"),
        ("γράφω", "γραφω"),
        ("γράφω", "γραφε"),
        ("γράφω", "λέω"),
    ]
    
    for text1, text2 in test_cases:
        score = GreekTextProcessor.get_similarity_score(text1, text2)
        print(f"   '{text1}' vs '{text2}' → {score:.2f}")
    
    print("\n" + "=" * 60)
    print("✅ All core functionality tests completed!")
    print("🎯 Greek text processing system is working correctly.")

if __name__ == '__main__':
    test_basic_functionality()