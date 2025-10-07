#!/usr/bin/env python3
import sqlite3

def test_expanded_dataset():
    """Test the expanded dataset after morphological dictionary integration"""
    print("🧪 Testing Expanded Dataset")
    print("=" * 40)
    
    try:
        conn = sqlite3.connect('greek-conjugator/backend/greek_conjugator_dev.db')
        cursor = conn.cursor()
        
        # Count total conjugations
        cursor.execute("SELECT COUNT(*) FROM conjugations")
        total_conjugations = cursor.fetchone()[0]
        print(f"📊 Total conjugations: {total_conjugations}")
        
        # Count verbs with conjugations
        cursor.execute("""
            SELECT COUNT(DISTINCT v.id) 
            FROM verbs v 
            JOIN conjugations c ON v.id = c.verb_id
        """)
        verbs_with_conjugations = cursor.fetchone()[0]
        print(f"📊 Verbs with conjugations: {verbs_with_conjugations}")
        
        # Count conjugations per verb (to verify distribution)
        cursor.execute("""
            SELECT v.infinitive, COUNT(c.id) as conjugation_count
            FROM verbs v 
            JOIN conjugations c ON v.id = c.verb_id
            GROUP BY v.id, v.infinitive
            ORDER BY conjugation_count DESC
            LIMIT 10
        """)
        
        top_verbs = cursor.fetchall()
        print(f"\n📝 Top 10 verbs by conjugation count:")
        for verb, count in top_verbs:
            print(f"   {verb}: {count} conjugations")
        
        # Test tense distribution
        cursor.execute("""
            SELECT tense, COUNT(*) as count
            FROM conjugations
            GROUP BY tense
            ORDER BY count DESC
        """)
        
        tense_distribution = cursor.fetchall()
        print(f"\n📊 Tense distribution:")
        for tense, count in tense_distribution:
            print(f"   {tense}: {count} forms")
        
        # Test mood distribution
        cursor.execute("""
            SELECT mood, COUNT(*) as count
            FROM conjugations
            GROUP BY mood
            ORDER BY count DESC
        """)
        
        mood_distribution = cursor.fetchall()
        print(f"\n📊 Mood distribution:")
        for mood, count in mood_distribution:
            print(f"   {mood}: {count} forms")
        
        # Test voice distribution
        cursor.execute("""
            SELECT voice, COUNT(*) as count
            FROM conjugations
            GROUP BY voice
            ORDER BY count DESC
        """)
        
        voice_distribution = cursor.fetchall()
        print(f"\n📊 Voice distribution:")
        for voice, count in voice_distribution:
            print(f"   {voice}: {count} forms")
        
        # Sample some new conjugations to verify quality
        cursor.execute("""
            SELECT v.infinitive, c.tense, c.mood, c.voice, c.person, c.number, c.form
            FROM verbs v 
            JOIN conjugations c ON v.id = c.verb_id
            WHERE c.id > 4884  -- New conjugations (after original 4884)
            ORDER BY RANDOM()
            LIMIT 10
        """)
        
        new_conjugations = cursor.fetchall()
        print(f"\n📝 Sample new conjugations (from morphological dictionary):")
        for row in new_conjugations:
            infinitive, tense, mood, voice, person, number, form = row
            print(f"   {infinitive}: {form} ({tense} {mood} {voice} {person} {number})")
        
        conn.close()
        
        print(f"\n✅ Dataset validation complete!")
        print(f"   The app now has {verbs_with_conjugations} verbs with conjugations")
        print(f"   Total of {total_conjugations} conjugations available for practice")
        
    except Exception as e:
        print(f"❌ Test error: {e}")

if __name__ == "__main__":
    test_expanded_dataset() 