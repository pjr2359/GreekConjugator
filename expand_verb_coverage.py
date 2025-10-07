#!/usr/bin/env python3
import sqlite3
import json
from datetime import datetime

def get_common_greek_verbs():
    """Get a list of common Greek verbs from the morphological dictionary"""
    try:
        conn = sqlite3.connect('morph_dict.db')
        cursor = conn.cursor()
        
        # Get verbs with high conjugation counts (indicating they're common/complete)
        cursor.execute("""
            SELECT lemma, COUNT(*) as form_count
            FROM words 
            WHERE pos = 'VERB' AND verbform = 'Fin'
            GROUP BY lemma
            HAVING form_count >= 20  -- Lowered threshold to get more verbs
            ORDER BY form_count DESC
            LIMIT 500  -- Increased limit for more comprehensive coverage
        """)
        
        common_verbs = cursor.fetchall()
        conn.close()
        
        return common_verbs
        
    except Exception as e:
        print(f"❌ Error getting common verbs: {e}")
        return []

def get_existing_verbs():
    """Get list of verbs already in the app database"""
    try:
        conn = sqlite3.connect('greek-conjugator/backend/greek_conjugator_dev.db')
        cursor = conn.cursor()
        cursor.execute("SELECT infinitive FROM verbs")
        existing = [row[0] for row in cursor.fetchall()]
        conn.close()
        return existing
    except Exception as e:
        print(f"❌ Error getting existing verbs: {e}")
        return []

def extract_verb_conjugations(lemma):
    """Extract all finite forms for a given lemma"""
    try:
        conn = sqlite3.connect('morph_dict.db')
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT form, lemma, tense, mood, voice, person, number, aspect, verbform, greek_pos
            FROM words 
            WHERE lemma = ? AND pos = 'VERB' AND verbform = 'Fin'
            ORDER BY tense, mood, voice, person, number
        """, (lemma,))
        
        conjugations = cursor.fetchall()
        conn.close()
        
        forms = []
        for conj in conjugations:
            form, lemma, tense, mood, voice, person, number, aspect, verbform, greek_pos = conj
            forms.append({
                'form': form,
                'lemma': lemma,
                'tense': tense,
                'mood': mood,
                'voice': voice,
                'person': person,
                'number': number,
                'aspect': aspect,
                'verbform': verbform,
                'greek_pos': greek_pos
            })
        
        return forms
        
    except Exception as e:
        print(f"❌ Error extracting forms for {lemma}: {e}")
        return []

def map_tense_mood(tense, mood, aspect, greek_pos):
    """Map morphological dictionary fields to app schema"""
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
        return "present", "indicative"

def map_voice(greek_pos):
    """Map voice from greek_pos"""
    if "Pass" in greek_pos or "PP" in greek_pos:
        return "passive"
    else:
        return "active"

def map_person_number(person, number):
    """Map person and number to match app's schema"""
    person_map = {1: "1st", 2: "2nd", 3: "3rd"}
    number_map = {"Sing": "singular", "Plur": "plural"}
    
    return person_map.get(person, "1st"), number_map.get(number, "singular")

def expand_verb_coverage():
    """Expand verb coverage by adding more common verbs from morphological dictionary"""
    print("🚀 Expanding Verb Coverage")
    print("=" * 50)
    
    # Get common verbs from dictionary
    common_verbs = get_common_greek_verbs()
    print(f"📋 Found {len(common_verbs)} common verbs in morphological dictionary")
    
    # Get existing verbs
    existing_verbs = get_existing_verbs()
    print(f"📋 Found {len(existing_verbs)} existing verbs in app database")
    
    # Filter out verbs that already exist
    new_verbs = []
    for lemma, form_count in common_verbs:
        # Check if this lemma or a similar form already exists
        exists = False
        for existing in existing_verbs:
            if lemma in existing or existing.startswith(lemma):
                exists = True
                break
        
        if not exists:
            new_verbs.append((lemma, form_count))
    
    print(f"✅ Found {len(new_verbs)} new verbs to add")
    
    if not new_verbs:
        print("❌ No new verbs to add!")
        return
    
    # Add new verbs (limit to top 400 for comprehensive coverage)
    verbs_to_add = new_verbs[:400]
    
    try:
        conn = sqlite3.connect('greek-conjugator/backend/greek_conjugator_dev.db')
        cursor = conn.cursor()
        
        added_verbs = 0
        added_conjugations = 0
        
        for lemma, form_count in verbs_to_add:
            print(f"\n🔍 Processing: {lemma} ({form_count} forms)")
            
            # Add verb to database
            try:
                cursor.execute("""
                    INSERT INTO verbs (infinitive, english, verb_group, frequency, difficulty)
                    VALUES (?, ?, ?, ?, ?)
                """, (lemma, f"to {lemma}", "A", 5, 3))
                
                verb_id = cursor.lastrowid
                added_verbs += 1
                
                # Extract and add conjugations
                finite_forms = extract_verb_conjugations(lemma)
                forms_added = 0
                
                for form_data in finite_forms:
                    tense, mood = map_tense_mood(
                        form_data['tense'], 
                        form_data['mood'], 
                        form_data['aspect'], 
                        form_data['greek_pos']
                    )
                    voice = map_voice(form_data['greek_pos'])
                    person, number = map_person_number(form_data['person'], form_data['number'])
                    
                    try:
                        cursor.execute("""
                            INSERT INTO conjugations 
                            (verb_id, tense, mood, voice, person, number, form)
                            VALUES (?, ?, ?, ?, ?, ?, ?)
                        """, (
                            verb_id,
                            tense,
                            mood,
                            voice,
                            person,
                            number,
                            form_data['form']
                        ))
                        forms_added += 1
                        added_conjugations += 1
                    except sqlite3.IntegrityError:
                        pass  # Skip duplicates
                
                print(f"   ✅ Added {forms_added} conjugations")
                
            except sqlite3.IntegrityError:
                print(f"   ⚠️  Verb already exists: {lemma}")
            except Exception as e:
                print(f"   ❌ Error adding {lemma}: {e}")
        
        # Commit changes
        conn.commit()
        conn.close()
        
        print(f"\n📊 Expansion Summary:")
        print(f"   New verbs added: {added_verbs}")
        print(f"   New conjugations added: {added_conjugations}")
        
        return True
        
    except Exception as e:
        print(f"❌ Expansion error: {e}")
        return False

if __name__ == "__main__":
    expand_verb_coverage() 