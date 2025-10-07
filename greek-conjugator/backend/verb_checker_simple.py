#!/usr/bin/env python3
"""
Simple Verb Checker for Greek Conjugator

A Flask-free version that allows you to check specific verbs and their conjugations.
"""

import sqlite3
import os
from typing import List, Dict, Optional

class SimpleVerbChecker:
    def __init__(self):
        self.db_path = 'greek_conjugator_dev.db'

    def connect_to_db(self):
        """Connect to the SQLite database."""
        if not os.path.exists(self.db_path):
            print(f"❌ Database file not found: {self.db_path}")
            return None
        
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            return conn
        except Exception as e:
            print(f"❌ Error connecting to database: {e}")
            return None

    def check_verb(self, verb_infinitive: str) -> Dict:
        """Check a specific verb and its conjugations."""
        conn = self.connect_to_db()
        if not conn:
            return {'found': False, 'error': 'Could not connect to database'}
        
        try:
            cursor = conn.cursor()
            
            # Find the verb
            cursor.execute("SELECT * FROM verbs WHERE infinitive = ?", (verb_infinitive,))
            verb = cursor.fetchone()
            
            if not verb:
                return {
                    'found': False,
                    'error': f'Verb "{verb_infinitive}" not found in database'
                }
            
            # Get all conjugations for this verb
            cursor.execute("""
                SELECT * FROM conjugations 
                WHERE verb_id = ? 
                ORDER BY tense, mood, voice, person, number
            """, (verb['id'],))
            
            conjugations = cursor.fetchall()
            
            # Group conjugations by tense, mood, voice
            grouped_conjugations = {}
            for conj in conjugations:
                key = f"{conj['tense']}_{conj['mood']}_{conj['voice']}"
                if key not in grouped_conjugations:
                    grouped_conjugations[key] = []
                grouped_conjugations[key].append(conj)
            
            return {
                'found': True,
                'verb': dict(verb),
                'total_conjugations': len(conjugations),
                'grouped_conjugations': grouped_conjugations,
                'conjugation_groups': list(grouped_conjugations.keys())
            }
            
        except Exception as e:
            return {'found': False, 'error': str(e)}
        finally:
            conn.close()

    def list_verbs_with_conjugations(self, limit: int = 20) -> List[Dict]:
        """List verbs that have conjugations."""
        conn = self.connect_to_db()
        if not conn:
            return []
        
        try:
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT v.infinitive, v.english, v.verb_group, v.frequency, COUNT(c.id) as conjugation_count
                FROM verbs v
                LEFT JOIN conjugations c ON v.id = c.verb_id
                GROUP BY v.id, v.infinitive, v.english, v.verb_group, v.frequency
                HAVING conjugation_count > 0
                ORDER BY conjugation_count DESC
                LIMIT ?
            """, (limit,))
            
            verbs = cursor.fetchall()
            return [dict(verb) for verb in verbs]
            
        except Exception as e:
            print(f"❌ Error listing verbs: {e}")
            return []
        finally:
            conn.close()

    def search_verbs(self, search_term: str, limit: int = 10) -> List[Dict]:
        """Search for verbs by infinitive or English meaning."""
        conn = self.connect_to_db()
        if not conn:
            return []
        
        try:
            cursor = conn.cursor()
            
            # Search by infinitive (case-insensitive)
            cursor.execute("""
                SELECT v.infinitive, v.english, v.verb_group, v.frequency, COUNT(c.id) as conjugation_count
                FROM verbs v
                LEFT JOIN conjugations c ON v.id = c.verb_id
                WHERE v.infinitive LIKE ?
                GROUP BY v.id, v.infinitive, v.english, v.verb_group, v.frequency
                ORDER BY conjugation_count DESC
                LIMIT ?
            """, (f'%{search_term}%', limit))
            
            verbs = cursor.fetchall()
            
            # Search by English meaning if not enough results
            if len(verbs) < limit:
                cursor.execute("""
                    SELECT v.infinitive, v.english, v.verb_group, v.frequency, COUNT(c.id) as conjugation_count
                    FROM verbs v
                    LEFT JOIN conjugations c ON v.id = c.verb_id
                    WHERE v.english LIKE ?
                    GROUP BY v.id, v.infinitive, v.english, v.verb_group, v.frequency
                    ORDER BY conjugation_count DESC
                    LIMIT ?
                """, (f'%{search_term}%', limit - len(verbs)))
                
                english_verbs = cursor.fetchall()
                verbs.extend(english_verbs)
            
            return [dict(verb) for verb in verbs]
            
        except Exception as e:
            print(f"❌ Error searching verbs: {e}")
            return []
        finally:
            conn.close()

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
                                       key=lambda c: (c['person'] or '', c['number'] or ''))
            
            for conj in sorted_conjugations:
                person_number = f"{conj['person']} {conj['number']}" if conj['person'] and conj['number'] else "N/A"
                print(f"      • {conj['form']} ({person_number})")
        
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
    checker = SimpleVerbChecker()
    
    print("🔍 Greek Conjugator - Simple Verb Checker")
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