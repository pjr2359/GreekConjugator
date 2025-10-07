#!/usr/bin/env python3
import sqlite3
import json
import re
from datetime import datetime

def extract_greek_lemma(infinitive):
    """Extract the Greek lemma from the infinitive field (before any parenthesis or explanation)."""
    lemma = re.split(r'[\s(]', infinitive)[0]
    return lemma.strip()

def get_app_lemmas():
    """Get a set of unique lemmas from the app's verbs table (cleaned)."""
    try:
        conn = sqlite3.connect('greek-conjugator/backend/greek_conjugator_dev.db')
        cursor = conn.cursor()
        cursor.execute("SELECT infinitive FROM verbs")
        infinitives = [row[0] for row in cursor.fetchall()]
        conn.close()
        # Clean to get only the lemma part
        lemmas = set(extract_greek_lemma(inf) for inf in infinitives)
        return lemmas
    except Exception as e:
        print(f"❌ Error getting app lemmas: {e}")
        return set()

def get_dict_lemmas():
    """Get a set of unique lemmas from the morphological dictionary."""
    try:
        conn = sqlite3.connect('morph_dict.db')
        cursor = conn.cursor()
        cursor.execute("SELECT DISTINCT lemma FROM words WHERE pos = 'VERB'")
        dict_lemmas = set(row[0] for row in cursor.fetchall())
        conn.close()
        return dict_lemmas
    except Exception as e:
        print(f"❌ Error getting dictionary lemmas: {e}")
        return set()

def extract_finite_forms(lemma):
    """Extract all finite forms for a given lemma from morphological dictionary"""
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

def bulk_extract_matched_lemmas():
    print("🚀 Bulk Extraction - App Lemmas Matched to Dictionary")
    print("=" * 60)
    app_lemmas = get_app_lemmas()
    print(f"📋 App verb lemmas: {len(app_lemmas)}")
    dict_lemmas = get_dict_lemmas()
    print(f"📋 Dictionary verb lemmas: {len(dict_lemmas)}")
    matched_lemmas = sorted(app_lemmas & dict_lemmas)
    print(f"✅ Matched lemmas: {len(matched_lemmas)}")
    extraction_results = []
    for i, lemma in enumerate(matched_lemmas, 1):
        print(f"\n🔍 [{i}/{len(matched_lemmas)}] Extracting: {lemma}")
        finite_forms = extract_finite_forms(lemma)
        extraction_results.append({
            'lemma': lemma,
            'finite_forms_count': len(finite_forms),
            'finite_forms': finite_forms
        })
        print(f"   ✅ Found {len(finite_forms)} finite forms")
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"morph_extraction_matched_{timestamp}.json"
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(extraction_results, f, ensure_ascii=False, indent=2)
    print(f"\n�� Extraction Summary:")
    print(f"   Total matched lemmas: {len(matched_lemmas)}")
    total_forms = sum(r['finite_forms_count'] for r in extraction_results)
    print(f"   Total finite forms extracted: {total_forms}")
    avg_forms = total_forms / len(extraction_results) if extraction_results else 0
    print(f"   Average forms per lemma: {avg_forms:.1f}")
    print(f"\n💾 Results exported to: {filename}")
    print(f"\n📝 Sample extraction results:")
    for i, result in enumerate(extraction_results[:3], 1):
        print(f"   {i}. {result['lemma']}: {result['finite_forms_count']} forms")
        if result['finite_forms']:
            sample_forms = result['finite_forms'][:3]
            for form in sample_forms:
                print(f"      - {form['form']} ({form['tense']} {form['mood']} {form['voice']} {form['person']} {form['number']})")

if __name__ == "__main__":
    bulk_extract_matched_lemmas() 