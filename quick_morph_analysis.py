#!/usr/bin/env python3
import sqlite3

def quick_analysis():
    print("🔍 Quick Analysis of Morphological Dictionary")
    print("=" * 50)
    
    try:
        conn = sqlite3.connect('morph_dict.db')
        cursor = conn.cursor()
        
        # Get table names
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        print(f"Tables: {[t[0] for t in tables]}")
        
        # Check words table
        cursor.execute("SELECT COUNT(*) FROM words;")
        word_count = cursor.fetchone()[0]
        print(f"Total words: {word_count:,}")
        
        # Check for verbs
        cursor.execute("SELECT COUNT(*) FROM words WHERE word LIKE '%ω';")
        verb_count = cursor.fetchone()[0]
        print(f"Verbs ending in -ω: {verb_count:,}")
        
        # Sample verbs
        cursor.execute("SELECT word FROM words WHERE word LIKE '%ω' LIMIT 10;")
        verbs = cursor.fetchall()
        print(f"Sample verbs: {[v[0] for v in verbs]}")
        
        # Check other tables
        for table in ['def', 'norm', 'translations']:
            try:
                cursor.execute(f"SELECT COUNT(*) FROM {table};")
                count = cursor.fetchone()[0]
                print(f"{table} table: {count:,} entries")
            except:
                print(f"{table} table: not found")
        
        conn.close()
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    quick_analysis() 