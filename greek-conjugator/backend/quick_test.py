#!/usr/bin/env python3
"""
Quick Database Test for Greek Conjugator

A simple script to quickly check if verbs and conjugations are in the database.
"""

import sqlite3
import os

def quick_check():
    """Quick check of database contents."""
    db_path = 'greek_conjugator_dev.db'
    
    if not os.path.exists(db_path):
        print(f"❌ Database file not found: {db_path}")
        return
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        print("🔍 Quick Database Check")
        print("=" * 40)
        
        # Check verbs
        cursor.execute("SELECT COUNT(*) FROM verbs")
        verb_count = cursor.fetchone()[0]
        print(f"📊 Total verbs: {verb_count}")
        
        # Check conjugations
        cursor.execute("SELECT COUNT(*) FROM conjugations")
        conjugation_count = cursor.fetchone()[0]
        print(f"📊 Total conjugations: {conjugation_count}")
        
        # Check verbs with conjugations
        cursor.execute("""
            SELECT COUNT(DISTINCT v.id) 
            FROM verbs v 
            JOIN conjugations c ON v.id = c.verb_id
        """)
        verbs_with_conjugations = cursor.fetchone()[0]
        print(f"📊 Verbs with conjugations: {verbs_with_conjugations}")
        
        # Sample verbs
        cursor.execute("SELECT infinitive, english FROM verbs LIMIT 5")
        sample_verbs = cursor.fetchall()
        print(f"\n📋 Sample verbs:")
        for verb in sample_verbs:
            print(f"   • {verb[0]} ({verb[1]})")
        
        # Sample conjugations
        cursor.execute("""
            SELECT v.infinitive, c.form, c.tense, c.mood, c.voice 
            FROM conjugations c 
            JOIN verbs v ON c.verb_id = v.id 
            LIMIT 5
        """)
        sample_conjugations = cursor.fetchall()
        print(f"\n📋 Sample conjugations:")
        for conj in sample_conjugations:
            print(f"   • {conj[0]}: {conj[1]} ({conj[2]} {conj[3]} {conj[4]})")
        
        conn.close()
        print(f"\n✅ Database check completed!")
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == '__main__':
    quick_check() 