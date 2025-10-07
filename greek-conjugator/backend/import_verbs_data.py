#!/usr/bin/env python3
"""
Import Verbs Data Script for Greek Conjugator

This script imports all verbs and conjugations from extracted_verbs.json into the database.
It includes progress tracking, error handling, and verification of the import.
"""

import sqlite3
import json
import os
import sys
from datetime import datetime
from typing import Dict, List, Tuple, Optional

class VerbDataImporter:
    def __init__(self):
        self.db_path = 'greek_conjugator_dev.db'
        self.json_path = '../extracted_verbs.json'
        self.stats = {
            'total_verbs_in_json': 0,
            'total_conjugations_in_json': 0,
            'verbs_imported': 0,
            'conjugations_imported': 0,
            'verbs_skipped': 0,
            'conjugations_skipped': 0,
            'errors': [],
            'start_time': None,
            'end_time': None
        }

    def load_json_data(self) -> Dict:
        """Load the extracted verbs from JSON file."""
        print("📂 Loading extracted_verbs.json...")
        
        if not os.path.exists(self.json_path):
            print(f"❌ Error: {self.json_path} not found!")
            print(f"   Make sure the file exists in the project root directory.")
            return {}
        
        try:
            with open(self.json_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            self.stats['total_verbs_in_json'] = len(data)
            self.stats['total_conjugations_in_json'] = sum(
                len(verb_data.get('conjugations', [])) 
                for verb_data in data.values()
            )
            
            print(f"✅ Loaded {self.stats['total_verbs_in_json']} verbs with {self.stats['total_conjugations_in_json']} conjugations")
            return data
            
        except json.JSONDecodeError as e:
            print(f"❌ Error parsing JSON: {e}")
            return {}
        except Exception as e:
            print(f"❌ Error loading file: {e}")
            return {}

    def connect_to_db(self):
        """Connect to the SQLite database."""
        if not os.path.exists(self.db_path):
            print(f"❌ Database file not found: {self.db_path}")
            print(f"   Run setup_and_test.py first to create the database.")
            return None
        
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            return conn
        except Exception as e:
            print(f"❌ Error connecting to database: {e}")
            return None

    def clean_verb_data(self, verb_data: Dict) -> Dict:
        """Clean and prepare verb data for import."""
        cleaned = {
            'infinitive': verb_data.get('word', '').strip(),
            'english': verb_data.get('english', '').strip(),
            'frequency': verb_data.get('frequency'),
            'difficulty': self.calculate_difficulty(verb_data),
            'verb_group': self.determine_verb_group(verb_data),
            'transitivity': self.determine_transitivity(verb_data),
            'tags': self.extract_tags(verb_data),
            'audio_url': verb_data.get('audio_url')
        }
        
        # Ensure required fields are not empty
        if not cleaned['infinitive']:
            cleaned['infinitive'] = verb_data.get('word', 'unknown')
        if not cleaned['english']:
            cleaned['english'] = 'to ' + cleaned['infinitive']
        
        return cleaned

    def calculate_difficulty(self, verb_data: Dict) -> int:
        """Calculate difficulty level based on verb characteristics."""
        # Simple heuristic based on frequency and complexity
        frequency = verb_data.get('frequency')
        conjugations = verb_data.get('conjugations', [])
        
        if frequency is not None and frequency <= 100:
            return 1  # Common verb
        elif len(conjugations) > 20:
            return 3  # Complex verb
        else:
            return 2  # Medium difficulty

    def determine_verb_group(self, verb_data: Dict) -> str:
        """Determine verb group based on conjugations."""
        conjugations = verb_data.get('conjugations', [])
        
        # Check for irregular patterns
        irregular_indicators = ['είμαι', 'έχω', 'έρχομαι', 'πηγαίνω']
        infinitive = verb_data.get('word', '').lower()
        
        if any(indicator in infinitive for indicator in irregular_indicators):
            return 'irregular'
        
        # Simple heuristic - could be improved with more sophisticated analysis
        if len(conjugations) > 15:
            return 'A'  # Most common group
        else:
            return 'B'  # Less common group

    def determine_transitivity(self, verb_data: Dict) -> str:
        """Determine if verb is transitive or intransitive."""
        english = verb_data.get('english', '').lower()
        
        # Simple heuristic based on English meaning
        intransitive_indicators = ['to be', 'to go', 'to come', 'to stay', 'to live', 'to sleep']
        if any(indicator in english for indicator in intransitive_indicators):
            return 'intransitive'
        else:
            return 'transitive'

    def extract_tags(self, verb_data: Dict) -> str:
        """Extract tags from verb data."""
        tags = []
        
        # Extract from English meaning
        english = verb_data.get('english', '').lower()
        if 'to be' in english:
            tags.append('existence')
        elif 'to go' in english or 'to come' in english:
            tags.append('movement')
        elif 'to see' in english or 'to look' in english:
            tags.append('perception')
        elif 'to say' in english or 'to speak' in english:
            tags.append('communication')
        
        # Add frequency-based tags
        frequency = verb_data.get('frequency')
        if frequency is not None:
            if frequency <= 100:
                tags.append('common')
            elif frequency <= 1000:
                tags.append('medium_frequency')
            else:
                tags.append('rare')
        
        return ', '.join(tags) if tags else 'general'

    def clean_conjugation_data(self, conj_data: Dict, verb_id: int) -> Dict:
        """Clean and prepare conjugation data for import."""
        cleaned = {
            'verb_id': verb_id,
            'tense': conj_data.get('tense', 'unknown').lower(),
            'mood': conj_data.get('mood', 'unknown').lower(),
            'voice': conj_data.get('voice', 'unknown').lower(),
            'person': conj_data.get('person'),
            'number': conj_data.get('number'),
            'form': conj_data.get('form', '').strip(),
            'audio_url': conj_data.get('audio_url'),
            'stress_pattern': conj_data.get('stress_pattern'),
            'morphology': conj_data.get('morphology')
        }
        
        # Clean up person/number data
        if cleaned['person']:
            cleaned['person'] = cleaned['person'].lower()
        if cleaned['number']:
            cleaned['number'] = cleaned['number'].lower()
        
        # Ensure form is not empty
        if not cleaned['form']:
            cleaned['form'] = 'unknown'
        
        return cleaned

    def import_verb(self, cursor, verb_infinitive: str, verb_data: Dict) -> Tuple[bool, int]:
        """Import a single verb and its conjugations."""
        try:
            # Check if verb already exists
            cursor.execute("SELECT id FROM verbs WHERE infinitive = ?", (verb_infinitive,))
            existing_verb = cursor.fetchone()
            
            if existing_verb:
                self.stats['verbs_skipped'] += 1
                return True, existing_verb['id']  # Return existing verb ID
            
            # Clean and prepare verb data
            cleaned_verb = self.clean_verb_data(verb_data)
            
            # Insert verb
            cursor.execute("""
                INSERT INTO verbs (infinitive, english, frequency, difficulty, verb_group, transitivity, tags, audio_url)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                cleaned_verb['infinitive'],
                cleaned_verb['english'],
                cleaned_verb['frequency'],
                cleaned_verb['difficulty'],
                cleaned_verb['verb_group'],
                cleaned_verb['transitivity'],
                cleaned_verb['tags'],
                cleaned_verb['audio_url']
            ))
            
            verb_id = cursor.lastrowid
            self.stats['verbs_imported'] += 1
            
            # Import conjugations
            conjugations = verb_data.get('conjugations', [])
            for conj_data in conjugations:
                try:
                    cleaned_conj = self.clean_conjugation_data(conj_data, verb_id)
                    
                    # Check for duplicate conjugation
                    cursor.execute("""
                        SELECT id FROM conjugations 
                        WHERE verb_id = ? AND form = ? AND tense = ? AND mood = ? AND voice = ?
                    """, (
                        cleaned_conj['verb_id'],
                        cleaned_conj['form'],
                        cleaned_conj['tense'],
                        cleaned_conj['mood'],
                        cleaned_conj['voice']
                    ))
                    
                    if not cursor.fetchone():
                        cursor.execute("""
                            INSERT INTO conjugations (verb_id, tense, mood, voice, person, number, form, audio_url, stress_pattern, morphology)
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                        """, (
                            cleaned_conj['verb_id'],
                            cleaned_conj['tense'],
                            cleaned_conj['mood'],
                            cleaned_conj['voice'],
                            cleaned_conj['person'],
                            cleaned_conj['number'],
                            cleaned_conj['form'],
                            cleaned_conj['audio_url'],
                            cleaned_conj['stress_pattern'],
                            cleaned_conj['morphology']
                        ))
                        self.stats['conjugations_imported'] += 1
                    else:
                        self.stats['conjugations_skipped'] += 1
                        
                except Exception as e:
                    self.stats['errors'].append(f"Conjugation error for {verb_infinitive}: {e}")
            
            return True, verb_id
            
        except Exception as e:
            self.stats['errors'].append(f"Verb error for {verb_infinitive}: {e}")
            return False, 0

    def import_all_data(self, data: Dict) -> bool:
        """Import all verbs and conjugations from the JSON data."""
        print("\n🚀 Starting data import...")
        self.stats['start_time'] = datetime.now()
        
        conn = self.connect_to_db()
        if not conn:
            return False
        
        try:
            cursor = conn.cursor()
            total_verbs = len(data)
            
            print(f"📊 Importing {total_verbs} verbs...")
            
            # Import verbs with progress tracking
            for i, (verb_infinitive, verb_data) in enumerate(data.items(), 1):
                if i % 100 == 0 or i == total_verbs:
                    print(f"   Progress: {i}/{total_verbs} verbs ({i/total_verbs*100:.1f}%)")
                
                success, verb_id = self.import_verb(cursor, verb_infinitive, verb_data)
                
                if not success:
                    print(f"   ⚠️  Failed to import verb: {verb_infinitive}")
            
            # Commit all changes
            conn.commit()
            self.stats['end_time'] = datetime.now()
            
            print(f"\n✅ Import completed!")
            return True
            
        except Exception as e:
            print(f"❌ Import error: {e}")
            conn.rollback()
            return False
        finally:
            conn.close()

    def verify_import(self) -> bool:
        """Verify that the import was successful."""
        print("\n🔍 Verifying import...")
        
        conn = self.connect_to_db()
        if not conn:
            return False
        
        try:
            cursor = conn.cursor()
            
            # Get database statistics
            cursor.execute("SELECT COUNT(*) FROM verbs")
            db_verbs = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM conjugations")
            db_conjugations = cursor.fetchone()[0]
            
            cursor.execute("""
                SELECT COUNT(DISTINCT v.id) 
                FROM verbs v 
                JOIN conjugations c ON v.id = c.verb_id
            """)
            verbs_with_conjugations = cursor.fetchone()[0]
            
            # Calculate coverage
            verb_coverage = (db_verbs / self.stats['total_verbs_in_json'] * 100) if self.stats['total_verbs_in_json'] > 0 else 0
            conjugation_coverage = (db_conjugations / self.stats['total_conjugations_in_json'] * 100) if self.stats['total_conjugations_in_json'] > 0 else 0
            
            print(f"📊 VERIFICATION RESULTS:")
            print(f"   • Verbs in JSON: {self.stats['total_verbs_in_json']}")
            print(f"   • Verbs in database: {db_verbs}")
            print(f"   • Verb coverage: {verb_coverage:.1f}%")
            print(f"   • Conjugations in JSON: {self.stats['total_conjugations_in_json']}")
            print(f"   • Conjugations in database: {db_conjugations}")
            print(f"   • Conjugation coverage: {conjugation_coverage:.1f}%")
            print(f"   • Verbs with conjugations: {verbs_with_conjugations}")
            
            # Check for data quality issues
            cursor.execute("SELECT COUNT(*) FROM conjugations WHERE form IS NULL OR form = ''")
            empty_forms = cursor.fetchone()[0]
            
            cursor.execute("""
                SELECT COUNT(*) 
                FROM conjugations c 
                LEFT JOIN verbs v ON c.verb_id = v.id 
                WHERE v.id IS NULL
            """)
            orphaned_conjugations = cursor.fetchone()[0]
            
            print(f"\n🔍 DATA QUALITY:")
            print(f"   • Empty conjugation forms: {empty_forms}")
            print(f"   • Orphaned conjugations: {orphaned_conjugations}")
            print(f"   • Import errors: {len(self.stats['errors'])}")
            
            if self.stats['errors']:
                print(f"\n⚠️  IMPORT ERRORS:")
                for error in self.stats['errors'][:10]:  # Show first 10 errors
                    print(f"   • {error}")
                if len(self.stats['errors']) > 10:
                    print(f"   ... and {len(self.stats['errors']) - 10} more errors")
            
            conn.close()
            
            # Determine success
            success = (verb_coverage > 90 and conjugation_coverage > 80 and len(self.stats['errors']) < 50)
            return success
            
        except Exception as e:
            print(f"❌ Verification error: {e}")
            return False

    def generate_import_report(self):
        """Generate a comprehensive import report."""
        print("\n" + "="*80)
        print("📋 IMPORT REPORT")
        print("="*80)
        print(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        if self.stats['start_time'] and self.stats['end_time']:
            duration = self.stats['end_time'] - self.stats['start_time']
            print(f"Duration: {duration}")
        
        print(f"\n📈 IMPORT STATISTICS:")
        print(f"   • Total verbs in JSON: {self.stats['total_verbs_in_json']}")
        print(f"   • Total conjugations in JSON: {self.stats['total_conjugations_in_json']}")
        print(f"   • Verbs imported: {self.stats['verbs_imported']}")
        print(f"   • Conjugations imported: {self.stats['conjugations_imported']}")
        print(f"   • Verbs skipped (already existed): {self.stats['verbs_skipped']}")
        print(f"   • Conjugations skipped (duplicates): {self.stats['conjugations_skipped']}")
        print(f"   • Import errors: {len(self.stats['errors'])}")
        
        if self.stats['total_verbs_in_json'] > 0:
            verb_import_rate = (self.stats['verbs_imported'] / self.stats['total_verbs_in_json']) * 100
            print(f"   • Verb import rate: {verb_import_rate:.1f}%")
        
        if self.stats['total_conjugations_in_json'] > 0:
            conj_import_rate = (self.stats['conjugations_imported'] / self.stats['total_conjugations_in_json']) * 100
            print(f"   • Conjugation import rate: {conj_import_rate:.1f}%")
        
        print("\n" + "="*80)

def main():
    """Main function to run the import process."""
    print("🚀 Greek Conjugator - Verb Data Import")
    print("=" * 60)
    
    importer = VerbDataImporter()
    
    # Step 1: Load JSON data
    data = importer.load_json_data()
    if not data:
        print("❌ Failed to load JSON data. Exiting.")
        return 1
    
    # Step 2: Import data
    if not importer.import_all_data(data):
        print("❌ Import failed. Exiting.")
        return 1
    
    # Step 3: Verify import
    if not importer.verify_import():
        print("❌ Import verification failed.")
        return 1
    
    # Step 4: Generate report
    importer.generate_import_report()
    
    print("\n🎉 Import process completed!")
    print("\n📝 Next Steps:")
    print("1. Run the test scripts to verify data integrity:")
    print("   • python3 quick_test.py")
    print("   • python3 simple_db_check.py")
    print("   • python3 verb_checker_simple.py")
    print("2. Test specific verbs to ensure they imported correctly")
    print("3. Your Greek Conjugator is ready with full verb data!")
    
    return 0

if __name__ == '__main__':
    exit(main()) 