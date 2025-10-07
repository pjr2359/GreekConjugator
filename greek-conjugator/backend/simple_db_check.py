#!/usr/bin/env python3
"""
Simple Database Check for Greek Conjugator

A lightweight script to check database contents without requiring the full Flask app.
"""

import sqlite3
import json
import os
from collections import Counter

def connect_to_db():
    """Connect to the SQLite database."""
    db_path = 'greek_conjugator_dev.db'
    if not os.path.exists(db_path):
        print(f"❌ Database file not found: {db_path}")
        return None
    
    try:
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row  # This allows column access by name
        return conn
    except Exception as e:
        print(f"❌ Error connecting to database: {e}")
        return None

def check_database_contents():
    """Check the basic contents of the database."""
    conn = connect_to_db()
    if not conn:
        return
    
    print("🔍 Checking database contents...")
    print("=" * 50)
    
    try:
        cursor = conn.cursor()
        
        # Check verbs table
        cursor.execute("SELECT COUNT(*) as count FROM verbs")
        verb_count = cursor.fetchone()['count']
        print(f"📊 Total verbs in database: {verb_count}")
        
        # Check conjugations table
        cursor.execute("SELECT COUNT(*) as count FROM conjugations")
        conjugation_count = cursor.fetchone()['count']
        print(f"📊 Total conjugations in database: {conjugation_count}")
        
        # Check verbs with conjugations
        cursor.execute("""
            SELECT COUNT(DISTINCT v.id) as count 
            FROM verbs v 
            JOIN conjugations c ON v.id = c.verb_id
        """)
        verbs_with_conjugations = cursor.fetchone()['count']
        print(f"📊 Verbs with conjugations: {verbs_with_conjugations}")
        
        # Check verbs without conjugations
        verbs_without_conjugations = verb_count - verbs_with_conjugations
        print(f"📊 Verbs without conjugations: {verbs_without_conjugations}")
        
        # Verb group distribution
        cursor.execute("""
            SELECT verb_group, COUNT(*) as count 
            FROM verbs 
            WHERE verb_group IS NOT NULL 
            GROUP BY verb_group 
            ORDER BY count DESC
        """)
        verb_groups = cursor.fetchall()
        
        print(f"\n📊 Verb Group Distribution:")
        for row in verb_groups:
            print(f"   • {row['verb_group']}: {row['count']}")
        
        # Tense distribution
        cursor.execute("""
            SELECT tense, COUNT(*) as count 
            FROM conjugations 
            WHERE tense IS NOT NULL 
            GROUP BY tense 
            ORDER BY count DESC
        """)
        tenses = cursor.fetchall()
        
        print(f"\n📊 Tense Distribution:")
        for row in tenses:
            print(f"   • {row['tense']}: {row['count']}")
        
        # Mood distribution
        cursor.execute("""
            SELECT mood, COUNT(*) as count 
            FROM conjugations 
            WHERE mood IS NOT NULL 
            GROUP BY mood 
            ORDER BY count DESC
        """)
        moods = cursor.fetchall()
        
        print(f"\n📊 Mood Distribution:")
        for row in moods:
            print(f"   • {row['mood']}: {row['count']}")
        
        # Voice distribution
        cursor.execute("""
            SELECT voice, COUNT(*) as count 
            FROM conjugations 
            WHERE voice IS NOT NULL 
            GROUP BY voice 
            ORDER BY count DESC
        """)
        voices = cursor.fetchall()
        
        print(f"\n📊 Voice Distribution:")
        for row in voices:
            print(f"   • {row['voice']}: {row['count']}")
        
        # Sample verbs with most conjugations
        cursor.execute("""
            SELECT v.infinitive, v.english, COUNT(c.id) as conjugation_count
            FROM verbs v
            JOIN conjugations c ON v.id = c.verb_id
            GROUP BY v.id, v.infinitive, v.english
            ORDER BY conjugation_count DESC
            LIMIT 10
        """)
        top_verbs = cursor.fetchall()
        
        print(f"\n📊 Top 10 Verbs by Conjugation Count:")
        for row in top_verbs:
            print(f"   • {row['infinitive']} ({row['english']}): {row['conjugation_count']} conjugations")
        
        # Check for data quality issues
        print(f"\n🔍 Data Quality Check:")
        
        # Check for empty forms
        cursor.execute("SELECT COUNT(*) as count FROM conjugations WHERE form IS NULL OR form = ''")
        empty_forms = cursor.fetchone()['count']
        print(f"   • Empty conjugation forms: {empty_forms}")
        
        # Check for orphaned conjugations
        cursor.execute("""
            SELECT COUNT(*) as count 
            FROM conjugations c 
            LEFT JOIN verbs v ON c.verb_id = v.id 
            WHERE v.id IS NULL
        """)
        orphaned_conjugations = cursor.fetchone()['count']
        print(f"   • Orphaned conjugations: {orphaned_conjugations}")
        
        # Check for duplicate conjugations
        cursor.execute("""
            SELECT COUNT(*) as count FROM (
                SELECT verb_id, form, tense, mood, voice, COUNT(*) as dup_count
                FROM conjugations
                GROUP BY verb_id, form, tense, mood, voice
                HAVING COUNT(*) > 1
            )
        """)
        duplicate_conjugations = cursor.fetchone()['count']
        print(f"   • Duplicate conjugations: {duplicate_conjugations}")
        
        print("\n" + "=" * 50)
        
    except Exception as e:
        print(f"❌ Error checking database: {e}")
    finally:
        conn.close()

