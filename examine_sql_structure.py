#!/usr/bin/env python3
"""
Examine SQL Structure
====================

Quick examination of the morphological dictionary SQL file structure.
"""

import re

def examine_sql_structure():
    """Examine the SQL file structure."""
    print("🔍 Examining morphological dictionary SQL structure...")
    
    try:
        with open('morph-dict-v0.2/dict.sql', 'r', encoding='utf-8') as f:
            # Read first 1000 lines to understand structure
            content = f.read(100000)  # First 100KB
            
            # Find CREATE TABLE statements
            create_tables = re.findall(r'CREATE TABLE (\w+)\(([^)]+)\)', content, re.DOTALL)
            
            print(f"📋 Found {len(create_tables)} table definitions:")
            
            for table_name, table_def in create_tables:
                print(f"\n📊 Table: {table_name}")
                # Extract column definitions
                columns = re.findall(r'(\w+)\s+([^,\n]+)', table_def)
                for col_name, col_type in columns:
                    if col_name.strip() and not col_name.strip().startswith('PRIMARY'):
                        print(f"   • {col_name.strip()}: {col_type.strip()}")
            
            # Look for INSERT statements to understand data format
            print(f"\n🔍 Looking for data patterns...")
            
            # Find some INSERT statements
            insert_pattern = r'INSERT INTO (\w+) VALUES\s*\(([^)]+)\)'
            inserts = re.findall(insert_pattern, content[:50000])  # First 50KB
            
            if inserts:
                print(f"📝 Found {len(inserts)} INSERT statements in sample")
                for table, values in inserts[:3]:  # Show first 3
                    print(f"   • {table}: {values[:100]}...")
            
            # Look for verb-like patterns
            print(f"\n🔍 Looking for verb patterns...")
            verb_pattern = r"'([^']*ω)'"  # Words ending in ω
            verbs = re.findall(verb_pattern, content[:100000])
            
            if verbs:
                print(f"📝 Found {len(verbs)} potential verbs in sample:")
                for verb in verbs[:10]:
                    print(f"   • {verb}")
            
    except Exception as e:
        print(f"❌ Error examining SQL file: {e}")

if __name__ == "__main__":
    examine_sql_structure() 