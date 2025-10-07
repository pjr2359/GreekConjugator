#!/usr/bin/env python3
import sqlite3

def remove_duplicate_conjugations():
    print("🧹 Removing duplicate conjugations...")
    try:
        conn = sqlite3.connect('greek-conjugator/backend/greek_conjugator_dev.db')
        cursor = conn.cursor()
        
        # Find duplicate ids (keep the lowest id for each group)
        cursor.execute('''
            SELECT MIN(id) as keep_id
            FROM conjugations
            GROUP BY verb_id, tense, mood, voice, person, number, form
        ''')
        ids_to_keep = set(row[0] for row in cursor.fetchall())
        
        # Delete all conjugations not in ids_to_keep
        cursor.execute('''
            DELETE FROM conjugations
            WHERE id NOT IN (
                SELECT MIN(id)
                FROM conjugations
                GROUP BY verb_id, tense, mood, voice, person, number, form
            )
        ''')
        deleted = conn.total_changes
        conn.commit()
        conn.close()
        print(f"✅ Removed {deleted} duplicate conjugations.")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    remove_duplicate_conjugations() 