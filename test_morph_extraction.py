#!/usr/bin/env python3
import sqlite3

def print_finite_conjugations(cursor, verb):
    print(f"\n🔍 Finite forms for verb: {verb}")
    cursor.execute("""
        SELECT form, lemma, tense, mood, voice, person, number, aspect, verbform, greek_pos
        FROM words 
        WHERE lemma = ? AND pos = 'VERB' AND verbform = 'Fin'
        ORDER BY tense, mood, voice, person, number
    """, (verb,))
    conjugations = cursor.fetchall()
    print(f"📝 Found {len(conjugations)} finite forms:")
    for i, conj in enumerate(conjugations, 1):
        form, lemma, tense, mood, voice, person, number, aspect, verbform, greek_pos = conj
        print(f"   {i}. {form} - {tense} {mood} {voice} {person} {number} ({aspect}/{verbform}) [{greek_pos}]")


def test_extraction():
    print("🧪 Testing Morphological Dictionary Extraction")
    print("=" * 50)
    
    try:
        # Connect to morphological dictionary
        conn = sqlite3.connect('morph_dict.db')
        cursor = conn.cursor()
        
        # Print finite forms for a sample of irregular/common verbs
        for verb in ["είμαι", "έχω", "πηγαίνω", "τρώω", "βλέπω"]:
            print_finite_conjugations(cursor, verb)
        
        # Count total verbs in dictionary
        cursor.execute("SELECT COUNT(DISTINCT lemma) FROM words WHERE pos = 'VERB';")
        total_verbs = cursor.fetchone()[0]
        print(f"\n📊 Total unique verbs in dictionary: {total_verbs:,}")
        
        # Count total verb forms
        cursor.execute("SELECT COUNT(*) FROM words WHERE pos = 'VERB';")
        total_forms = cursor.fetchone()[0]
        print(f"📊 Total verb forms in dictionary: {total_forms:,}")
        
        conn.close()
        
        print(f"\n✅ Extraction test successful!")
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_extraction() 