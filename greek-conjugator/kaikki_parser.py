#!/usr/bin/env python3
"""
Kaikki.org Greek Dictionary Parser
Extracts verb conjugations for a given frequency list of words.
"""

import json
import re
from typing import Dict, List, Set, Optional, Tuple
from collections import defaultdict

class KaikkiParser:
    def __init__(self, dictionary_path: str):
        self.dictionary_path = dictionary_path
        self.verb_entries = {}
        self.conjugation_patterns = {
            'present': {
                'indicative': ['1st', '2nd', '3rd'],
                'subjunctive': ['1st', '2nd', '3rd'],
                'imperative': ['2nd', '3rd']
            },
            'imperfect': {
                'indicative': ['1st', '2nd', '3rd']
            },
            'future': {
                'indicative': ['1st', '2nd', '3rd']
            },
            'aorist': {
                'indicative': ['1st', '2nd', '3rd'],
                'subjunctive': ['1st', '2nd', '3rd'],
                'imperative': ['2nd', '3rd']
            },
            'perfect': {
                'indicative': ['1st', '2nd', '3rd']
            },
            'pluperfect': {
                'indicative': ['1st', '2nd', '3rd']
            }
        }

    def load_frequency_list(self, frequency_file: str) -> Set[str]:
        """Load a frequency list of Greek words."""
        words = set()
        try:
            with open(frequency_file, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#'):
                        # Handle different formats: word, word\trank, etc.
                        parts = line.split('\t')
                        word = parts[0].strip()
                        if word:
                            words.add(word.lower())
        except FileNotFoundError:
            print(f"Warning: Frequency file {frequency_file} not found.")
            print("You can create one with common Greek words, one per line.")
        return words

    def parse_kaikki_dictionary(self, target_words: Set[str]) -> Dict:
        """Parse the Kaikki.org dictionary and extract verb entries for target words."""
        print(f"Parsing Kaikki.org dictionary for {len(target_words)} target words...")
        
        extracted_verbs = {}
        processed_count = 0
        
        with open(self.dictionary_path, 'r', encoding='utf-8') as f:
            for line in f:
                try:
                    entry = json.loads(line.strip())
                    
                    # Check if this is a verb and in our target words
                    if (entry.get('pos') == 'verb' and 
                        entry.get('word', '').lower() in target_words):
                        
                        word = entry.get('word', '')
                        print(f"Found verb: {word}")
                        
                        # Extract basic info
                        verb_data = {
                            'word': word,
                            'english': self._extract_english_glosses(entry),
                            'conjugations': self._extract_conjugations(entry),
                            'audio_url': self._extract_audio_url(entry),
                            'frequency': self._extract_frequency(entry)
                        }
                        
                        extracted_verbs[word] = verb_data
                        processed_count += 1
                        
                        if processed_count % 10 == 0:
                            print(f"Processed {processed_count} verbs...")
                            
                except json.JSONDecodeError:
                    continue
                except Exception as e:
                    print(f"Error processing entry: {e}")
                    continue
        
        print(f"Extracted {len(extracted_verbs)} verbs from Kaikki.org")
        return extracted_verbs

    def _extract_english_glosses(self, entry: Dict) -> str:
        """Extract English translations from the entry."""
        glosses = []
        for sense in entry.get('senses', []):
            for gloss in sense.get('glosses', []):
                if gloss and isinstance(gloss, str):
                    glosses.append(gloss)
        
        # Return the first few glosses, separated by commas
        return ', '.join(glosses[:3]) if glosses else ''

    def _extract_conjugations(self, entry: Dict) -> List[Dict]:
        """Extract conjugation forms from the entry."""
        conjugations = []
        
        # Extract from forms array
        for form in entry.get('forms', []):
            form_text = form.get('form', '')
            tags = form.get('tags', [])
            
            if form_text and tags:
                conjugation = self._parse_conjugation_tags(form_text, tags)
                if conjugation:
                    conjugations.append(conjugation)
        
        # Extract from inflection templates
        for template in entry.get('inflection_templates', []):
            template_name = template.get('name', '')
            args = template.get('args', {})
            
            if 'el-verb' in template_name.lower():
                conjugations.extend(self._parse_inflection_template(args))
        
        return conjugations

    def _parse_conjugation_tags(self, form: str, tags: List[str]) -> Optional[Dict]:
        """Parse conjugation information from form tags."""
        # Map Kaikki tags to our schema
        tense_mapping = {
            'present': 'present',
            'imperfect': 'imperfect', 
            'future': 'future',
            'aorist': 'aorist',
            'perfect': 'perfect',
            'pluperfect': 'pluperfect'
        }
        
        mood_mapping = {
            'indicative': 'indicative',
            'subjunctive': 'subjunctive',
            'imperative': 'imperative',
            'optative': 'optative'
        }
        
        voice_mapping = {
            'active': 'active',
            'passive': 'passive',
            'middle': 'middle'
        }
        
        person_mapping = {
            '1st': '1st',
            '2nd': '2nd', 
            '3rd': '3rd'
        }
        
        number_mapping = {
            'singular': 'singular',
            'plural': 'plural'
        }
        
        # Extract information from tags
        tense = None
        mood = None
        voice = None
        person = None
        number = None
        
        for tag in tags:
            if tag in tense_mapping:
                tense = tense_mapping[tag]
            elif tag in mood_mapping:
                mood = mood_mapping[tag]
            elif tag in voice_mapping:
                voice = voice_mapping[tag]
            elif tag in person_mapping:
                person = person_mapping[tag]
            elif tag in number_mapping:
                number = number_mapping[tag]
        
        # Only return if we have meaningful conjugation info
        if tense or mood or voice:
            return {
                'form': form,
                'tense': tense or 'present',
                'mood': mood or 'indicative',
                'voice': voice or 'active',
                'person': person,
                'number': number
            }
        
        return None

    def _parse_inflection_template(self, args: Dict) -> List[Dict]:
        """Parse inflection template arguments for conjugations."""
        conjugations = []
        
        # This is a simplified parser - you might need to expand based on actual templates
        for key, value in args.items():
            if isinstance(value, str) and value:
                # Try to infer conjugation info from the key name
                if 'present' in key.lower():
                    tense = 'present'
                elif 'imperfect' in key.lower():
                    tense = 'imperfect'
                elif 'future' in key.lower():
                    tense = 'future'
                elif 'aorist' in key.lower():
                    tense = 'aorist'
                else:
                    continue
                
                conjugations.append({
                    'form': value,
                    'tense': tense,
                    'mood': 'indicative',
                    'voice': 'active',
                    'person': None,
                    'number': None
                })
        
        return conjugations

    def _extract_audio_url(self, entry: Dict) -> Optional[str]:
        """Extract audio URL if available."""
        sounds = entry.get('sounds', [])
        for sound in sounds:
            if 'ogg_url' in sound:
                return sound['ogg_url']
            elif 'mp3_url' in sound:
                return sound['mp3_url']
        return None

    def _extract_frequency(self, entry: Dict) -> Optional[int]:
        """Extract frequency information if available."""
        # Kaikki.org might not have frequency data, but we can infer from categories
        categories = entry.get('categories', [])
        for category in categories:
            if 'frequency' in category.get('name', '').lower():
                # Try to extract number from category name
                match = re.search(r'(\d+)', category['name'])
                if match:
                    return int(match.group(1))
        return None

    def generate_database_script(self, extracted_verbs: Dict, output_file: str):
        """Generate SQL script to insert verbs and conjugations into the database."""
        print(f"Generating database script: {output_file}")
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write("-- Generated from Kaikki.org Greek Dictionary\n")
            f.write("-- Insert verbs and conjugations\n\n")
            
            for word, verb_data in extracted_verbs.items():
                # Insert verb
                english = verb_data['english'].replace("'", "''")  # Escape single quotes
                audio_url = verb_data['audio_url'] or 'NULL'
                frequency = verb_data['frequency'] or 'NULL'
                
                f.write(f"-- Verb: {word}\n")
                f.write(f"INSERT INTO verbs (infinitive, english, frequency, audio_url) VALUES ('{word}', '{english}', {frequency}, {audio_url});\n")
                f.write("SET @verb_id = LAST_INSERT_ID();\n\n")
                
                # Insert conjugations
                for conj in verb_data['conjugations']:
                    form = conj['form'].replace("'", "''")
                    tense = conj['tense'] or 'NULL'
                    mood = conj['mood'] or 'NULL'
                    voice = conj['voice'] or 'NULL'
                    person = f"'{conj['person']}'" if conj['person'] else 'NULL'
                    number = f"'{conj['number']}'" if conj['number'] else 'NULL'
                    
                    f.write(f"INSERT INTO conjugations (verb_id, tense, mood, voice, person, number, form) VALUES (@verb_id, '{tense}', '{mood}', '{voice}', {person}, {number}, '{form}');\n")
                
                f.write("\n")
        
        print(f"Database script generated: {output_file}")

    def generate_json_output(self, extracted_verbs: Dict, output_file: str):
        """Generate JSON output for manual review or import."""
        print(f"Generating JSON output: {output_file}")
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(extracted_verbs, f, ensure_ascii=False, indent=2)
        
        print(f"JSON output generated: {output_file}")

def main():
    # Configuration
    dictionary_path = "kaikki.org-dictionary-Greek.jsonl"
    frequency_file = "greek_5000_words.txt"  # Use the 5000 words list
    output_sql = "import_verbs.sql"
    output_json = "extracted_verbs.json"
    
    # Initialize parser
    parser = KaikkiParser(dictionary_path)
    
    # Load frequency list
    print("Loading frequency list...")
    target_words = parser.load_frequency_list(frequency_file)
    
    if not target_words:
        print("No target words found. Please create a frequency list file.")
        print("Example format (one word per line):")
        print("γράφω")
        print("λέω")
        print("έχω")
        return
    
    print(f"Loaded {len(target_words)} target words")
    
    # Parse dictionary
    extracted_verbs = parser.parse_kaikki_dictionary(target_words)
    
    if extracted_verbs:
        # Generate outputs
        parser.generate_database_script(extracted_verbs, output_sql)
        parser.generate_json_output(extracted_verbs, output_json)
        
        # Summary
        total_conjugations = sum(len(v['conjugations']) for v in extracted_verbs.values())
        print(f"\nSummary:")
        print(f"- Verbs extracted: {len(extracted_verbs)}")
        print(f"- Total conjugations: {total_conjugations}")
        print(f"- SQL script: {output_sql}")
        print(f"- JSON review: {output_json}")
    else:
        print("No verbs found in the dictionary for the given frequency list.")

if __name__ == "__main__":
    main() 