#!/usr/bin/env python3
"""
Extract Verb Conjugations from Morphological Dictionary
======================================================

Extract verb conjugations from the Greek morphological dictionary
and import them into our Greek Conjugator database.
"""

import sqlite3
import json
import os

def get_our_verbs_needing_conjugations():
    """Get our verbs that need conjugations."""
    try:
        conn = sqlite3.connect('greek-conjugator/backend/greek_conjugator_dev.db')
        cursor = conn.cursor()
        
        # Get verbs without conjugations, ordered by frequency
        cursor.execute("""
            SELECT v.id, v.infinitive, v.english, v.frequency, v.verb_group
            FROM verbs v
            LEFT JOIN conjugations c ON v.id = c.verb_id
            GROUP BY v.id
            HAVING COUNT(c.id) = 0
            ORDER BY v.frequency ASC
            LIMIT 50
        """)
        
        verbs = cursor.fetchall()
        conn.close()
        
        return verbs
        
    except Exception as e:
        print(f"❌ Error getting our verbs: {e}")
        return []

def find_verb_in_morph_dict(verb_infinitive):
    """Find a verb and its conjugations in the morphological dictionary."""
    try:
        conn = sqlite3.connect('morph_dict.db')
        cursor = conn.cursor()
        
        # Find all forms of this verb
        cursor.execute("""
            SELECT form, lemma, pos, tense, mood, voice, person, number, aspect, verbform
            FROM words 
            WHERE lemma = ? AND pos = 'VERB'
            ORDER BY tense, mood, voice, person, number
        """, (verb_infinitive,))
        
        conjugations = cursor.fetchall()
        conn.close()
        
        return conjugations
        
    except Exception as e:
        print(f"❌ Error finding verb {verb_infinitive}: {e}")
        return []

def map_morph_to_our_schema(morph_conjugations):
    """Map morphological dictionary data to our database schema."""
    mapped_conjugations = []
    
    for conj in morph_conjugations:
        form, lemma, pos, tense, mood, voice, person, number, aspect, verbform = conj
        
        # Map tense
        tense_mapping = {
            'Pres': 'present',
            'Past': 'imperfect',  # Assuming Past is imperfect
            'Fut': 'future',
            'Perf': 'perfect',
            'Aor': 'aorist'
        }
        
        # Map mood
        mood_mapping = {
            'Ind': 'indicative',
            'Imp': 'imperative',
            'Sub': 'subjunctive'
        }
        
        # Map voice
        voice_mapping = {
            'Act': 'active',
            'Pass': 'passive',
            'Mid': 'middle'
        }
        
        # Map person
        person_mapping = {
            1: '1st',
            2: '2nd', 
            3: '3rd'
        }
        
        # Map number
        number_mapping = {
            'Sing': 'singular',
            'Plur': 'plural'
        }
        
        mapped_conj = {
            'form': form,
            'tense': tense_mapping.get(tense, tense.lower()),
            'mood': mood_mapping.get(mood, mood.lower()),
            'voice': voice_mapping.get(voice, voice.lower()),
            'person': person_mapping.get(person, str(person)),
            'number': number_mapping.get(number, number.lower()),
            'aspect': aspect,
            'verbform': verbform
        }
        
        mapped_conjugations.append(mapped_conj)
    
    return mapped_conjugations

def analyze_verb_coverage():
    """Analyze how many of our verbs are in the morphological dictionary."""
    print("🔍 Analyzing Verb Coverage in Morphological Dictionary")
    print("=" * 60)
    
    our_verbs = get_our_verbs_needing_conjugations()
    
    print(f"📊 Analyzing {len(our_verbs)} verbs that need conjugations:")
    
    found_verbs = []
    not_found = []
    
    for verb_id, infinitive, english, frequency, verb_group in our_verbs:
        conjugations = find_verb_in_morph_dict(infinitive)
        
        if conjugations:
            print(f"   ✅ {infinitive} ({english}) - {len(conjugations)} conjugations")
            found_verbs.append({
                'verb_id': verb_id,
                'infinitive': infinitive,
                'english': english,
                'frequency': frequency,
                'verb_group': verb_group,
                'conjugation_count': len(conjugations),
                'conjugations': map_morph_to_our_schema(conjugations)
            })
        else:
            print(f"   ❌ {infinitive} ({english}) - Not found")
            not_found.append(infinitive)
    
    print(f"\n📊 Summary:")
    print(f"   • Found: {len(found_verbs)} verbs")
    print(f"   • Not found: {len(not_found)} verbs")
    print(f"   • Coverage: {len(found_verbs)/len(our_verbs)*100:.1f}%")
    
    # Save results
    with open('verb_coverage_analysis.json', 'w', encoding='utf-8') as f:
        json.dump({
            'found_verbs': found_verbs,
            'not_found': not_found,
            'summary': {
                'total_analyzed': len(our_verbs),
                'found': len(found_verbs),
                'not_found': len(not_found),
                'coverage_percentage': len(found_verbs)/len(our_verbs)*100
            }
        }, f, ensure_ascii=False, indent=2)
    
    print(f"💾 Saved analysis to 'verb_coverage_analysis.json'")
    
    return found_verbs

def show_sample_conjugations(found_verbs, num_verbs=3):
    """Show sample conjugations for the first few verbs."""
    print(f"\n📝 Sample Conjugations (first {num_verbs} verbs):")
    print("=" * 60)
    
    for i, verb_data in enumerate(found_verbs[:num_verbs]):
        print(f"\n🔍 {verb_data['infinitive']} ({verb_data['english']})")
        print(f"   Frequency: {verb_data['frequency']}, Group: {verb_data['verb_group']}")
        print(f"   Total conjugations: {verb_data['conjugation_count']}")
        
        # Show sample conjugations by tense
        tenses = {}
        for conj in verb_data['conjugations']:
            tense = conj['tense']
            if tense not in tenses:
                tenses[tense] = []
            tenses[tense].append(conj)
        
        for tense, conjugations in tenses.items():
            print(f"   📚 {tense.title()} tense ({len(conjugations)} forms):")
            for conj in conjugations[:5]:  # Show first 5
                print(f"     • {conj['form']} ({conj['person']} {conj['number']} {conj['mood']} {conj['voice']})")

def main():
    """Main extraction function."""
    print("🔬 Greek Verb Conjugation Extraction")
    print("=" * 60)
    
    # Analyze verb coverage
    found_verbs = analyze_verb_coverage()
    
    if found_verbs:
        # Show sample conjugations
        show_sample_conjugations(found_verbs)
        
        print(f"\n🎯 Next Steps:")
        print(f"1. Review the conjugation data above")
        print(f"2. Check 'verb_coverage_analysis.json' for detailed results")
        print(f"3. Create import script to add conjugations to our database")
        print(f"4. Start with importing conjugations for the first 10-20 verbs")
    else:
        print(f"\n❌ No verbs found in morphological dictionary")
        print(f"   Check if the database was created correctly")

if __name__ == "__main__":
    main() 