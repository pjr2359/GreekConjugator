#!/usr/bin/env python3
"""
Greek Vocabulary Builder
========================

Downloads and processes Greek vocabulary from Kaikki.org (Wiktionary extraction)
to build a comprehensive vocabulary database for the Greek Conjugator app.

Usage:
    1. Download the dictionary: python build_vocabulary.py --download
    2. Extract vocabulary: python build_vocabulary.py --extract
    3. Import to database: python build_vocabulary.py --import
    
Or run all steps: python build_vocabulary.py --all
"""

import json
import os
import sys
import sqlite3
import argparse
import re
from datetime import datetime
from typing import Dict, List, Optional, Set
from collections import defaultdict
import urllib.request
import gzip
import shutil

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Configuration
KAIKKI_URL = "https://kaikki.org/dictionary/Greek/kaikki.org-dictionary-Greek.jsonl.gz"
DICTIONARY_FILE = "kaikki.org-dictionary-Greek.jsonl"
DICTIONARY_GZ = "kaikki.org-dictionary-Greek.jsonl.gz"
OUTPUT_DIR = "vocabulary_data"
DB_PATH = "greek-conjugator/backend/greek_conjugator_dev.db"

# Word type mapping from Kaikki to our schema
POS_MAPPING = {
    'noun': 'noun',
    'verb': 'verb',
    'adj': 'adjective',
    'adjective': 'adjective',
    'adv': 'adverb',
    'adverb': 'adverb',
    'prep': 'preposition',
    'preposition': 'preposition',
    'pron': 'pronoun',
    'pronoun': 'pronoun',
    'conj': 'conjunction',
    'conjunction': 'conjunction',
    'num': 'numeral',
    'numeral': 'numeral',
    'det': 'determiner',
    'determiner': 'determiner',
    'article': 'article',
    'intj': 'interjection',
    'interjection': 'interjection',
    'particle': 'particle',
    'phrase': 'phrase',
}

# Thematic category detection patterns
THEMATIC_PATTERNS = {
    'family': ['μητέρα', 'πατέρας', 'αδελφός', 'αδελφή', 'γιος', 'κόρη', 'γιαγιά', 'παππούς', 
               'θείος', 'θεία', 'ξάδελφος', 'οικογένεια', 'γονείς', 'παιδί'],
    'food': ['φαγητό', 'ψωμί', 'νερό', 'κρέας', 'ψάρι', 'λαχανικά', 'φρούτα', 'τυρί', 
             'γάλα', 'αυγό', 'ρύζι', 'μακαρόνια', 'σαλάτα', 'σούπα'],
    'travel': ['αεροπλάνο', 'τρένο', 'αυτοκίνητο', 'λεωφορείο', 'ταξί', 'βαλίτσα', 
               'διαβατήριο', 'ξενοδοχείο', 'αεροδρόμιο', 'σταθμός'],
    'restaurant': ['εστιατόριο', 'μενού', 'πιάτο', 'ποτήρι', 'μαχαίρι', 'πιρούνι', 
                   'κουτάλι', 'λογαριασμός', 'σερβιτόρος', 'παραγγελία'],
    'places': ['σπίτι', 'πόλη', 'χωριό', 'δρόμος', 'πλατεία', 'εκκλησία', 'σχολείο', 
               'νοσοκομείο', 'τράπεζα', 'ταχυδρομείο', 'σούπερ μάρκετ'],
    'time': ['ώρα', 'λεπτό', 'μέρα', 'εβδομάδα', 'μήνας', 'χρόνος', 'σήμερα', 
             'αύριο', 'χθες', 'πρωί', 'απόγευμα', 'βράδυ'],
    'body': ['κεφάλι', 'μάτι', 'αυτί', 'μύτη', 'στόμα', 'χέρι', 'πόδι', 'καρδιά', 
             'δάχτυλο', 'μαλλί'],
    'colors': ['κόκκινο', 'μπλε', 'πράσινο', 'κίτρινο', 'άσπρο', 'μαύρο', 'γκρι', 
               'ροζ', 'πορτοκαλί', 'μωβ'],
    'numbers': ['ένα', 'δύο', 'τρία', 'τέσσερα', 'πέντε', 'έξι', 'επτά', 'οκτώ', 
                'εννέα', 'δέκα', 'εκατό', 'χίλια'],
    'work': ['δουλειά', 'γραφείο', 'εργασία', 'συνέντευξη', 'μισθός', 'αφεντικό', 
             'συνάδελφος', 'εταιρεία', 'υπάλληλος'],
    'weather': ['καιρός', 'ήλιος', 'βροχή', 'χιόνι', 'άνεμος', 'σύννεφο', 'ζέστη', 
                'κρύο', 'θερμοκρασία'],
    'emotions': ['χαρά', 'λύπη', 'θυμός', 'φόβος', 'αγάπη', 'ευτυχία', 'στεναχώρια', 
                 'ανησυχία', 'ελπίδα'],
}