def check_specific_verb(verb_infinitive):
    """Check a specific verb and its conjugations."""
    conn = connect_to_db()
    if not conn:
        return
    
    print(f"\n🔍 Checking verb: {verb_infinitive}")
    print("=" * 50)
    
    try:
        cursor = conn.cursor()
        
        # Get verb details
        cursor.execute("SELECT * FROM verbs WHERE infinitive = ?", (verb_infinitive,))
        verb = cursor.fetchone()
        
        if not verb:
            print(f"❌ Verb '{verb_infinitive}' not found in database")
            return
        
        print(f"📋 Verb Details:")
        print(f"   • Infinitive: {verb['infinitive']}")
        print(f"   • English: {verb['english']}")
        print(f"   • Verb Group: {verb['verb_group']}")
        print(f"   • Frequency: {verb['frequency']}")
        print(f"   • Difficulty: {verb['difficulty']}")
        print(f"   • Transitivity: {verb['transitivity']}")
        
        # Get conjugations
        cursor.execute("""
            SELECT * FROM conjugations 
            WHERE verb_id = ? 
            ORDER BY tense, mood, voice, person, number
        """, (verb['id'],))
        conjugations = cursor.fetchall()
        
        print(f"\n📊 Conjugations ({len(conjugations)} total):")
        
        # Group by tense, mood, voice
        grouped = {}
        for conj in conjugations:
            key = f"{conj['tense']}_{conj['mood']}_{conj['voice']}"
            if key not in grouped:
                grouped[key] = []
            grouped[key].append(conj)
        
        for group_name, group_conjugations in sorted(grouped.items()):
            print(f"\n   📝 {group_name.upper()} ({len(group_conjugations)} forms):")
            for conj in group_conjugations:
                person_number = f"{conj['person']} {conj['number']}" if conj['person'] and conj['number'] else "N/A"
                print(f"      • {conj['form']} ({person_number})")
        
        print("\n" + "=" * 50)
        
    except Exception as e:
        print(f"❌ Error checking verb: {e}")
    finally:
        conn.close()

def compare_with_json():
    """Compare database contents with extracted_verbs.json."""
    json_path = '../extracted_verbs.json'
    if not os.path.exists(json_path):
        print(f"❌ JSON file not found: {json_path}")
        return
    
    print("\n🔍 Comparing database with JSON file...")
    print("=" * 50)
    
    try:
        # Load JSON
        with open(json_path, 'r', encoding='utf-8') as f:
            extracted_verbs = json.load(f)
        
        # Connect to database
        conn = connect_to_db()
        if not conn:
            return
        
        cursor = conn.cursor()
        
        # Get database verbs
        cursor.execute("SELECT infinitive FROM verbs")
        db_verbs = {row['infinitive'] for row in cursor.fetchall()}
        
        # Get JSON verbs
        json_verbs = set(extracted_verbs.keys())
        
        # Compare
        print(f"📊 Verb Comparison:")
        print(f"   • Verbs in JSON: {len(json_verbs)}")
        print(f"   • Verbs in database: {len(db_verbs)}")
        
        missing_in_db = json_verbs - db_verbs
        extra_in_db = db_verbs - json_verbs
        
        print(f"   • Missing in database: {len(missing_in_db)}")
        print(f"   • Extra in database: {len(extra_in_db)}")
        
        if missing_in_db:
            print(f"\n⚠️  Sample missing verbs:")
            for verb in sorted(list(missing_in_db))[:10]:
                print(f"      • {verb}")
            if len(missing_in_db) > 10:
                print(f"      ... and {len(missing_in_db) - 10} more")
        
        if extra_in_db:
            print(f"\n⚠️  Sample extra verbs:")
            for verb in sorted(list(extra_in_db))[:10]:
                print(f"      • {verb}")
            if len(extra_in_db) > 10:
                print(f"      ... and {len(extra_in_db) - 10} more")
        
        # Calculate coverage
        if json_verbs:
            coverage = (len(db_verbs & json_verbs) / len(json_verbs)) * 100
            print(f"\n📈 Coverage: {coverage:.1f}%")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Error comparing with JSON: {e}")

def main():
    """Main function with menu."""
    print("🔍 Greek Conjugator - Simple Database Check")
    print("=" * 50)
    
    while True:
        print("\nOptions:")
        print("1. Check database contents")
        print("2. Check specific verb")
        print("3. Compare with JSON file")
        print("4. Exit")
        
        choice = input("\nEnter your choice (1-4): ").strip()
        
        if choice == '1':
            check_database_contents()
        
        elif choice == '2':
            verb = input("Enter verb infinitive: ").strip()
            if verb:
                check_specific_verb(verb)
        
        elif choice == '3':
            compare_with_json()
        
        elif choice == '4':
            print("👋 Goodbye!")
            break
        
        else:
            print("Invalid choice. Please enter 1-4.")

if __name__ == '__main__':
    main() 