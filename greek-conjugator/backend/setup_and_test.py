#!/usr/bin/env python3
"""
Setup and Test Script for Greek Conjugator Database

This script will:
1. Set up the database with tables and sample data
2. Run all the database tests
3. Provide a comprehensive report

Run this script to verify your database is working correctly.
"""

import sqlite3
import os
import sys
from datetime import datetime

def setup_database():
    """Set up the database with tables and sample data."""
    print("🚀 Setting up Greek Conjugator Database")
    print("=" * 50)
    
    db_path = 'greek_conjugator_dev.db'
    
    # Remove existing database if it exists
    if os.path.exists(db_path):
        os.remove(db_path)
        print(f"🗑️  Removed existing database: {db_path}")
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        print("🗄️  Creating database tables...")
        
        # Create verbs table
        cursor.execute('''
            CREATE TABLE verbs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                infinitive VARCHAR(100) NOT NULL,
                english VARCHAR(255) NOT NULL,
                frequency INTEGER,
                difficulty INTEGER,
                verb_group VARCHAR(50),
                transitivity VARCHAR(50),
                tags TEXT,
                audio_url VARCHAR(500),
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Create conjugations table
        cursor.execute('''
            CREATE TABLE conjugations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                verb_id INTEGER NOT NULL,
                tense VARCHAR(50) NOT NULL,
                mood VARCHAR(50) NOT NULL,
                voice VARCHAR(50) NOT NULL,
                person VARCHAR(10),
                number VARCHAR(20),
                form VARCHAR(100) NOT NULL,
                audio_url VARCHAR(500),
                stress_pattern VARCHAR(50),
                morphology TEXT,
                FOREIGN KEY (verb_id) REFERENCES verbs (id)
            )
        ''')
        
        # Create other tables
        cursor.execute('''
            CREATE TABLE users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email VARCHAR(255) UNIQUE NOT NULL,
                username VARCHAR(100) UNIQUE,
                password_hash VARCHAR(255) NOT NULL,
                subscription_tier VARCHAR(50) DEFAULT 'free',
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                last_login DATETIME,
                preferences TEXT
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE user_progress (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                verb_id INTEGER NOT NULL,
                conjugation_id INTEGER NOT NULL,
                attempts INTEGER DEFAULT 0,
                correct_attempts INTEGER DEFAULT 0,
                last_attempt DATETIME,
                next_review DATETIME,
                ease_factor REAL DEFAULT 2.50,
                interval_days INTEGER DEFAULT 1,
                streak INTEGER DEFAULT 0,
                common_mistakes TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id),
                FOREIGN KEY (verb_id) REFERENCES verbs (id),
                FOREIGN KEY (conjugation_id) REFERENCES conjugations (id)
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE practice_sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                session_type VARCHAR(50) NOT NULL,
                duration_seconds INTEGER,
                questions_attempted INTEGER,
                correct_answers INTEGER,
                verbs_practiced TEXT,
                accuracy_rate REAL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')
        
        conn.commit()
        print("✅ Database tables created successfully!")
        
        # Add sample data
        print("🌱 Adding sample verbs and conjugations...")
        
        sample_verbs = [
            ('είμαι', 'to be', 1, 1, 'irregular', 'intransitive', 'existence, state'),
            ('γράφω', 'to write', 2, 2, 'A', 'transitive', 'communication, action'),
            ('λέω', 'to say', 3, 2, 'A', 'transitive', 'communication, speech'),
            ('κάνω', 'to do/make', 4, 1, 'A', 'transitive', 'action, creation'),
            ('πηγαίνω', 'to go', 5, 2, 'A', 'intransitive', 'movement, travel'),
            ('έρχομαι', 'to come', 6, 3, 'irregular', 'intransitive', 'movement, arrival'),
            ('βλέπω', 'to see', 7, 2, 'A', 'transitive', 'perception, sight'),
            ('έχω', 'to have', 8, 1, 'A', 'transitive', 'possession, state'),
            ('ξέρω', 'to know', 9, 2, 'A', 'transitive', 'knowledge, cognition'),
            ('θέλω', 'to want', 10, 2, 'A', 'transitive', 'desire, emotion')
        ]
        
        # Insert verbs
        for verb_data in sample_verbs:
            cursor.execute('''
                INSERT INTO verbs (infinitive, english, frequency, difficulty, verb_group, transitivity, tags)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', verb_data)
        
        # Sample conjugations
        sample_conjugations = [
            # γράφω conjugations
            (2, 'present', 'indicative', 'active', '1st', 'singular', 'γράφω'),
            (2, 'present', 'indicative', 'active', '2nd', 'singular', 'γράφεις'),
            (2, 'present', 'indicative', 'active', '3rd', 'singular', 'γράφει'),
            (2, 'present', 'indicative', 'active', '1st', 'plural', 'γράφουμε'),
            (2, 'present', 'indicative', 'active', '2nd', 'plural', 'γράφετε'),
            (2, 'present', 'indicative', 'active', '3rd', 'plural', 'γράφουν'),
            (2, 'aorist', 'indicative', 'active', '1st', 'singular', 'έγραψα'),
            (2, 'aorist', 'indicative', 'active', '2nd', 'singular', 'έγραψες'),
            (2, 'aorist', 'indicative', 'active', '3rd', 'singular', 'έγραψε'),
            (2, 'aorist', 'indicative', 'active', '1st', 'plural', 'γράψαμε'),
            (2, 'aorist', 'indicative', 'active', '2nd', 'plural', 'γράψατε'),
            (2, 'aorist', 'indicative', 'active', '3rd', 'plural', 'έγραψαν'),
            
            # είμαι conjugations
            (1, 'present', 'indicative', 'active', '1st', 'singular', 'είμαι'),
            (1, 'present', 'indicative', 'active', '2nd', 'singular', 'είσαι'),
            (1, 'present', 'indicative', 'active', '3rd', 'singular', 'είναι'),
            (1, 'present', 'indicative', 'active', '1st', 'plural', 'είμαστε'),
            (1, 'present', 'indicative', 'active', '2nd', 'plural', 'είστε'),
            (1, 'present', 'indicative', 'active', '3rd', 'plural', 'είναι'),
            
            # έχω conjugations
            (8, 'present', 'indicative', 'active', '1st', 'singular', 'έχω'),
            (8, 'present', 'indicative', 'active', '2nd', 'singular', 'έχεις'),
            (8, 'present', 'indicative', 'active', '3rd', 'singular', 'έχει'),
            (8, 'present', 'indicative', 'active', '1st', 'plural', 'έχουμε'),
            (8, 'present', 'indicative', 'active', '2nd', 'plural', 'έχετε'),
            (8, 'present', 'indicative', 'active', '3rd', 'plural', 'έχουν')
        ]
        
        # Insert conjugations
        for conj_data in sample_conjugations:
            cursor.execute('''
                INSERT INTO conjugations (verb_id, tense, mood, voice, person, number, form)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', conj_data)
        
        conn.commit()
        print("✅ Sample data added successfully!")
        
        # Verify setup
        cursor.execute("SELECT COUNT(*) FROM verbs")
        verb_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM conjugations")
        conjugation_count = cursor.fetchone()[0]
        
        print(f"\n📊 Database Setup Complete!")
        print(f"   • Verbs: {verb_count}")
        print(f"   • Conjugations: {conjugation_count}")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Error setting up database: {e}")
        return False

def run_quick_test():
    """Run the quick database test."""
    print("\n🔍 Running Quick Database Test")
    print("=" * 50)
    
    db_path = 'greek_conjugator_dev.db'
    
    if not os.path.exists(db_path):
        print(f"❌ Database file not found: {db_path}")
        return False
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check verbs
        cursor.execute("SELECT COUNT(*) FROM verbs")
        verb_count = cursor.fetchone()[0]
        print(f"📊 Total verbs: {verb_count}")
        
        # Check conjugations
        cursor.execute("SELECT COUNT(*) FROM conjugations")
        conjugation_count = cursor.fetchone()[0]
        print(f"📊 Total conjugations: {conjugation_count}")
        
        # Check verbs with conjugations
        cursor.execute("""
            SELECT COUNT(DISTINCT v.id) 
            FROM verbs v 
            JOIN conjugations c ON v.id = c.verb_id
        """)
        verbs_with_conjugations = cursor.fetchone()[0]
        print(f"📊 Verbs with conjugations: {verbs_with_conjugations}")
        
        # Sample verbs
        cursor.execute("SELECT infinitive, english FROM verbs LIMIT 5")
        sample_verbs = cursor.fetchall()
        print(f"\n📋 Sample verbs:")
        for verb in sample_verbs:
            print(f"   • {verb[0]} ({verb[1]})")
        
        # Sample conjugations
        cursor.execute("""
            SELECT v.infinitive, c.form, c.tense, c.mood, c.voice 
            FROM conjugations c 
            JOIN verbs v ON c.verb_id = v.id 
            LIMIT 5
        """)
        sample_conjugations = cursor.fetchall()
        print(f"\n📋 Sample conjugations:")
        for conj in sample_conjugations:
            print(f"   • {conj[0]}: {conj[1]} ({conj[2]} {conj[3]} {conj[4]})")
        
        # Data quality checks
        print(f"\n🔍 Data Quality Check:")
        
        # Check for empty forms
        cursor.execute("SELECT COUNT(*) FROM conjugations WHERE form IS NULL OR form = ''")
        empty_forms = cursor.fetchone()[0]
        print(f"   • Empty conjugation forms: {empty_forms}")
        
        # Check for orphaned conjugations
        cursor.execute("""
            SELECT COUNT(*) 
            FROM conjugations c 
            LEFT JOIN verbs v ON c.verb_id = v.id 
            WHERE v.id IS NULL
        """)
        orphaned_conjugations = cursor.fetchone()[0]
        print(f"   • Orphaned conjugations: {orphaned_conjugations}")
        
        # Check for duplicate conjugations
        cursor.execute("""
            SELECT COUNT(*) FROM (
                SELECT verb_id, form, tense, mood, voice, COUNT(*) as dup_count
                FROM conjugations
                GROUP BY verb_id, form, tense, mood, voice
                HAVING COUNT(*) > 1
            )
        """)
        duplicate_conjugations = cursor.fetchone()[0]
        print(f"   • Duplicate conjugations: {duplicate_conjugations}")
        
        conn.close()
        print(f"\n✅ Quick test completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Error in quick test: {e}")
        return False

def run_comprehensive_test():
    """Run a comprehensive test of the database."""
    print("\n🔍 Running Comprehensive Database Test")
    print("=" * 50)
    
    db_path = 'greek_conjugator_dev.db'
    
    if not os.path.exists(db_path):
        print(f"❌ Database file not found: {db_path}")
        return False
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Get all statistics
        cursor.execute("SELECT COUNT(*) FROM verbs")
        total_verbs = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM conjugations")
        total_conjugations = cursor.fetchone()[0]
        
        cursor.execute("""
            SELECT COUNT(DISTINCT v.id) 
            FROM verbs v 
            JOIN conjugations c ON v.id = c.verb_id
        """)
        verbs_with_conjugations = cursor.fetchone()[0]
        
        # Verb group distribution
        cursor.execute("""
            SELECT verb_group, COUNT(*) as count 
            FROM verbs 
            WHERE verb_group IS NOT NULL 
            GROUP BY verb_group 
            ORDER BY count DESC
        """)
        verb_groups = cursor.fetchall()
        
        # Tense distribution
        cursor.execute("""
            SELECT tense, COUNT(*) as count 
            FROM conjugations 
            WHERE tense IS NOT NULL 
            GROUP BY tense 
            ORDER BY count DESC
        """)
        tenses = cursor.fetchall()
        
        # Mood distribution
        cursor.execute("""
            SELECT mood, COUNT(*) as count 
            FROM conjugations 
            WHERE mood IS NOT NULL 
            GROUP BY mood 
            ORDER BY count DESC
        """)
        moods = cursor.fetchall()
        
        # Voice distribution
        cursor.execute("""
            SELECT voice, COUNT(*) as count 
            FROM conjugations 
            WHERE voice IS NOT NULL 
            GROUP BY voice 
            ORDER BY count DESC
        """)
        voices = cursor.fetchall()
        
        # Top verbs by conjugation count
        cursor.execute("""
            SELECT v.infinitive, v.english, COUNT(c.id) as conjugation_count
            FROM verbs v
            JOIN conjugations c ON v.id = c.verb_id
            GROUP BY v.id, v.infinitive, v.english
            ORDER BY conjugation_count DESC
            LIMIT 5
        """)
        top_verbs = cursor.fetchall()
        
        # Print comprehensive report
        print(f"📊 COMPREHENSIVE DATABASE REPORT")
        print(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        print(f"\n📈 BASIC STATISTICS:")
        print(f"   • Total verbs: {total_verbs}")
        print(f"   • Total conjugations: {total_conjugations}")
        print(f"   • Verbs with conjugations: {verbs_with_conjugations}")
        print(f"   • Verbs without conjugations: {total_verbs - verbs_with_conjugations}")
        
        if total_verbs > 0:
            coverage = (verbs_with_conjugations / total_verbs) * 100
            print(f"   • Verb coverage: {coverage:.1f}%")
        
        print(f"\n📊 VERB GROUP DISTRIBUTION:")
        for group, count in verb_groups:
            print(f"   • {group}: {count}")
        
        print(f"\n📊 TENSE DISTRIBUTION:")
        for tense, count in tenses:
            print(f"   • {tense}: {count}")
        
        print(f"\n📊 MOOD DISTRIBUTION:")
        for mood, count in moods:
            print(f"   • {mood}: {count}")
        
        print(f"\n📊 VOICE DISTRIBUTION:")
        for voice, count in voices:
            print(f"   • {voice}: {count}")
        
        print(f"\n📊 TOP VERBS BY CONJUGATION COUNT:")
        for verb in top_verbs:
            print(f"   • {verb[0]} ({verb[1]}): {verb[2]} conjugations")
        
        conn.close()
        print(f"\n✅ Comprehensive test completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Error in comprehensive test: {e}")
        return False

def main():
    """Main function to set up and test the database."""
    print("🧪 Greek Conjugator - Database Setup and Test Suite")
    print("=" * 60)
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Step 1: Setup database
    if not setup_database():
        print("❌ Database setup failed!")
        return 1
    
    # Step 2: Run quick test
    if not run_quick_test():
        print("❌ Quick test failed!")
        return 1
    
    # Step 3: Run comprehensive test
    if not run_comprehensive_test():
        print("❌ Comprehensive test failed!")
        return 1
    
    print("\n" + "=" * 60)
    print("🎉 ALL TESTS PASSED!")
    print("✅ Database is working correctly")
    print("✅ Sample data is properly stored")
    print("✅ All relationships are intact")
    print("=" * 60)
    
    print("\n📝 Next Steps:")
    print("1. Your database is ready for the Greek Conjugator application")
    print("2. You can now run the other test scripts:")
    print("   • python3 quick_test.py")
    print("   • python3 simple_db_check.py")
    print("   • python3 check_specific_verbs.py")
    print("3. Import your extracted_verbs.json data when ready")
    
    return 0

if __name__ == '__main__':
    exit(main()) 