class VocabularyBuilder:
    def __init__(self, output_dir: str = OUTPUT_DIR):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
        self.words = []
        self.word_count = defaultdict(int)
        self.frequency_list = set()
        self.frequency_rank = {}
    
    def load_frequency_list(self, filepath: str = "greek-conjugator/greek_5000_words.txt"):
        """Load a frequency list to prioritize common words."""
        print(f"📊 Loading frequency list from {filepath}...")
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                for rank, line in enumerate(f, 1):
                    word = line.strip().lower()
                    if word:
                        self.frequency_list.add(word)
                        self.frequency_rank[word] = rank
            print(f"   ✅ Loaded {len(self.frequency_list)} words from frequency list")
            return True
        except FileNotFoundError:
            print(f"   ⚠️ Frequency list not found: {filepath}")
            return False
        
    def download_dictionary(self) -> bool:
        """Download the Kaikki.org Greek dictionary."""
        print("📥 Downloading Kaikki.org Greek dictionary...")
        print(f"   URL: {KAIKKI_URL}")
        
        gz_path = os.path.join(self.output_dir, DICTIONARY_GZ)
        jsonl_path = os.path.join(self.output_dir, DICTIONARY_FILE)
        
        if os.path.exists(jsonl_path):
            print(f"   ✅ Dictionary already exists: {jsonl_path}")
            return True
        
        try:
            # Download compressed file
            print("   Downloading (this may take a few minutes)...")
            urllib.request.urlretrieve(KAIKKI_URL, gz_path)
            print(f"   ✅ Downloaded: {gz_path}")
            
            # Decompress
            print("   Decompressing...")
            with gzip.open(gz_path, 'rb') as f_in:
                with open(jsonl_path, 'wb') as f_out:
                    shutil.copyfileobj(f_in, f_out)
            
            # Clean up compressed file
            os.remove(gz_path)
            print(f"   ✅ Decompressed: {jsonl_path}")
            
            return True
            
        except Exception as e:
            print(f"   ❌ Error downloading dictionary: {e}")
            return False
    
    def extract_vocabulary(self, max_words: int = 5000, use_frequency_filter: bool = True) -> List[Dict]:
        """Extract vocabulary from the Kaikki dictionary."""
        print(f"\n📚 Extracting vocabulary (target: {max_words} words)...")
        
        # Load frequency list if available and filtering is enabled
        if use_frequency_filter and not self.frequency_list:
            self.load_frequency_list()
        
        using_freq = use_frequency_filter and len(self.frequency_list) > 0
        if using_freq:
            print(f"   🎯 Filtering to common words from frequency list")
        
        jsonl_path = os.path.join(self.output_dir, DICTIONARY_FILE)
        
        if not os.path.exists(jsonl_path):
            print(f"   ❌ Dictionary not found: {jsonl_path}")
            print("   Run with --download first")
            return []
        
        extracted = []
        seen_words = set()
        line_count = 0
        freq_matches = 0
        
        with open(jsonl_path, 'r', encoding='utf-8') as f:
            for line in f:
                line_count += 1
                if line_count % 50000 == 0:
                    print(f"   Processing line {line_count:,}... ({len(extracted)} words extracted, {freq_matches} from freq list)")
                
                try:
                    entry = json.loads(line.strip())
                    
                    # Get basic info
                    word = entry.get('word', '').strip()
                    pos = entry.get('pos', '').lower()
                    
                    # Skip if already seen or empty
                    if not word or word in seen_words:
                        continue
                    
                    # Skip if not a useful word type
                    if pos not in POS_MAPPING:
                        continue
                    
                    # Skip very short words (likely abbreviations) or very long ones
                    # Minimum 2 characters for frequency list words, 3 for others
                    min_len = 2 if word.lower() in self.frequency_list else 3
                    if len(word) < min_len or len(word) > 30:
                        continue
                    
                    # Skip words that are all uppercase (abbreviations)
                    if word.isupper():
                        continue
                    
                    # Skip words with non-Greek characters (except common punctuation)
                    if not self._is_greek_word(word):
                        continue
                    
                    # Extract English translation
                    english = self._extract_english(entry)
                    if not english:
                        continue  # Skip words without translations
                    
                    # Check if in frequency list
                    word_lower = word.lower()
                    is_common = word_lower in self.frequency_list
                    if is_common:
                        freq_matches += 1
                    
                    # Build word entry
                    word_entry = {
                        'word': word,
                        'english': english,
                        'word_type': POS_MAPPING[pos],
                        'gender': self._extract_gender(entry),
                        'tags': self._detect_thematic_tags(word, english),
                        'example_sentence': self._extract_example(entry),
                        'audio_url': self._extract_audio(entry),
                        'difficulty_level': self._estimate_difficulty(word, pos),
                        'frequency_rank': self.frequency_rank.get(word_lower, 99999),
                        'is_common': is_common,
                    }
                    
                    extracted.append(word_entry)
                    seen_words.add(word)
                    self.word_count[POS_MAPPING[pos]] += 1
                    
                except json.JSONDecodeError:
                    continue
                except Exception as e:
                    continue
        
        # Sort: prioritize common words by frequency rank, then others by difficulty
        if using_freq:
            # Common words first (sorted by frequency rank), then uncommon words
            common_words = [w for w in extracted if w['is_common']]
            uncommon_words = [w for w in extracted if not w['is_common']]
            
            common_words.sort(key=lambda x: x['frequency_rank'])
            uncommon_words.sort(key=lambda x: (x['difficulty_level'], len(x['word'])))
            
            # Take common words first, fill remainder with uncommon if needed
            self.words = common_words[:max_words]
            if len(self.words) < max_words:
                self.words.extend(uncommon_words[:max_words - len(self.words)])
            
            print(f"\n   ✅ Extracted {len(self.words)} words ({len(common_words)} from frequency list)")
        else:
            extracted.sort(key=lambda x: (x['difficulty_level'], len(x['word'])))
            self.words = extracted[:max_words]
            print(f"\n   ✅ Extracted {len(self.words)} words")
        
        print(f"   Word type breakdown:")
        for word_type, count in sorted(self.word_count.items(), key=lambda x: -x[1]):
            print(f"      • {word_type}: {count}")
        
        return self.words
    
    def _is_greek_word(self, word: str) -> bool:
        """Check if word contains primarily Greek characters."""
        greek_chars = sum(1 for c in word if '\u0370' <= c <= '\u03FF' or '\u1F00' <= c <= '\u1FFF')
        return greek_chars >= len(word) * 0.8
    
    def _extract_english(self, entry: Dict) -> str:
        """Extract English translation from entry."""
        glosses = []
        for sense in entry.get('senses', []):
            for gloss in sense.get('glosses', []):
                if gloss and isinstance(gloss, str):
                    # Clean up the gloss
                    gloss = gloss.strip()
                    if gloss and len(gloss) < 200:  # Skip very long definitions
                        # Filter out grammatical form descriptions (not real translations)
                        skip_patterns = [
                            'singular of ', 'plural of ', 'vocative ', 'genitive ',
                            'accusative ', 'nominative ', 'dative ', 'participle of ',
                            'inflection of ', 'form of ', 'alternative form of ',
                            'first-person ', 'second-person ', 'third-person ',
                            'masculine ', 'feminine ', 'neuter ',
                            'present tense', 'past tense', 'imperfect ',
                            'aorist ', 'perfect ', 'imperative of ',
                            'misspelling of ', 'contraction of ', 'alternative spelling of ',
                            'obsolete form of ', 'archaic form of ', 'rare form of '
                        ]
                        if not any(pattern in gloss.lower() for pattern in skip_patterns):
                            glosses.append(gloss)
        
        if glosses:
            # Return first 2-3 meanings
            return '; '.join(glosses[:3])
        return ''
    
    def _extract_gender(self, entry: Dict) -> Optional[str]:
        """Extract grammatical gender for nouns."""
        pos = entry.get('pos', '').lower()
        if pos != 'noun':
            return None
        
        # Check head templates for gender info
        for head in entry.get('head_templates', []):
            args = head.get('args', {})
            for key, value in args.items():
                if value in ['m', 'masculine']:
                    return 'masculine'
                elif value in ['f', 'feminine']:
                    return 'feminine'
                elif value in ['n', 'neuter']:
                    return 'neuter'
        
        # Check forms for gender tags
        for form in entry.get('forms', []):
            tags = form.get('tags', [])
            if 'masculine' in tags:
                return 'masculine'
            elif 'feminine' in tags:
                return 'feminine'
            elif 'neuter' in tags:
                return 'neuter'
        
        return None
    
    def _detect_thematic_tags(self, word: str, english: str) -> str:
        """Detect thematic categories for the word."""
        tags = set()
        
        combined = f"{word.lower()} {english.lower()}"
        
        for theme, patterns in THEMATIC_PATTERNS.items():
            for pattern in patterns:
                if pattern.lower() in combined:
                    tags.add(theme)
                    break
        
        # Also check English keywords
        if any(kw in english.lower() for kw in ['food', 'eat', 'drink', 'cook']):
            tags.add('food')
        if any(kw in english.lower() for kw in ['family', 'mother', 'father', 'brother', 'sister']):
            tags.add('family')
        if any(kw in english.lower() for kw in ['travel', 'trip', 'journey', 'airport', 'hotel']):
            tags.add('travel')
        
        return ','.join(sorted(tags)) if tags else ''
    
    def _extract_example(self, entry: Dict) -> str:
        """Extract example sentence if available."""
        for sense in entry.get('senses', []):
            for example in sense.get('examples', []):
                if isinstance(example, dict):
                    text = example.get('text', '')
                    if text and len(text) < 300:
                        return text
                elif isinstance(example, str) and len(example) < 300:
                    return example
        return ''
    
    def _extract_audio(self, entry: Dict) -> Optional[str]:
        """Extract audio URL if available."""
        sounds = entry.get('sounds', [])
        for sound in sounds:
            if 'ogg_url' in sound:
                return sound['ogg_url']
            elif 'mp3_url' in sound:
                return sound['mp3_url']
        return None
    
    def _estimate_difficulty(self, word: str, pos: str) -> int:
        """Estimate word difficulty (1-5 scale)."""
        difficulty = 1
        
        # Very short words (3-4 chars) are often common and easy
        if len(word) <= 4:
            difficulty = 1
        # Medium length words (5-8 chars) are moderate
        elif len(word) <= 8:
            difficulty = 2
        # Longer words are harder
        elif len(word) <= 12:
            difficulty = 3
        else:
            difficulty = 4
        
        # Some word types are harder
        if pos in ['phrase', 'interjection']:
            difficulty += 1
        
        # Words with thematic tags are more useful - prioritize them
        # (This will be checked separately)
        
        # Cap at 5
        return min(difficulty, 5)
    
    def save_vocabulary(self, filename: str = "vocabulary.json"):
        """Save extracted vocabulary to JSON file."""
        output_path = os.path.join(self.output_dir, filename)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(self.words, f, ensure_ascii=False, indent=2)
        
        print(f"   ✅ Saved vocabulary to: {output_path}")
        return output_path
    
    def create_database_tables(self, db_path: str = DB_PATH):
        """Create vocabulary-related database tables."""
        print(f"\n🗄️ Creating database tables...")
        
        # Ensure database directory exists
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Create common_words table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS common_words (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                word TEXT NOT NULL UNIQUE,
                english TEXT NOT NULL,
                word_type TEXT NOT NULL,
                frequency_rank INTEGER,
                gender TEXT,
                case_forms TEXT,
                plural_forms TEXT,
                example_sentence TEXT,
                audio_url TEXT,
                difficulty_level INTEGER DEFAULT 1,
                tags TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Create practice_sentences table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS practice_sentences (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                greek_text TEXT NOT NULL,
                english_translation TEXT NOT NULL,
                difficulty_level INTEGER DEFAULT 1,
                target_words TEXT,
                sentence_type TEXT,
                audio_url TEXT,
                tags TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Create user_vocabulary_progress table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS user_vocabulary_progress (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                word_id INTEGER NOT NULL,
                attempts INTEGER DEFAULT 0,
                correct_attempts INTEGER DEFAULT 0,
                last_attempt DATETIME,
                next_review DATETIME,
                ease_factor REAL DEFAULT 2.5,
                interval_days INTEGER DEFAULT 1,
                mastery_level INTEGER DEFAULT 0,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id),
                FOREIGN KEY (word_id) REFERENCES common_words(id),
                UNIQUE(user_id, word_id)
            )
        """)
        
        # Create indices for better query performance
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_common_words_type ON common_words(word_type)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_common_words_difficulty ON common_words(difficulty_level)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_common_words_tags ON common_words(tags)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_user_vocab_progress_user ON user_vocabulary_progress(user_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_user_vocab_progress_review ON user_vocabulary_progress(next_review)")
        
        conn.commit()
        conn.close()
        
        print(f"   ✅ Tables created in: {db_path}")
    
    def import_to_database(self, db_path: str = DB_PATH):
        """Import vocabulary to database."""
        print(f"\n📥 Importing vocabulary to database...")
        
        if not self.words:
            print("   ❌ No vocabulary to import. Run extraction first.")
            return
        
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        imported = 0
        skipped = 0
        
        for i, word_entry in enumerate(self.words, 1):
            try:
                cursor.execute("""
                    INSERT OR IGNORE INTO common_words 
                    (word, english, word_type, frequency_rank, gender, example_sentence, 
                     audio_url, difficulty_level, tags)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    word_entry['word'],
                    word_entry['english'],
                    word_entry['word_type'],
                    i,  # frequency_rank based on extraction order
                    word_entry['gender'],
                    word_entry['example_sentence'],
                    word_entry['audio_url'],
                    word_entry['difficulty_level'],
                    word_entry['tags']
                ))
                
                if cursor.rowcount > 0:
                    imported += 1
                else:
                    skipped += 1
                    
            except Exception as e:
                print(f"   ⚠️ Error importing '{word_entry['word']}': {e}")
                skipped += 1
        
        conn.commit()
        conn.close()
        
        print(f"   ✅ Imported: {imported} words")
        print(f"   ⏭️ Skipped (duplicates): {skipped} words")
    
    def print_summary(self):
        """Print summary of extracted vocabulary."""
        print(f"\n📊 Vocabulary Summary")
        print(f"=" * 40)
        print(f"Total words: {len(self.words)}")
        
        # Count by type
        type_counts = defaultdict(int)
        for word in self.words:
            type_counts[word['word_type']] += 1
        
        print(f"\nBy word type:")
        for word_type, count in sorted(type_counts.items(), key=lambda x: -x[1]):
            print(f"  • {word_type}: {count}")
        
        # Count by difficulty
        diff_counts = defaultdict(int)
        for word in self.words:
            diff_counts[word['difficulty_level']] += 1
        
        print(f"\nBy difficulty:")
        for diff, count in sorted(diff_counts.items()):
            print(f"  • Level {diff}: {count}")
        
        # Count words with tags
        tagged = sum(1 for w in self.words if w['tags'])
        print(f"\nThematic tags: {tagged} words categorized")
        
        # Count words with audio
        with_audio = sum(1 for w in self.words if w['audio_url'])
        print(f"Audio available: {with_audio} words")
        
        # Count words with examples
        with_examples = sum(1 for w in self.words if w['example_sentence'])
        print(f"Example sentences: {with_examples} words")


