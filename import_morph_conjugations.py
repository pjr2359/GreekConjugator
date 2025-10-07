#!/usr/bin/env python3
import sqlite3
import json
from datetime import datetime

def map_tense_mood(tense, mood, aspect, greek_pos):
    """Map the morphological dictionary fields to our app's tense/mood schema"""
    if tense == "Pres" and mood == "Ind":
        return "present", "indicative"
    elif tense == "Past" and mood == "Ind":
        return "imperfect", "indicative"
    elif tense is None and mood == "Imp":
        return "present", "imperative"
    elif tense is None and mood == "Ind" and aspect == "Perf":
        return "future", "indicative"
    elif tense is None and mood == "Ind" and "AOR_YPOT" in greek_pos:
        return "aorist", "subjunctive"
    elif tense is None and mood == "Ind" and "AOR" in greek_pos:
        return "aorist", "indicative"
    else:
        # Default mapping for unclear cases
        return "present", "indicative"

def map_voice(greek_pos):
    """Map voice from greek_pos or other indicators"""
    if "Pass" in greek_pos or "PP" in greek_pos:
        return "passive"
    else:
        return "active"

def map_person_number(person, number):
    """Map person and number to match app's schema"""
    person_map = {1: "1st", 2: "2nd", 3: "3rd"}
    number_map = {"Sing": "singular", "Plur": "plural"}
    
    return person_map.get(person, "1st"), number_map.get(number, "singular")

def import_conjugations(json_file):
    """Import conjugations from JSON file into the app database"""
    print("🚀 Importing Morphological Dictionary Conjugations")
    print("=" * 60)
    
    try:
        # Load JSON data
        with open(json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        print(f"📋 Loaded {len(data)} verbs from JSON file")
        
        # Connect to app database
        conn = sqlite3.connect('greek-conjugator/backend/greek_conjugator_dev.db')
        cursor = conn.cursor()
        
        # Get existing verb IDs for mapping
        cursor.execute("SELECT id, infinitive FROM verbs")
        verb_mapping = {row[1]: row[0] for row in cursor.fetchall()}
        
        print(f"📋 Found {len(verb_mapping)} verbs in app database")
        
        # Track statistics
        total_imported = 0
        verbs_processed = 0
        verbs_with_conjugations = 0
        
        for verb_data in data:
            lemma = verb_data['lemma']
            finite_forms = verb_data['finite_forms']
            
            # Find matching verb in app database
            matching_verb_id = None
            for infinitive, verb_id in verb_mapping.items():
                if lemma in infinitive or infinitive.startswith(lemma):
                    matching_verb_id = verb_id
                    break
            
            if not matching_verb_id:
                print(f"⚠️  No match found for lemma: {lemma}")
                continue
            
            verbs_processed += 1
            forms_imported = 0
            
            for form_data in finite_forms:
                # Map fields to our schema
                tense, mood = map_tense_mood(
                    form_data['tense'], 
                    form_data['mood'], 
                    form_data['aspect'], 
                    form_data['greek_pos']
                )
                voice = map_voice(form_data['greek_pos'])
                
                # Map person and number
                person, number = map_person_number(form_data['person'], form_data['number'])
                
                # Insert conjugation
                try:
                    cursor.execute("""
                        INSERT INTO conjugations 
                        (verb_id, tense, mood, voice, person, number, form)
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                    """, (
                        matching_verb_id,
                        tense,
                        mood,
                        voice,
                        person,
                        number,
                        form_data['form']
                    ))
                    forms_imported += 1
                    total_imported += 1
                except sqlite3.IntegrityError:
                    # Skip duplicates
                    pass
                except Exception as e:
                    print(f"❌ Error importing form {form_data['form']} for {lemma}: {e}")
            
            if forms_imported > 0:
                verbs_with_conjugations += 1
                print(f"✅ {lemma}: imported {forms_imported} forms")
        
        # Commit changes
        conn.commit()
        conn.close()
        
        print(f"\n📊 Import Summary:")
        print(f"   Verbs processed: {verbs_processed}")
        print(f"   Verbs with conjugations imported: {verbs_with_conjugations}")
        print(f"   Total forms imported: {total_imported}")
        
        return True
        
    except Exception as e:
        print(f"❌ Import error: {e}")
        return False

def validate_import():
    """Validate the imported data"""
    print("\n🔍 Validating Imported Data")
    print("=" * 40)
    
    try:
        conn = sqlite3.connect('greek-conjugator/backend/greek_conjugator_dev.db')
        cursor = conn.cursor()
        
        # Count total conjugations
        cursor.execute("SELECT COUNT(*) FROM conjugations")
        total_conjugations = cursor.fetchone()[0]
        print(f"📊 Total conjugations in database: {total_conjugations}")
        
        # Count verbs with conjugations
        cursor.execute("""
            SELECT COUNT(DISTINCT v.id) 
            FROM verbs v 
            JOIN conjugations c ON v.id = c.verb_id
        """)
        verbs_with_conjugations = cursor.fetchone()[0]
        print(f"📊 Verbs with conjugations: {verbs_with_conjugations}")
        
        # Sample of imported data
        cursor.execute("""
            SELECT v.infinitive, c.tense, c.mood, c.voice, c.person, c.number, c.form
            FROM verbs v 
            JOIN conjugations c ON v.id = c.verb_id
            ORDER BY v.infinitive, c.tense, c.mood, c.voice, c.person, c.number
            LIMIT 10
        """)
        
        sample_data = cursor.fetchall()
        print(f"\n📝 Sample imported conjugations:")
        for row in sample_data:
            infinitive, tense, mood, voice, person, number, form = row
            print(f"   {infinitive}: {form} ({tense} {mood} {voice} {person} {number})")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Validation error: {e}")

if __name__ == "__main__":
    # Import the latest extraction file
    import_success = import_conjugations("morph_extraction_matched_20250716_190035.json")
    
    if import_success:
        validate_import()
    else:
        print("❌ Import failed, skipping validation") 