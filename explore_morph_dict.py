#!/usr/bin/env python3
"""
Explore Greek Morphological Dictionary
=====================================

This script explores the structure and content of the Greek morphological dictionary
to understand how to extract verb conjugations for the Greek Conjugator project.
"""

import sqlite3
import os
import sys

def create_morph_db():
    """Create the morphological database from the SQL file."""
    print("🔧 Creating morphological database...")
    
    if not os.path.exists("morph-dict-v0.2/dict.sql"):
        print("❌ Error: dict.sql not found in morph-dict-v0.2/")
        return False
    
    try:
        # Create database from SQL file
        os.system("sqlite3 morph_dict.db < morph-dict-v0.2/dict.sql")
        print("✅ Database created successfully!")
        return True
    except Exception as e:
        print(f"❌ Error creating database: {e}")
        return False

def explore_database():
    """Explore the database structure and content."""
    print("\n🔍 Exploring morphological database...")
    
    try:
        conn = sqlite3.connect('morph_dict.db')
        cursor = conn.cursor()
        
        # Get table names
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        
        print(f"\n📋 Found {len(tables)} tables:")
        for table in tables:
            print(f"   • {table[0]}")
        
        # Explore the words table structure
        print("\n📊 Words table structure:")
        cursor.execute("PRAGMA table_info(words);")
        columns = cursor.fetchall()
        for col in columns:
            print(f"   • {col[1]} ({col[2]})")
        
        # Get sample data from words table
        print("\n📝 Sample words (first 10):")
        cursor.execute("SELECT * FROM words LIMIT 10;")
        sample_words = cursor.fetchall()
        for word in sample_words:
            print(f"   • {word}")
        
        # Count total words
        cursor.execute("SELECT COUNT(*) FROM words;")
        total_words = cursor.fetchone()[0]
        print(f"\n📊 Total words in dictionary: {total_words:,}")
        
        # Look for verbs specifically
        print("\n🔍 Searching for verbs...")
        cursor.execute("SELECT * FROM words WHERE word LIKE '%ω' LIMIT 10;")
        verbs = cursor.fetchall()
        print(f"📝 Sample verbs ending in -ω (first 10):")
        for verb in verbs:
            print(f"   • {verb}")
        
        # Check if there are conjugation-related fields
        print("\n🔍 Checking for conjugation data...")
        cursor.execute("SELECT * FROM words WHERE word LIKE '%ω' LIMIT 1;")
        sample_verb = cursor.fetchone()
        if sample_verb:
            print(f"📝 Sample verb structure: {sample_verb}")
        
        # Look for related tables that might contain conjugations
        print("\n🔍 Checking related tables...")
        for table_name in ['def', 'norm', 'translations']:
            try:
                cursor.execute(f"SELECT COUNT(*) FROM {table_name};")
                count = cursor.fetchone()[0]
                print(f"   • {table_name}: {count:,} entries")
                
                # Get sample data
                cursor.execute(f"SELECT * FROM {table_name} LIMIT 3;")
                samples = cursor.fetchall()
                print(f"     Sample: {samples}")
            except Exception as e:
                print(f"   • {table_name}: Error - {e}")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Error exploring database: {e}")
        return False
    
    return True

def search_for_verbs():
    """Search for specific verbs from our database."""
    print("\n🔍 Searching for verbs from our database...")
    
    try:
        # Connect to both databases
        morph_conn = sqlite3.connect('morph_dict.db')
        our_conn = sqlite3.connect('greek-conjugator/backend/greek_conjugator_dev.db')
        
        morph_cursor = morph_conn.cursor()
        our_cursor = our_conn.cursor()
        
        # Get our verbs
        our_cursor.execute("SELECT infinitive FROM verbs LIMIT 20;")
        our_verbs = [row[0] for row in our_cursor.fetchall()]
        
        print(f"🔍 Looking for {len(our_verbs)} verbs in morphological dictionary:")
        
        found_count = 0
        for verb in our_verbs:
            morph_cursor.execute("SELECT * FROM words WHERE word = ? LIMIT 1;", (verb,))
            result = morph_cursor.fetchone()
            if result:
                print(f"   ✅ {verb}: Found")
                found_count += 1
            else:
                print(f"   ❌ {verb}: Not found")
        
        print(f"\n📊 Found {found_count}/{len(our_verbs)} verbs in morphological dictionary")
        
        morph_conn.close()
        our_conn.close()
        
    except Exception as e:
        print(f"❌ Error searching for verbs: {e}")

def main():
    """Main exploration function."""
    print("🔬 Greek Morphological Dictionary Explorer")
    print("=" * 50)
    
    # Create database if it doesn't exist
    if not os.path.exists('morph_dict.db'):
        if not create_morph_db():
            return
    
    # Explore the database
    if not explore_database():
        return
    
    # Search for our verbs
    search_for_verbs()
    
    print("\n🎯 Next Steps:")
    print("1. Analyze the data structure to understand conjugation format")
    print("2. Create extraction script for verb conjugations")
    print("3. Map morphological data to our database schema")
    print("4. Import conjugations for our verbs")

if __name__ == "__main__":
    main() 