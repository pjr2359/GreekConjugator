#!/usr/bin/env python3
"""
Conjugation Completeness Test for Greek Conjugator

This test focuses specifically on checking that all expected conjugations
are present and correctly formatted according to Greek grammar rules.
"""

import sys
import os
import json
from collections import defaultdict
from typing import Dict, List, Set, Tuple

# Add the project directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from app.models import db, Verb, Conjugation

class ConjugationCompletenessChecker:
    def __init__(self):
        self.app = create_app()
        self.extracted_verbs_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            'extracted_verbs.json'
        )
        
        # Expected conjugation patterns for Greek verbs
        self.expected_conjugation_patterns = {
            'present_indicative_active': {
                'tense': 'present',
                'mood': 'indicative', 
                'voice': 'active',
                'expected_forms': 6,  # 1st, 2nd, 3rd singular + 1st, 2nd, 3rd plural
                'persons': ['1st', '2nd', '3rd'],
                'numbers': ['singular', 'plural']
            },
            'present_indicative_passive': {
                'tense': 'present',
                'mood': 'indicative',
                'voice': 'passive', 
                'expected_forms': 6,
                'persons': ['1st', '2nd', '3rd'],
                'numbers': ['singular', 'plural']
            },
            'aorist_indicative_active': {
                'tense': 'aorist',
                'mood': 'indicative',
                'voice': 'active',
                'expected_forms': 6,
                'persons': ['1st', '2nd', '3rd'],
                'numbers': ['singular', 'plural']
            },
            'aorist_indicative_passive': {
                'tense': 'aorist',
                'mood': 'indicative',
                'voice': 'passive',
                'expected_forms': 6,
                'persons': ['1st', '2nd', '3rd'],
                'numbers': ['singular', 'plural']
            },
            'imperfect_indicative_active': {
                'tense': 'imperfect',
                'mood': 'indicative',
                'voice': 'active',
                'expected_forms': 6,
                'persons': ['1st', '2nd', '3rd'],
                'numbers': ['singular', 'plural']
            },
            'future_indicative_active': {
                'tense': 'future',
                'mood': 'indicative',
                'voice': 'active',
                'expected_forms': 6,
                'persons': ['1st', '2nd', '3rd'],
                'numbers': ['singular', 'plural']
            },
            'present_subjunctive_active': {
                'tense': 'present',
                'mood': 'subjunctive',
                'voice': 'active',
                'expected_forms': 6,
                'persons': ['1st', '2nd', '3rd'],
                'numbers': ['singular', 'plural']
            },
            'present_imperative_active': {
                'tense': 'present',
                'mood': 'imperative',
                'voice': 'active',
                'expected_forms': 4,  # Usually 2nd singular, 2nd plural, 3rd singular, 3rd plural
                'persons': ['2nd', '3rd'],
                'numbers': ['singular', 'plural']
            }
        }
        
        self.results = {
            'total_verbs_checked': 0,
            'verbs_with_complete_conjugations': 0,
            'verbs_with_incomplete_conjugations': [],
            'verbs_with_incorrect_forms': [],
            'missing_tense_mood_voice_combinations': [],
            'statistics': defaultdict(int)
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

    def check_verb_conjugation_completeness(self, verb_infinitive: str, verb_data: Dict) -> Dict:
        """Check if a specific verb has complete conjugations."""
        with self.app.app_context():
            # Get verb from database
            db_verb = Verb.query.filter_by(infinitive=verb_infinitive).first()
            if not db_verb:
                return {'status': 'missing_verb', 'issues': [f'Verb {verb_infinitive} not found in database']}
            
            # Get all conjugations for this verb
            db_conjugations = Conjugation.query.filter_by(verb_id=db_verb.id).all()
            
            issues = []
            completeness_score = 0
            total_expected_forms = 0
            
            # Check each expected conjugation pattern
            for pattern_name, pattern in self.expected_conjugation_patterns.items():
                expected_forms = pattern['expected_forms']
                total_expected_forms += expected_forms
                
                # Find conjugations matching this pattern
                matching_conjugations = [
                    c for c in db_conjugations
                    if (c.tense == pattern['tense'] and 
                        c.mood == pattern['mood'] and 
                        c.voice == pattern['voice'])
                ]
                
                if len(matching_conjugations) == 0:
                    issues.append(f'Missing {pattern_name} conjugations')
                elif len(matching_conjugations) < expected_forms:
                    issues.append(f'Incomplete {pattern_name}: {len(matching_conjugations)}/{expected_forms} forms')
                else:
                    completeness_score += expected_forms
                    
                    # Check for correct person/number combinations
                    person_number_combinations = set()
                    for conj in matching_conjugations:
                        if conj.person and conj.number:
                            person_number_combinations.add((conj.person, conj.number))
                    
                    # Check if we have the expected person/number combinations
                    expected_combinations = set()
                    for person in pattern['persons']:
                        for number in pattern['numbers']:
                            expected_combinations.add((person, number))
                    
                    missing_combinations = expected_combinations - person_number_combinations
                    if missing_combinations:
                        issues.append(f'Missing person/number combinations in {pattern_name}: {missing_combinations}')
            
            # Calculate completeness percentage
            completeness_percentage = (completeness_score / total_expected_forms * 100) if total_expected_forms > 0 else 0
            
            return {
                'status': 'complete' if not issues else 'incomplete',
                'completeness_percentage': completeness_percentage,
                'total_conjugations': len(db_conjugations),
                'expected_forms': total_expected_forms,
                'issues': issues
            }

    def validate_conjugation_forms(self, verb_infinitive: str, verb_data: Dict) -> List[str]:
        """Validate that conjugation forms are grammatically correct."""
        with self.app.app_context():
            db_verb = Verb.query.filter_by(infinitive=verb_infinitive).first()
            if not db_verb:
                return [f'Verb {verb_infinitive} not found in database']
            
            db_conjugations = Conjugation.query.filter_by(verb_id=db_verb.id).all()
            issues = []
            
            # Basic validation rules
            for conjugation in db_conjugations:
                # Check for empty forms
                if not conjugation.form or conjugation.form.strip() == '':
                    issues.append(f'Empty conjugation form for {verb_infinitive}')
                    continue
                
                # Check for forms that are too short (likely incomplete)
                if len(conjugation.form.strip()) < 2:
                    issues.append(f'Suspiciously short form "{conjugation.form}" for {verb_infinitive}')
                
                # Check for forms with only punctuation or numbers
                if conjugation.form.strip().replace('-', '').replace('‑', '').isdigit():
                    issues.append(f'Form appears to be only numbers: "{conjugation.form}" for {verb_infinitive}')
                
                # Check for forms that are just punctuation
                if conjugation.form.strip() in ['-', '‑', '.', ',', ';', ':']:
                    issues.append(f'Form is just punctuation: "{conjugation.form}" for {verb_infinitive}')
            
            return issues

    def check_common_greek_verb_patterns(self) -> Dict:
        """Check for common Greek verb conjugation patterns and their completeness."""
        print("\n🔍 Checking common Greek verb patterns...")
        
        with self.app.app_context():
            # Get all verbs with their conjugations
            verbs = Verb.query.all()
            pattern_analysis = defaultdict(lambda: {'count': 0, 'complete': 0, 'incomplete': 0})
            
            for verb in verbs:
                conjugations = Conjugation.query.filter_by(verb_id=verb.id).all()
                
                # Analyze by verb group
                verb_group = verb.verb_group or 'unknown'
                
                # Check if verb has present indicative active (most basic conjugation)
                present_active = [c for c in conjugations 
                                if c.tense == 'present' and c.mood == 'indicative' and c.voice == 'active']
                
                if present_active:
                    pattern_analysis[f'{verb_group}_present_active']['count'] += 1
                    if len(present_active) >= 6:  # Should have 6 forms
                        pattern_analysis[f'{verb_group}_present_active']['complete'] += 1
                    else:
                        pattern_analysis[f'{verb_group}_present_active']['incomplete'] += 1
                
                # Check for aorist indicative active
                aorist_active = [c for c in conjugations 
                               if c.tense == 'aorist' and c.mood == 'indicative' and c.voice == 'active']
                
                if aorist_active:
                    pattern_analysis[f'{verb_group}_aorist_active']['count'] += 1
                    if len(aorist_active) >= 6:
                        pattern_analysis[f'{verb_group}_aorist_active']['complete'] += 1
                    else:
                        pattern_analysis[f'{verb_group}_aorist_active']['incomplete'] += 1
            
            return dict(pattern_analysis)

    def run_completeness_check(self) -> Dict:
        """Run the complete conjugation completeness check."""
        print("🚀 Starting Conjugation Completeness Check...")
        
        # Load extracted verbs
        extracted_verbs = self.load_extracted_verbs()
        if not extracted_verbs:
            print("❌ Failed to load extracted verbs. Exiting.")
            return self.results
        
        print(f"\n📊 Checking {len(extracted_verbs)} verbs for conjugation completeness...")
        
        # Check each verb
        for verb_infinitive, verb_data in extracted_verbs.items():
            self.results['total_verbs_checked'] += 1
            
            # Check completeness
            completeness_result = self.check_verb_conjugation_completeness(verb_infinitive, verb_data)
            
            if completeness_result['status'] == 'complete':
                self.results['verbs_with_complete_conjugations'] += 1
            else:
                self.results['verbs_with_incomplete_conjugations'].append({
                    'verb': verb_infinitive,
                    'completeness_percentage': completeness_result['completeness_percentage'],
                    'issues': completeness_result['issues']
                })
            
            # Check form validity
            form_issues = self.validate_conjugation_forms(verb_infinitive, verb_data)
            if form_issues:
                self.results['verbs_with_incorrect_forms'].append({
                    'verb': verb_infinitive,
                    'issues': form_issues
                })
        
        # Check common patterns
        pattern_analysis = self.check_common_greek_verb_patterns()
        
        # Generate report
        self.generate_completeness_report(pattern_analysis)
        
        return self.results

    def generate_completeness_report(self, pattern_analysis: Dict) -> None:
        """Generate a comprehensive completeness report."""
        print("\n" + "="*70)
        print("📋 CONJUGATION COMPLETENESS REPORT")
        print("="*70)
        
        # Basic statistics
        total_verbs = self.results['total_verbs_checked']
        complete_verbs = self.results['verbs_with_complete_conjugations']
        incomplete_verbs = len(self.results['verbs_with_incomplete_conjugations'])
        
        print(f"\n📈 BASIC STATISTICS:")
        print(f"   • Total verbs checked: {total_verbs}")
        print(f"   • Verbs with complete conjugations: {complete_verbs}")
        print(f"   • Verbs with incomplete conjugations: {incomplete_verbs}")
        
        if total_verbs > 0:
            completeness_percentage = (complete_verbs / total_verbs) * 100
            print(f"   • Overall completeness: {completeness_percentage:.1f}%")
        
        # Incomplete verbs summary
        if self.results['verbs_with_incomplete_conjugations']:
            print(f"\n⚠️  INCOMPLETE VERBS ({len(self.results['verbs_with_incomplete_conjugations'])}):")
            for verb_info in self.results['verbs_with_incomplete_conjugations'][:10]:
                print(f"   • {verb_info['verb']}: {verb_info['completeness_percentage']:.1f}% complete")
                for issue in verb_info['issues'][:3]:  # Show first 3 issues
                    print(f"     - {issue}")
                if len(verb_info['issues']) > 3:
                    print(f"     ... and {len(verb_info['issues']) - 3} more issues")
            
            if len(self.results['verbs_with_incomplete_conjugations']) > 10:
                print(f"   ... and {len(self.results['verbs_with_incomplete_conjugations']) - 10} more verbs")
        
        # Form validation issues
        if self.results['verbs_with_incorrect_forms']:
            print(f"\n❌ FORM VALIDATION ISSUES ({len(self.results['verbs_with_incorrect_forms'])}):")
            for verb_info in self.results['verbs_with_incorrect_forms'][:5]:
                print(f"   • {verb_info['verb']}:")
                for issue in verb_info['issues'][:2]:
                    print(f"     - {issue}")
                if len(verb_info['issues']) > 2:
                    print(f"     ... and {len(verb_info['issues']) - 2} more issues")
        
        # Pattern analysis
        if pattern_analysis:
            print(f"\n📊 CONJUGATION PATTERN ANALYSIS:")
            for pattern, stats in pattern_analysis.items():
                if stats['count'] > 0:
                    completeness = (stats['complete'] / stats['count']) * 100
                    print(f"   • {pattern}: {stats['complete']}/{stats['count']} complete ({completeness:.1f}%)")
        
        print("\n" + "="*70)

def main():
    """Main function to run the completeness checker."""
    checker = ConjugationCompletenessChecker()
    results = checker.run_completeness_check()
    
    # Exit with error code if there are significant issues
    total_verbs = results['total_verbs_checked']
    complete_verbs = results['verbs_with_complete_conjugations']
    
    if total_verbs > 0:
        completeness_percentage = (complete_verbs / total_verbs) * 100
        
        if completeness_percentage < 50:
            print("\n❌ Conjugation completeness check failed! Less than 50% of verbs are complete.")
            return 1
        elif completeness_percentage < 80:
            print("\n⚠️  Conjugation completeness check passed with warnings. Less than 80% of verbs are complete.")
            return 0
        else:
            print("\n✅ Conjugation completeness check passed!")
            return 0
    else:
        print("\n❌ No verbs were checked!")
        return 1

if __name__ == '__main__':
    exit(main()) 