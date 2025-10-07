#!/usr/bin/env python3
"""
Fix Duplicate Conjugation Script

This script identifies and fixes duplicate conjugations in the database.
"""

import sqlite3
import os

def find_and_fix_duplicates():
    """Find and fix duplicate conjugations."""
    db_path = 'greek_conjugator_dev.db'
    
    if not os.path.exists(db_path):
        print(f"❌ Database file not found: {db_path}")
        return
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        print("🔍 Finding duplicate conjugations...")
        
        # Find duplicates
        cursor.execute("""
            SELECT verb_id, form, tense, mood, voice, COUNT(*) as count
            FROM conjugations
            GROUP BY verb_id, form, tense, mood, voice
            HAVING COUNT(*) > 1
        """)
        
        duplicates = cursor.fetchall()
        
        if not duplicates:
            print("✅ No duplicate conjugations found!")
            return
        
        print(f"⚠️  Found {len(duplicates)} duplicate conjugation groups:")
        
        for dup in duplicates:
            verb_id, form, tense, mood, voice, count = dup
            
            # Get verb name for display
            cursor.execute("SELECT infinitive FROM verbs WHERE id = ?", (verb_id,))
            verb_name = cursor.fetchone()[0]
            
            print(f"   • {verb_name}: {form} ({tense} {mood} {voice}) - {count} duplicates")
            
            # Get all instances of this duplicate
            cursor.execute("""
                SELECT id FROM conjugations 
                WHERE verb_id = ? AND form = ? AND tense = ? AND mood = ? AND voice = ?
                ORDER BY id
            """, (verb_id, form, tense, mood, voice))
            
            duplicate_ids = [row[0] for row in cursor.fetchall()]
            
            # Keep the first one, delete the rest
            ids_to_delete = duplicate_ids[1:]
            
            if ids_to_delete:
                cursor.execute("""
                    DELETE FROM conjugations 
                    WHERE id IN ({})
                """.format(','.join('?' * len(ids_to_delete))), ids_to_delete)
                
                print(f"      → Kept ID {duplicate_ids[0]}, deleted IDs: {ids_to_delete}")
        
        conn.commit()
        
        # Verify fix
        cursor.execute("""
            SELECT COUNT(*) FROM (
                SELECT verb_id, form, tense, mood, voice, COUNT(*) as count
                FROM conjugations
                GROUP BY verb_id, form, tense, mood, voice
                HAVING COUNT(*) > 1
            )
        """)
        
        remaining_duplicates = cursor.fetchone()[0]
        
        if remaining_duplicates == 0:
            print("✅ All duplicates fixed successfully!")
        else:
            print(f"⚠️  {remaining_duplicates} duplicate groups still remain")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Error fixing duplicates: {e}")

def main():
    """Main function."""
    print("🔧 Fixing Duplicate Conjugations")
    print("=" * 40)
    
    find_and_fix_duplicates()
    
    print("\n✅ Duplicate fixing process completed!")

if __name__ == '__main__':
    main() 