#!/usr/bin/env python3
"""
Analyze Morphological Dictionary
================================

Analyze the Greek morphological dictionary to understand how to extract
verb conjugations for the Greek Conjugator project.
"""

import sqlite3
import os

def analyze_database():
    """Analyze the morphological database structure and content."""
    print("🔍 Analyzing Greek Morphological Dictionary")
    print("=" * 50)
    
    try:
        conn = sqlite3.connect('morph_dict.db')
        cursor = conn.cursor()
        
        # Get all table names
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        
        print(f"📋 Database contains {len(tables)} tables:")
        for table in tables:
            print(f"   • {table[0]}")
        
        # Analyze each table
        for table_name in [t[0] for t in tables]:
            print(f"\n📊 Table: {table_name}")
            
            # Get table structure
            cursor.execute(f"PRAGMA table_info({table_name});")
            columns = cursor.fetchall()
            print(f"   Columns ({len(columns)}):")
            for col in columns:
                print(f"     • {col[1]} ({col[2]})")
            
            # Get row count
            cursor.execute(f"SELECT COUNT(*) FROM {table_name};")
            count = cursor.fetchone()[0]
            print(f"   Rows: {count:,}")
            
            # Get sample data
            cursor.execute(f"SELECT * FROM {table_name} LIMIT 3;")
            samples = cursor.fetchall()
            print(f"   Sample data:")
            for i, sample in enumerate(samples, 1):
                print(f"     {i}. {sample}")
        
        # Look for verb-related data
        print(f"\n🔍 Analyzing verb data...")
        
        # Check if words table has verb information
        cursor.execute("SELECT * FROM words WHERE word LIKE '%ω' LIMIT 5;")
        verb_samples = cursor.fetchall()
        print(f"📝 Sample verbs from 'words' table:")
        for verb in verb_samples:
            print(f"   • {verb}")
        
        # Check for conjugation-related data in other tables
        print(f"\n🔍 Looking for conjugation data...")
        
        # Check 'def' table for definitions that might contain conjugations
        cursor.execute("SELECT * FROM def LIMIT 3;")
        def_samples = cursor.fetchall()
        print(f"📝 Sample definitions:")
        for def_sample in def_samples:
            print(f"   • {def_sample}")
        
        # Check 'norm' table (might contain normalized forms)
        cursor.execute("SELECT * FROM norm LIMIT 3;")
        norm_samples = cursor.fetchall()
        print(f"📝 Sample normalized forms:")
        for norm_sample in norm_samples:
            print(f"   • {norm_sample}")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Error analyzing database: {e}")

def map_our_verbs():
    """Map our verbs to the morphological dictionary."""
    print(f"\n🔍 Mapping our verbs to morphological dictionary...")
    
    try:
        # Connect to both databases
        morph_conn = sqlite3.connect('morph_dict.db')
        our_conn = sqlite3.connect('greek-conjugator/backend/greek_conjugator_dev.db')
        
        morph_cursor = morph_conn.cursor()
        our_cursor = our_conn.cursor()
        
        # Get our verbs that need conjugations
        our_cursor.execute("""
            SELECT v.infinitive, v.english, COUNT(c.id) as conjugation_count
            FROM verbs v
            LEFT JOIN conjugations c ON v.id = c.verb_id
            GROUP BY v.id
            HAVING conjugation_count = 0
            ORDER BY v.frequency ASC
            LIMIT 20
        """)
        
        verbs_needing_conjugations = our_cursor.fetchall()
        
        print(f"🔍 Checking {len(verbs_needing_conjugations)} verbs that need conjugations:")
        
        found_count = 0
        for verb, english, count in verbs_needing_conjugations:
            # Check if verb exists in morphological dictionary
            morph_cursor.execute("SELECT * FROM words WHERE word = ? LIMIT 1;", (verb,))
            result = morph_cursor.fetchone()
            
            if result:
                print(f"   ✅ {verb} ({english}): Found in morphological dictionary")
                found_count += 1
                
                # Get related data
                morph_cursor.execute("SELECT * FROM def WHERE word_id = ? LIMIT 3;", (result[0],))
                definitions = morph_cursor.fetchall()
                if definitions:
                    print(f"     Definitions: {len(definitions)} found")
                
            else:
                print(f"   ❌ {verb} ({english}): Not found")
        
        print(f"\n📊 Summary: Found {found_count}/{len(verbs_needing_conjugations)} verbs in morphological dictionary")
        
        morph_conn.close()
        our_conn.close()
        
    except Exception as e:
        print(f"❌ Error mapping verbs: {e}")

def main():
    """Main analysis function."""
    analyze_database()
    map_our_verbs()
    
    print(f"\n🎯 Next Steps:")
    print(f"1. Analyze the data structure to understand conjugation format")
    print(f"2. Create extraction script for verb conjugations")
    print(f"3. Map morphological data to our database schema")
    print(f"4. Import conjugations for our verbs")

if __name__ == "__main__":
    main() 