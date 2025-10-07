#!/usr/bin/env python3
import sqlite3

def check_schema():
    print("🔍 Checking Morphological Dictionary Schema")
    print("=" * 50)
    
    try:
        # Connect to morphological dictionary
        conn = sqlite3.connect('morph_dict.db')
        cursor = conn.cursor()
        
        # Get table schema
        cursor.execute("PRAGMA table_info(words);")
        columns = cursor.fetchall()
        
        print("📋 Table 'words' columns:")
        for col in columns:
            print(f"   {col[1]} ({col[2]})")
        
        # Get a sample row to see actual data
        cursor.execute("SELECT * FROM words WHERE pos = 'VERB' LIMIT 1;")
        sample = cursor.fetchone()
        
        if sample:
            print(f"\n📝 Sample verb row:")
            for i, col in enumerate(columns):
                print(f"   {col[1]}: {sample[i]}")
        
        # Check what fields are actually populated
        cursor.execute("""
            SELECT DISTINCT tense FROM words WHERE pos = 'VERB' AND tense IS NOT NULL LIMIT 10;
        """)
        tenses = cursor.fetchall()
        print(f"\n📊 Sample tenses: {[t[0] for t in tenses]}")
        
        cursor.execute("""
            SELECT DISTINCT mood FROM words WHERE pos = 'VERB' AND mood IS NOT NULL LIMIT 10;
        """)
        moods = cursor.fetchall()
        print(f"📊 Sample moods: {[m[0] for m in moods]}")
        
        cursor.execute("""
            SELECT DISTINCT voice FROM words WHERE pos = 'VERB' AND voice IS NOT NULL LIMIT 10;
        """)
        voices = cursor.fetchall()
        print(f"📊 Sample voices: {[v[0] for v in voices]}")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    check_schema() 