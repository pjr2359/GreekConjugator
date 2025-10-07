#!/usr/bin/env python3
"""
Create Morphological Database
============================

Create and explore the Greek morphological dictionary database.
"""

import subprocess
import sqlite3
import os

def create_database():
    """Create the morphological database."""
    print("🔧 Creating morphological database...")
    
    try:
        # Create database from SQL file
        result = subprocess.run([
            'sqlite3', 'morph_dict.db', '<', 'morph-dict-v0.2/dict.sql'
        ], shell=True, capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Database created successfully!")
            return True
        else:
            print(f"❌ Error creating database: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def explore_database():
    """Explore the database structure."""
    print("\n🔍 Exploring database structure...")
    
    try:
        conn = sqlite3.connect('morph_dict.db')
        cursor = conn.cursor()
        
        # Get table names
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        
        print(f"📋 Found {len(tables)} tables:")
        for table in tables:
            print(f"   • {table[0]}")
        
        # Explore words table
        print("\n📊 Words table structure:")
        cursor.execute("PRAGMA table_info(words);")
        columns = cursor.fetchall()
        for col in columns:
            print(f"   • {col[1]} ({col[2]})")
        
        # Get sample data
        print("\n📝 Sample words:")
        cursor.execute("SELECT * FROM words LIMIT 5;")
        samples = cursor.fetchall()
        for sample in samples:
            print(f"   • {sample}")
        
        # Count total words
        cursor.execute("SELECT COUNT(*) FROM words;")
        total = cursor.fetchone()[0]
        print(f"\n📊 Total words: {total:,}")
        
        # Look for verbs
        print("\n🔍 Looking for verbs ending in -ω:")
        cursor.execute("SELECT word FROM words WHERE word LIKE '%ω' LIMIT 10;")
        verbs = cursor.fetchall()
        for verb in verbs:
            print(f"   • {verb[0]}")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Error exploring database: {e}")

def main():
    """Main function."""
    print("🔬 Greek Morphological Dictionary Explorer")
    print("=" * 50)
    
    if not os.path.exists('morph_dict.db'):
        if not create_database():
            return
    
    explore_database()

if __name__ == "__main__":
    main() 