#!/usr/bin/env python3
import sqlite3
import re
from datetime import datetime

def validate_database_integrity():
    """Comprehensive validation of the database"""
    print("🔍 Comprehensive Data Validation")
    print("=" * 50)
    
    try:
        conn = sqlite3.connect('greek-conjugator/backend/greek_conjugator_dev.db')
        cursor = conn.cursor()
        
        # 1. Basic Statistics
        print("\n📊 BASIC STATISTICS:")
        print("-" * 30)
        
        cursor.execute("SELECT COUNT(*) FROM verbs")
        total_verbs = cursor.fetchone()[0]
        print(f"Total verbs: {total_verbs}")
        
        cursor.execute("SELECT COUNT(*) FROM conjugations")
        total_conjugations = cursor.fetchone()[0]
        print(f"Total conjugations: {total_conjugations}")
        
        cursor.execute("""
            SELECT COUNT(DISTINCT v.id) 
            FROM verbs v 
            JOIN conjugations c ON v.id = c.verb_id
        """)
        verbs_with_conjugations = cursor.fetchone()[0]
        print(f"Verbs with conjugations: {verbs_with_conjugations}")
        
        # 2. Data Quality Checks
        print("\n🔍 DATA QUALITY CHECKS:")
        print("-" * 30)
        
        # Check for empty forms
        cursor.execute("SELECT COUNT(*) FROM conjugations WHERE form IS NULL OR form = ''")
        empty_forms = cursor.fetchone()[0]
        print(f"Empty forms: {empty_forms}")
        
        # Check for orphaned conjugations
        cursor.execute("""
            SELECT COUNT(*) FROM conjugations c 
            LEFT JOIN verbs v ON c.verb_id = v.id 
            WHERE v.id IS NULL
        """)
        orphaned_conjugations = cursor.fetchone()[0]
        print(f"Orphaned conjugations: {orphaned_conjugations}")
        
        # Check for duplicate conjugations
        cursor.execute("""
            SELECT verb_id, tense, mood, voice, person, number, form, COUNT(*)
            FROM conjugations 
            GROUP BY verb_id, tense, mood, voice, person, number, form
            HAVING COUNT(*) > 1
        """)
        duplicates = cursor.fetchall()
        print(f"Duplicate conjugations: {len(duplicates)}")
        
        # 3. Tense/Mood/Voice Distribution
        print("\n📊 GRAMMATICAL DISTRIBUTION:")
        print("-" * 30)
        
        cursor.execute("SELECT tense, COUNT(*) FROM conjugations GROUP BY tense ORDER BY COUNT(*) DESC")
        tense_dist = cursor.fetchall()
        print("Tense distribution:")
        for tense, count in tense_dist:
            print(f"  {tense}: {count}")
        
        cursor.execute("SELECT mood, COUNT(*) FROM conjugations GROUP BY mood ORDER BY COUNT(*) DESC")
        mood_dist = cursor.fetchall()
        print("Mood distribution:")
        for mood, count in mood_dist:
            print(f"  {mood}: {count}")
        
        cursor.execute("SELECT voice, COUNT(*) FROM conjugations GROUP BY voice ORDER BY COUNT(*) DESC")
        voice_dist = cursor.fetchall()
        print("Voice distribution:")
        for voice, count in voice_dist:
            print(f"  {voice}: {count}")
        
        # 4. Verb Coverage Analysis
        print("\n📊 VERB COVERAGE ANALYSIS:")
        print("-" * 30)
        
        cursor.execute("""
            SELECT 
                CASE 
                    WHEN conjugation_count >= 100 THEN 'Excellent (100+)'
                    WHEN conjugation_count >= 50 THEN 'Good (50-99)'
                    WHEN conjugation_count >= 20 THEN 'Fair (20-49)'
                    ELSE 'Poor (<20)'
                END as coverage_level,
                COUNT(*) as verb_count
            FROM (
                SELECT v.infinitive, COUNT(c.id) as conjugation_count
                FROM verbs v 
                LEFT JOIN conjugations c ON v.id = c.verb_id
                GROUP BY v.id, v.infinitive
            )
            GROUP BY coverage_level
            ORDER BY verb_count DESC
        """)
        coverage_analysis = cursor.fetchall()
        print("Verb coverage levels:")
        for level, count in coverage_analysis:
            print(f"  {level}: {count} verbs")
        
        # 5. Sample Quality Check
        print("\n📝 SAMPLE QUALITY CHECK:")
        print("-" * 30)
        
        # Sample verbs with high conjugation counts
        cursor.execute("""
            SELECT v.infinitive, COUNT(c.id) as conjugation_count
            FROM verbs v 
            JOIN conjugations c ON v.id = c.verb_id
            GROUP BY v.id, v.infinitive
            ORDER BY conjugation_count DESC
            LIMIT 5
        """)
        top_verbs = cursor.fetchall()
        print("Top 5 verbs by conjugation count:")
        for verb, count in top_verbs:
            print(f"  {verb}: {count} conjugations")
        
        # Sample conjugations for quality check
        cursor.execute("""
            SELECT v.infinitive, c.tense, c.mood, c.voice, c.person, c.number, c.form
            FROM verbs v 
            JOIN conjugations c ON v.id = c.verb_id
            ORDER BY RANDOM()
            LIMIT 10
        """)
        sample_conjugations = cursor.fetchall()
        print("\nSample conjugations (random):")
        for row in sample_conjugations:
            infinitive, tense, mood, voice, person, number, form = row
            print(f"  {infinitive}: {form} ({tense} {mood} {voice} {person} {number})")
        
        # 6. Data Consistency Checks
        print("\n🔍 DATA CONSISTENCY CHECKS:")
        print("-" * 30)
        
        # Check for invalid tense values
        cursor.execute("SELECT DISTINCT tense FROM conjugations WHERE tense NOT IN ('present', 'imperfect', 'future', 'perfect', 'aorist')")
        invalid_tenses = cursor.fetchall()
        print(f"Invalid tense values: {len(invalid_tenses)}")
        if invalid_tenses:
            print(f"  Found: {[t[0] for t in invalid_tenses]}")
        
        # Check for invalid mood values
        cursor.execute("SELECT DISTINCT mood FROM conjugations WHERE mood NOT IN ('indicative', 'imperative', 'subjunctive')")
        invalid_moods = cursor.fetchall()
        print(f"Invalid mood values: {len(invalid_moods)}")
        if invalid_moods:
            print(f"  Found: {[m[0] for m in invalid_moods]}")
        
        # Check for invalid voice values
        cursor.execute("SELECT DISTINCT voice FROM conjugations WHERE voice NOT IN ('active', 'passive')")
        invalid_voices = cursor.fetchall()
        print(f"Invalid voice values: {len(invalid_voices)}")
        if invalid_voices:
            print(f"  Found: {[v[0] for v in invalid_voices]}")
        
        # 7. Performance Indicators
        print("\n⚡ PERFORMANCE INDICATORS:")
        print("-" * 30)
        
        avg_conjugations = total_conjugations / verbs_with_conjugations if verbs_with_conjugations > 0 else 0
        print(f"Average conjugations per verb: {avg_conjugations:.1f}")
        
        coverage_percentage = (verbs_with_conjugations / total_verbs) * 100 if total_verbs > 0 else 0
        print(f"Verb coverage percentage: {coverage_percentage:.1f}%")
        
        # 8. Overall Assessment
        print("\n✅ OVERALL ASSESSMENT:")
        print("-" * 30)
        
        issues = []
        if empty_forms > 0:
            issues.append(f"Empty forms: {empty_forms}")
        if orphaned_conjugations > 0:
            issues.append(f"Orphaned conjugations: {orphaned_conjugations}")
        if len(duplicates) > 0:
            issues.append(f"Duplicate conjugations: {len(duplicates)}")
        if len(invalid_tenses) > 0:
            issues.append(f"Invalid tenses: {len(invalid_tenses)}")
        if len(invalid_moods) > 0:
            issues.append(f"Invalid moods: {len(invalid_moods)}")
        if len(invalid_voices) > 0:
            issues.append(f"Invalid voices: {len(invalid_voices)}")
        
        if not issues:
            print("✅ Data is clean and ready for production!")
            print("✅ No data integrity issues found")
            print("✅ All conjugations are properly formatted")
            print("✅ Database is ready for app deployment")
        else:
            print("⚠️  Issues found that need attention:")
            for issue in issues:
                print(f"  - {issue}")
        
        conn.close()
        
        return len(issues) == 0
        
    except Exception as e:
        print(f"❌ Validation error: {e}")
        return False

if __name__ == "__main__":
    is_ready = validate_database_integrity()
    
    if is_ready:
        print("\n🎉 VALIDATION COMPLETE - DATABASE IS READY!")
    else:
        print("\n⚠️  VALIDATION COMPLETE - ISSUES FOUND") 