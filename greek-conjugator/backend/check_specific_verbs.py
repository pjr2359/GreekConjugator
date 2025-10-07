#!/usr/bin/env python3
"""
Specific Verb Checker for Greek Conjugator

This utility allows you to check specific verbs and their conjugations in detail.
Useful for debugging and verifying that specific verbs were imported correctly.
"""

import sys
import os
import json
from typing import List, Dict, Optional

# Add the project directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from app.models import db, Verb, Conjugation

class VerbChecker:
    def __init__(self):
        self.app = create_app()

    def check_verb(self, verb_infinitive: str) -> Dict:
        """Check a specific verb and its conjugations."""
        with self.app.app_context():
            # Find the verb
            verb = Verb.query.filter_by(infinitive=verb_infinitive).first()
            if not verb:
                return {
                    'found': False,
                    'error': f'Verb "{verb_infinitive}" not found in database'
                }
            
            # Get all conjugations for this verb
            conjugations = Conjugation.query.filter_by(verb_id=verb.id).all()
            
            # Group conjugations by tense, mood, voice
            grouped_conjugations = {}
            for conj in conjugations:
                key = f"{conj.tense}_{conj.mood}_{conj.voice}"
                if key not in grouped_conjugations:
                    grouped_conjugations[key] = []
                grouped_conjugations[key].append(conj)
            
            return {
                'found': True,
                'verb': verb.to_dict(),
                'total_conjugations': len(conjugations),
                'grouped_conjugations': grouped_conjugations,
                'conjugation_groups': list(grouped_conjugations.keys())
            }

    def list_verbs_with_conjugations(self, limit: int = 20) -> List[Dict]:
        """List verbs that have conjugations."""
        with self.app.app_context():
            verbs_with_conjugations = []
            
            for verb in Verb.query.all():
                conjugation_count = Conjugation.query.filter_by(verb_id=verb.id).count()
                if conjugation_count > 0:
                    verbs_with_conjugations.append({
                        'infinitive': verb.infinitive,
                        'english': verb.english,
                        'conjugation_count': conjugation_count,
                        'verb_group': verb.verb_group,
                        'frequency': verb.frequency
                    })
            
            # Sort by conjugation count (descending)
            verbs_with_conjugations.sort(key=lambda x: x['conjugation_count'], reverse=True)
            
            return verbs_with_conjugations[:limit]

    def search_verbs(self, search_term: str, limit: int = 10) -> List[Dict]:
        """Search for verbs by infinitive or English meaning."""
        with self.app.app_context():
            # Search by infinitive (case-insensitive)
            verbs = Verb.query.filter(
                Verb.infinitive.ilike(f'%{search_term}%')
            ).limit(limit).all()
            
            # Search by English meaning if not enough results
            if len(verbs) < limit:
                english_verbs = Verb.query.filter(
                    Verb.english.ilike(f'%{search_term}%')
                ).limit(limit - len(verbs)).all()
                verbs.extend(english_verbs)
            
            results = []
            for verb in verbs:
                conjugation_count = Conjugation.query.filter_by(verb_id=verb.id).count()
                results.append({
                    'infinitive': verb.infinitive,
                    'english': verb.english,
                    'conjugation_count': conjugation_count,
                    'verb_group': verb.verb_group,
                    'frequency': verb.frequency
                })
            
            return results

    def print_verb_details(self, verb_infinitive: str) -> None:
        """Print detailed information about a specific verb."""
        result = self.check_verb(verb_infinitive)
        
        if not result['found']:
            print(f"❌ {result['error']}")
            return
        
        verb = result['verb']
        print(f"\n{'='*60}")
        print(f"📖 VERB DETAILS: {verb_infinitive}")
        print(f"{'='*60}")
        
        print(f"\n📋 BASIC INFORMATION:")
        print(f"   • Infinitive: {verb['infinitive']}")
        print(f"   • English: {verb['english']}")
        print(f"   • Verb Group: {verb['verb_group']}")
        print(f"   • Frequency: {verb['frequency']}")
        print(f"   • Difficulty: {verb['difficulty']}")
        print(f"   • Transitivity: {verb['transitivity']}")
        print(f"   • Tags: {verb['tags']}")
        
        print(f"\n📊 CONJUGATION STATISTICS:")
        print(f"   • Total conjugations: {result['total_conjugations']}")
        print(f"   • Conjugation groups: {len(result['conjugation_groups'])}")
        
        print(f"\n🔍 CONJUGATION GROUPS:")
        for group_name in sorted(result['conjugation_groups']):
            conjugations = result['grouped_conjugations'][group_name]
            print(f"\n   📝 {group_name.upper()} ({len(conjugations)} forms):")
            
            # Sort conjugations by person and number for better display
            sorted_conjugations = sorted(conjugations, 
                                       key=lambda c: (c.person or '', c.number or ''))
            
            for conj in sorted_conjugations:
                person_number = f"{conj.person} {conj.number}" if conj.person and conj.number else "N/A"
                print(f"      • {conj.form} ({person_number})")
        
        print(f"\n{'='*60}")

    def print_verb_list(self, verbs: List[Dict], title: str) -> None:
        """Print a list of verbs in a formatted way."""
        print(f"\n{'='*60}")
        print(f"📋 {title}")
        print(f"{'='*60}")
        
        if not verbs:
            print("   No verbs found.")
            return
        
        print(f"{'Infinitive':<20} {'English':<25} {'Conjugations':<12} {'Group':<10} {'Freq':<5}")
        print("-" * 80)
        
        for verb in verbs:
            print(f"{verb['infinitive']:<20} {verb['english'][:24]:<25} {verb['conjugation_count']:<12} {verb['verb_group']:<10} {verb['frequency'] or 'N/A':<5}")
        
        print(f"\nTotal: {len(verbs)} verbs")

def main():
    """Main function with interactive menu."""
    checker = VerbChecker()
    
    print("🔍 Greek Conjugator - Verb Checker")
    print("=" * 50)
    
    while True:
        print("\nOptions:")
        print("1. Check specific verb")
        print("2. List verbs with conjugations")
        print("3. Search verbs")
        print("4. Exit")
        
        choice = input("\nEnter your choice (1-4): ").strip()
        
        if choice == '1':
            verb = input("Enter verb infinitive: ").strip()
            if verb:
                checker.print_verb_details(verb)
        
        elif choice == '2':
            try:
                limit = int(input("Enter number of verbs to show (default 20): ") or "20")
                verbs = checker.list_verbs_with_conjugations(limit)
                checker.print_verb_list(verbs, f"VERBS WITH CONJUGATIONS (Top {len(verbs)})")
            except ValueError:
                print("Invalid number. Using default of 20.")
                verbs = checker.list_verbs_with_conjugations(20)
                checker.print_verb_list(verbs, "VERBS WITH CONJUGATIONS (Top 20)")
        
        elif choice == '3':
            search_term = input("Enter search term: ").strip()
            if search_term:
                try:
                    limit = int(input("Enter number of results (default 10): ") or "10")
                    verbs = checker.search_verbs(search_term, limit)
                    checker.print_verb_list(verbs, f"SEARCH RESULTS FOR '{search_term}'")
                except ValueError:
                    print("Invalid number. Using default of 10.")
                    verbs = checker.search_verbs(search_term, 10)
                    checker.print_verb_list(verbs, f"SEARCH RESULTS FOR '{search_term}'")
        
        elif choice == '4':
            print("👋 Goodbye!")
            break
        
        else:
            print("Invalid choice. Please enter 1-4.")

if __name__ == '__main__':
    main() 