#!/usr/bin/env python3
import sqlite3

def check_schema():
    try:
        conn = sqlite3.connect('greek-conjugator/backend/greek_conjugator_dev.db')
        cursor = conn.cursor()
        
        # Get conjugations table schema
        cursor.execute("PRAGMA table_info(conjugations);")
        columns = cursor.fetchall()
        
        print("📋 Conjugations table columns:")
        for col in columns:
            print(f"   {col[1]} ({col[2]})")
        
        # Get a sample row
        cursor.execute("SELECT * FROM conjugations LIMIT 1;")
        sample = cursor.fetchone()
        
        if sample:
            print(f"\n📝 Sample conjugation row:")
            for i, col in enumerate(columns):
                print(f"   {col[1]}: {sample[i]}")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    check_schema() 