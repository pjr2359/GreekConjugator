#!/usr/bin/env python3
"""
Database Integrity Test Suite for Greek Conjugator

This test suite verifies that all verbs and conjugations from the extracted_verbs.json
file have been properly imported into the database with correct relationships and data integrity.
"""

import sys
import os
import json
from collections import defaultdict, Counter
from typing import Dict, List, Set, Tuple

# Add the project directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from app.models import db, Verb, Conjugation

class DatabaseIntegrityChecker:
    def __init__(self):
        self.app = create_app()
        self.extracted_verbs_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            'extracted_verbs.json'
        )
        self.stats = {
            'total_verbs_in_json': 0,
            'total_conjugations_in_json': 0,
            'verbs_in_database': 0,
            'conjugations_in_database': 0,
            'missing_verbs': [],
            'missing_conjugations': [],
            'data_quality_issues': [],
            'verb_groups': Counter(),
            'tense_distribution': Counter(),
            'mood_distribution': Counter(),
            'voice_distribution': Counter()
        }

    def load_extracted_verbs(self) -> Dict:
        """Load the extracted verbs from JSON file."""
        try:
            with open(self.extracted_verbs_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"❌ Error: {self.extracted_verbs_path} not found!")
            return {}
        except json.JSONDecodeError as e:
            print(f"❌ Error parsing JSON: {e}")
            return {}

    def check_verb_coverage(self, extracted_verbs: Dict) -> None:
        """Check if all verbs from JSON are in the database."""
        print("\n🔍 Checking verb coverage...")
        
        with self.app.app_context():
            # Get all verbs from database
            db_verbs = Verb.query.all()
            db_verb_infinitives = {verb.infinitive for verb in db_verbs}
            
            # Count verbs in JSON
            self.stats['total_verbs_in_json'] = len(extracted_verbs)
            self.stats['verbs_in_database'] = len(db_verbs)
            
            # Find missing verbs
            json_verb_infinitives = set(extracted_verbs.keys())
            missing_verbs = json_verb_infinitives - db_verb_infinitives
            
            if missing_verbs:
                self.stats['missing_verbs'] = list(missing_verbs)
                print(f"⚠️  Found {len(missing_verbs)} missing verbs:")
                for verb in sorted(list(missing_verbs))[:10]:  # Show first 10
                    print(f"   - {verb}")
                if len(missing_verbs) > 10:
                    print(f"   ... and {len(missing_verbs) - 10} more")
            else:
                print("✅ All verbs from JSON are in the database!")

    def check_conjugation_coverage(self, extracted_verbs: Dict) -> None:
        """Check if all conjugations from JSON are in the database."""
        print("\n🔍 Checking conjugation coverage...")
        
        with self.app.app_context():
            # Get all conjugations from database
            db_conjugations = Conjugation.query.all()
            self.stats['conjugations_in_database'] = len(db_conjugations)
            
            # Count total conjugations in JSON
            total_json_conjugations = sum(
                len(verb_data.get('conjugations', [])) 
                for verb_data in extracted_verbs.values()
            )
            self.stats['total_conjugations_in_json'] = total_json_conjugations
            
            # Check each verb's conjugations
            missing_conjugations = []
            
            for verb_infinitive, verb_data in extracted_verbs.items():
                json_conjugations = verb_data.get('conjugations', [])
                
                # Get verb from database
                db_verb = Verb.query.filter_by(infinitive=verb_infinitive).first()
                if not db_verb:
                    continue
                
                # Get conjugations for this verb from database
                db_verb_conjugations = Conjugation.query.filter_by(verb_id=db_verb.id).all()
                db_conjugation_forms = {c.form for c in db_verb_conjugations}
                
                # Check for missing conjugations
                for conj in json_conjugations:
                    if conj.get('form') and conj['form'] not in db_conjugation_forms:
                        missing_conjugations.append({
                            'verb': verb_infinitive,
                            'form': conj['form'],
                            'tense': conj.get('tense'),
                            'mood': conj.get('mood'),
                            'voice': conj.get('voice')
                        })
            
            if missing_conjugations:
                self.stats['missing_conjugations'] = missing_conjugations
                print(f"⚠️  Found {len(missing_conjugations)} missing conjugations:")
                for conj in missing_conjugations[:10]:  # Show first 10
                    print(f"   - {conj['verb']}: {conj['form']} ({conj['tense']} {conj['mood']} {conj['voice']})")
                if len(missing_conjugations) > 10:
                    print(f"   ... and {len(missing_conjugations) - 10} more")
            else:
                print("✅ All conjugations from JSON are in the database!")

    def check_data_quality(self) -> None:
        """Check data quality and consistency."""
        print("\n🔍 Checking data quality...")
        
        with self.app.app_context():
            # Check for verbs without conjugations
            verbs_without_conjugations = []
            for verb in Verb.query.all():
                conjugation_count = Conjugation.query.filter_by(verb_id=verb.id).count()
                if conjugation_count == 0:
                    verbs_without_conjugations.append(verb.infinitive)
            
            if verbs_without_conjugations:
                self.stats['data_quality_issues'].append({
                    'type': 'verbs_without_conjugations',
                    'count': len(verbs_without_conjugations),
                    'verbs': verbs_without_conjugations
                })
                print(f"⚠️  Found {len(verbs_without_conjugations)} verbs without conjugations")
            
            # Check for orphaned conjugations
            orphaned_conjugations = []
            for conjugation in Conjugation.query.all():
                verb = Verb.query.get(conjugation.verb_id)
                if not verb:
                    orphaned_conjugations.append(conjugation.id)
            
            if orphaned_conjugations:
                self.stats['data_quality_issues'].append({
                    'type': 'orphaned_conjugations',
                    'count': len(orphaned_conjugations),
                    'ids': orphaned_conjugations
                })
                print(f"⚠️  Found {len(orphaned_conjugations)} orphaned conjugations")
            
            # Check for duplicate conjugations
            duplicate_conjugations = []
            seen_conjugations = set()
            
            for conjugation in Conjugation.query.all():
                key = (conjugation.verb_id, conjugation.form, conjugation.tense, 
                      conjugation.mood, conjugation.voice)
                if key in seen_conjugations:
                    duplicate_conjugations.append(conjugation.id)
                else:
                    seen_conjugations.add(key)
            
            if duplicate_conjugations:
                self.stats['data_quality_issues'].append({
                    'type': 'duplicate_conjugations',
                    'count': len(duplicate_conjugations),
                    'ids': duplicate_conjugations
                })
                print(f"⚠️  Found {len(duplicate_conjugations)} duplicate conjugations")
            
            if not self.stats['data_quality_issues']:
                print("✅ No data quality issues found!")

    def analyze_database_statistics(self) -> None:
        """Analyze database statistics and distributions."""
        print("\n📊 Analyzing database statistics...")
        
        with self.app.app_context():
            # Verb group distribution
            for verb in Verb.query.all():
                if verb.verb_group:
                    self.stats['verb_groups'][verb.verb_group] += 1
            
            # Conjugation distributions
            for conjugation in Conjugation.query.all():
                if conjugation.tense:
                    self.stats['tense_distribution'][conjugation.tense] += 1
                if conjugation.mood:
                    self.stats['mood_distribution'][conjugation.mood] += 1
                if conjugation.voice:
                    self.stats['voice_distribution'][conjugation.voice] += 1

    def generate_coverage_report(self) -> None:
        """Generate a comprehensive coverage report."""
        print("\n" + "="*60)
        print("📋 DATABASE INTEGRITY REPORT")
        print("="*60)
        
        # Basic statistics
        print(f"\n📈 BASIC STATISTICS:")
        print(f"   • Total verbs in JSON: {self.stats['total_verbs_in_json']}")
        print(f"   • Total verbs in database: {self.stats['verbs_in_database']}")
        print(f"   • Total conjugations in JSON: {self.stats['total_conjugations_in_json']}")
        print(f"   • Total conjugations in database: {self.stats['conjugations_in_database']}")
        
        # Coverage percentages
        if self.stats['total_verbs_in_json'] > 0:
            verb_coverage = (self.stats['verbs_in_database'] / self.stats['total_verbs_in_json']) * 100
            print(f"   • Verb coverage: {verb_coverage:.1f}%")
        
        if self.stats['total_conjugations_in_json'] > 0:
            conj_coverage = (self.stats['conjugations_in_database'] / self.stats['total_conjugations_in_json']) * 100
            print(f"   • Conjugation coverage: {conj_coverage:.1f}%")
        
        # Missing data
        if self.stats['missing_verbs']:
            print(f"\n❌ MISSING VERBS: {len(self.stats['missing_verbs'])}")
        
        if self.stats['missing_conjugations']:
            print(f"\n❌ MISSING CONJUGATIONS: {len(self.stats['missing_conjugations'])}")
        
        # Data quality issues
        if self.stats['data_quality_issues']:
            print(f"\n⚠️  DATA QUALITY ISSUES:")
            for issue in self.stats['data_quality_issues']:
                print(f"   • {issue['type']}: {issue['count']} items")
        
        # Distributions
        if self.stats['verb_groups']:
            print(f"\n📊 VERB GROUP DISTRIBUTION:")
            for group, count in self.stats['verb_groups'].most_common():
                print(f"   • {group}: {count}")
        
        if self.stats['tense_distribution']:
            print(f"\n📊 TENSE DISTRIBUTION:")
            for tense, count in self.stats['tense_distribution'].most_common():
                print(f"   • {tense}: {count}")
        
        if self.stats['mood_distribution']:
            print(f"\n📊 MOOD DISTRIBUTION:")
            for mood, count in self.stats['mood_distribution'].most_common():
                print(f"   • {mood}: {count}")
        
        if self.stats['voice_distribution']:
            print(f"\n📊 VOICE DISTRIBUTION:")
            for voice, count in self.stats['voice_distribution'].most_common():
                print(f"   • {voice}: {count}")
        
        print("\n" + "="*60)

    def run_all_checks(self) -> Dict:
        """Run all integrity checks and return results."""
        print("🚀 Starting Database Integrity Check...")
        
        # Load extracted verbs
        extracted_verbs = self.load_extracted_verbs()
        if not extracted_verbs:
            print("❌ Failed to load extracted verbs. Exiting.")
            return self.stats
        
        # Run all checks
        self.check_verb_coverage(extracted_verbs)
        self.check_conjugation_coverage(extracted_verbs)
        self.check_data_quality()
        self.analyze_database_statistics()
        self.generate_coverage_report()
        
        return self.stats

def main():
    """Main function to run the integrity checker."""
    checker = DatabaseIntegrityChecker()
    results = checker.run_all_checks()
    
    # Exit with error code if there are issues
    if (checker.stats['missing_verbs'] or 
        checker.stats['missing_conjugations'] or 
        checker.stats['data_quality_issues']):
        print("\n❌ Database integrity check failed!")
        return 1
    else:
        print("\n✅ Database integrity check passed!")
        return 0

if __name__ == '__main__':
    exit(main()) 