def main():
    parser = argparse.ArgumentParser(description='Build Greek vocabulary database')
    parser.add_argument('--download', action='store_true', help='Download Kaikki dictionary')
    parser.add_argument('--extract', action='store_true', help='Extract vocabulary from dictionary')
    parser.add_argument('--import', dest='do_import', action='store_true', help='Import to database')
    parser.add_argument('--all', action='store_true', help='Run all steps')
    parser.add_argument('--max-words', type=int, default=2000, help='Maximum words to extract (default: 2000)')
    parser.add_argument('--db-path', type=str, default=DB_PATH, help='Database path')
    
    args = parser.parse_args()
    
    # If no arguments, show help
    if not any([args.download, args.extract, args.do_import, args.all]):
        parser.print_help()
        print("\n💡 Quick start: python build_vocabulary.py --all")
        return
    
    builder = VocabularyBuilder()
    
    # Run selected steps
    if args.download or args.all:
        if not builder.download_dictionary():
            print("❌ Download failed. Exiting.")
            return
    
    if args.extract or args.all:
        builder.extract_vocabulary(max_words=args.max_words)
        builder.save_vocabulary()
        builder.print_summary()
    
    if args.do_import or args.all:
        if not builder.words:
            # Try to load from saved file
            vocab_path = os.path.join(builder.output_dir, "vocabulary.json")
            if os.path.exists(vocab_path):
                with open(vocab_path, 'r', encoding='utf-8') as f:
                    builder.words = json.load(f)
                print(f"   Loaded {len(builder.words)} words from {vocab_path}")
            else:
                print("   ❌ No vocabulary data. Run --extract first.")
                return
        
        builder.create_database_tables(args.db_path)
        builder.import_to_database(args.db_path)
    
    print("\n✅ Done!")


if __name__ == "__main__":
    main()

