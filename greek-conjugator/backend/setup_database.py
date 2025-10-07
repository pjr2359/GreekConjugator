#!/usr/bin/env python3
"""
Simple Database Setup for Greek Conjugator

Creates the database tables and adds sample data without requiring Flask app context.
"""

import sqlite3
import os

def create_tables():
    """Create the database tables."""
    db_path = 'greek_conjugator_dev.db'
    
    # Remove existing database if it exists
    if os.path.exists(db_path):
        os.remove(db_path)
        print(f"🗑️  Removed existing database: {db_path}")
    
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
    
    # Create users table
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
    
    # Create user_progress table
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
    
    # Create practice_sessions table
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
    
    return conn

def add_sample_data(conn):
    """Add sample verbs and conjugations."""
    cursor = conn.cursor()
    
    print("🌱 Adding sample verbs and conjugations...")
    
    # Sample verbs
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
    
    # Sample conjugations for γράφω
    grafo_conjugations = [
        # Present indicative active
        (2, 'present', 'indicative', 'active', '1st', 'singular', 'γράφω'),
        (2, 'present', 'indicative', 'active', '2nd', 'singular', 'γράφεις'),
        (2, 'present', 'indicative', 'active', '3rd', 'singular', 'γράφει'),
        (2, 'present', 'indicative', 'active', '1st', 'plural', 'γράφουμε'),
        (2, 'present', 'indicative', 'active', '2nd', 'plural', 'γράφετε'),
        (2, 'present', 'indicative', 'active', '3rd', 'plural', 'γράφουν'),
        
        # Aorist indicative active
        (2, 'aorist', 'indicative', 'active', '1st', 'singular', 'έγραψα'),
        (2, 'aorist', 'indicative', 'active', '2nd', 'singular', 'έγραψες'),
        (2, 'aorist', 'indicative', 'active', '3rd', 'singular', 'έγραψε'),
        (2, 'aorist', 'indicative', 'active', '1st', 'plural', 'γράψαμε'),
        (2, 'aorist', 'indicative', 'active', '2nd', 'plural', 'γράψατε'),
        (2, 'aorist', 'indicative', 'active', '3rd', 'plural', 'έγραψαν')
    ]
    
    # Sample conjugations for είμαι
    eimai_conjugations = [
        (1, 'present', 'indicative', 'active', '1st', 'singular', 'είμαι'),
        (1, 'present', 'indicative', 'active', '2nd', 'singular', 'είσαι'),
        (1, 'present', 'indicative', 'active', '3rd', 'singular', 'είναι'),
        (1, 'present', 'indicative', 'active', '1st', 'plural', 'είμαστε'),
        (1, 'present', 'indicative', 'active', '2nd', 'plural', 'είστε'),
        (1, 'present', 'indicative', 'active', '3rd', 'plural', 'είναι')
    ]
    
    # Sample conjugations for έχω
    echo_conjugations = [
        (8, 'present', 'indicative', 'active', '1st', 'singular', 'έχω'),
        (8, 'present', 'indicative', 'active', '2nd', 'singular', 'έχεις'),
        (8, 'present', 'indicative', 'active', '3rd', 'singular', 'έχει'),
        (8, 'present', 'indicative', 'active', '1st', 'plural', 'έχουμε'),
        (8, 'present', 'indicative', 'active', '2nd', 'plural', 'έχετε'),
        (8, 'present', 'indicative', 'active', '3rd', 'plural', 'έχουν')
    ]
    
    # Insert conjugations
    all_conjugations = grafo_conjugations + eimai_conjugations + echo_conjugations
    
    for conj_data in all_conjugations:
        cursor.execute('''
            INSERT INTO conjugations (verb_id, tense, mood, voice, person, number, form)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', conj_data)
    
    conn.commit()
    print("✅ Sample data added successfully!")

def main():
    """Main function to set up the database."""
    print("🚀 Setting up Greek Conjugator Database")
    print("=" * 50)
    
    try:
        # Create tables
        conn = create_tables()
        
        # Add sample data
        add_sample_data(conn)
        
        # Verify setup
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM verbs")
        verb_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM conjugations")
        conjugation_count = cursor.fetchone()[0]
        
        print(f"\n📊 Database Setup Complete!")
        print(f"   • Verbs: {verb_count}")
        print(f"   • Conjugations: {conjugation_count}")
        print(f"   • Database file: greek_conjugator_dev.db")
        
        conn.close()
        
        print("\n✅ Database is ready for testing!")
        
    except Exception as e:
        print(f"❌ Error setting up database: {e}")

if __name__ == '__main__':
    main() 