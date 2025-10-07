#!/usr/bin/env python3
"""
Start Morphological Analysis
============================

Begin the analysis of the Greek morphological dictionary to extract verb conjugations.
"""

import sqlite3
import os
import json

def basic_analysis():
    """Perform basic analysis of the morphological dictionary."""
    print("🔍 Basic Analysis of Greek Morphological Dictionary")
    print("=" * 60)
    
    try:
        conn = sqlite3.connect('morph_dict.db')
        cursor = conn.cursor()
        
        # Get table names
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        table_names = [t[0] for t in tables]
        
        print(f"📋 Found {len(table_names)} tables: {', '.join(table_names)}")
        
        # Analyze each table
        for table_name in table_names:
            print(f"\n📊 Table: {table_name}")
            
            # Get row count
            cursor.execute(f"SELECT COUNT(*) FROM {table_name};")
            count = cursor.fetchone()[0]
            print(f"   Rows: {count:,}")
            
            # Get table structure
            cursor.execute(f"PRAGMA table_info({table_name});")
            columns = cursor.fetchall()
            print(f"   Columns ({len(columns)}):")
            for col in columns:
                print(f"     • {col[1]} ({col[2]})")
            
            # Get sample data
            cursor.execute(f"SELECT * FROM {table_name} LIMIT 2;")
            samples = cursor.fetchall()
            print(f"   Sample data:")
            for i, sample in enumerate(samples, 1):
                print(f"     {i}. {sample}")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Error in basic analysis: {e}")

def find_our_verbs():
    """Find our verbs in the morphological dictionary."""
    print(f"\n🔍 Finding Our Verbs in Morphological Dictionary")
    print("=" * 60)
    
    try:
        # Connect to both databases
        morph_conn = sqlite3.connect('morph_dict.db')
        our_conn = sqlite3.connect('greek-conjugator/backend/greek_conjugator_dev.db')
        
        morph_cursor = morph_conn.cursor()
        our_cursor = our_conn.cursor()
        
        # Get our verbs that need conjugations (top 20 by frequency)
        our_cursor.execute("""
            SELECT v.infinitive, v.english, v.frequency
            FROM verbs v
            LEFT JOIN conjugations c ON v.id = c.verb_id
            GROUP BY v.id
            HAVING COUNT(c.id) = 0
            ORDER BY v.frequency ASC
            LIMIT 20
        """)
        
        verbs_needing_conjugations = our_cursor.fetchall()
        
        print(f"🔍 Checking {len(verbs_needing_conjugations)} verbs that need conjugations:")
        
        found_verbs = []
        for verb, english, frequency in verbs_needing_conjugations:
            # Check if verb exists in morphological dictionary
            morph_cursor.execute("SELECT * FROM words WHERE word = ? LIMIT 1;", (verb,))
            result = morph_cursor.fetchone()
            
            if result:
                print(f"   ✅ {verb} ({english}) - Freq: {frequency}")
                found_verbs.append({
                    'verb': verb,
                    'english': english,
                    'frequency': frequency,
                    'morph_data': result
                })
            else:
                print(f"   ❌ {verb} ({english}) - Freq: {frequency}")
        
        print(f"\n📊 Summary: Found {len(found_verbs)}/{len(verbs_needing_conjugations)} verbs in morphological dictionary")
        
        # Save found verbs for further analysis
        with open('found_verbs.json', 'w', encoding='utf-8') as f:
            json.dump(found_verbs, f, ensure_ascii=False, indent=2)
        
        print(f"💾 Saved found verbs to 'found_verbs.json'")
        
        morph_conn.close()
        our_conn.close()
        
        return found_verbs
        
    except Exception as e:
        print(f"❌ Error finding verbs: {e}")
        return []

def analyze_verb_data(verb_data):
    """Analyze the data structure for a specific verb."""
    print(f"\n🔍 Analyzing Verb Data Structure")
    print("=" * 60)
    
    if not verb_data:
        print("❌ No verb data to analyze")
        return
    
    try:
        morph_conn = sqlite3.connect('morph_dict.db')
        cursor = morph_conn.cursor()
        
        # Analyze the first verb in detail
        first_verb = verb_data[0]
        verb_word = first_verb['verb']
        
        print(f"📝 Analyzing verb: {verb_word}")
        
        # Get the word record
        cursor.execute("SELECT * FROM words WHERE word = ?;", (verb_word,))
        word_record = cursor.fetchone()
        
        if word_record:
            print(f"📊 Word record: {word_record}")
            
            # Get related data from other tables
            word_id = word_record[0]  # Assuming first column is ID
            
            # Check definitions
            cursor.execute("SELECT * FROM def WHERE word_id = ? LIMIT 5;", (word_id,))
            definitions = cursor.fetchall()
            print(f"📚 Definitions ({len(definitions)}):")
            for i, def_record in enumerate(definitions, 1):
                print(f"   {i}. {def_record}")
            
            # Check normalized forms
            cursor.execute("SELECT * FROM norm WHERE word_id = ? LIMIT 5;", (word_id,))
            norms = cursor.fetchall()
            print(f"🔄 Normalized forms ({len(norms)}):")
            for i, norm_record in enumerate(norms, 1):
                print(f"   {i}. {norm_record}")
            
            # Check translations
            cursor.execute("SELECT * FROM translations WHERE word_id = ? LIMIT 5;", (word_id,))
            translations = cursor.fetchall()
            print(f"🌐 Translations ({len(translations)}):")
            for i, trans_record in enumerate(translations, 1):
                print(f"   {i}. {trans_record}")
        
        morph_conn.close()
        
    except Exception as e:
        print(f"❌ Error analyzing verb data: {e}")

def main():
    """Main analysis function."""
    print("🔬 Greek Morphological Dictionary Analysis")
    print("=" * 60)
    
    # Basic analysis
    basic_analysis()
    
    # Find our verbs
    found_verbs = find_our_verbs()
    
    # Analyze verb data structure
    analyze_verb_data(found_verbs)
    
    print(f"\n🎯 Next Steps:")
    print(f"1. Review the data structure analysis above")
    print(f"2. Check 'found_verbs.json' for the verbs we found")
    print(f"3. Design extraction scripts based on the data format")
    print(f"4. Start with a small sample (5-10 verbs)")

if __name__ == "__main__":
    main() 