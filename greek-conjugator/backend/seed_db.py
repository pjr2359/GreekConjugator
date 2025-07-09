#!/usr/bin/env python3
import sys
import os

# Add the project directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from app.models import db, Verb, Conjugation

app = create_app()

# Sample Greek verbs data (top 20 most frequent)
SAMPLE_VERBS = [
    {
        'infinitive': 'είμαι',
        'english': 'to be',
        'frequency': 1,
        'difficulty': 1,
        'verb_group': 'irregular',
        'transitivity': 'intransitive',
        'tags': ['existence', 'state']
    },
    {
        'infinitive': 'γράφω',
        'english': 'to write',
        'frequency': 2,
        'difficulty': 2,
        'verb_group': 'A',
        'transitivity': 'transitive',
        'tags': ['communication', 'action']
    },
    {
        'infinitive': 'λέω',
        'english': 'to say',
        'frequency': 3,
        'difficulty': 2,
        'verb_group': 'A',
        'transitivity': 'transitive',
        'tags': ['communication', 'speech']
    },
    {
        'infinitive': 'κάνω',
        'english': 'to do/make',
        'frequency': 4,
        'difficulty': 1,
        'verb_group': 'A',
        'transitivity': 'transitive',
        'tags': ['action', 'creation']
    },
    {
        'infinitive': 'πηγαίνω',
        'english': 'to go',
        'frequency': 5,
        'difficulty': 2,
        'verb_group': 'A',
        'transitivity': 'intransitive',
        'tags': ['movement', 'travel']
    },
    {
        'infinitive': 'έρχομαι',
        'english': 'to come',
        'frequency': 6,
        'difficulty': 3,
        'verb_group': 'irregular',
        'transitivity': 'intransitive',
        'tags': ['movement', 'arrival']
    },
    {
        'infinitive': 'βλέπω',
        'english': 'to see',
        'frequency': 7,
        'difficulty': 2,
        'verb_group': 'A',
        'transitivity': 'transitive',
        'tags': ['perception', 'sight']
    },
    {
        'infinitive': 'έχω',
        'english': 'to have',
        'frequency': 8,
        'difficulty': 1,
        'verb_group': 'A',
        'transitivity': 'transitive',
        'tags': ['possession', 'state']
    },
    {
        'infinitive': 'ξέρω',
        'english': 'to know',
        'frequency': 9,
        'difficulty': 2,
        'verb_group': 'A',
        'transitivity': 'transitive',
        'tags': ['knowledge', 'cognition']
    },
    {
        'infinitive': 'θέλω',
        'english': 'to want',
        'frequency': 10,
        'difficulty': 2,
        'verb_group': 'A',
        'transitivity': 'transitive',
        'tags': ['desire', 'emotion']
    },
    {
        'infinitive': 'μπορώ',
        'english': 'can/to be able',
        'frequency': 11,
        'difficulty': 2,
        'verb_group': 'A',
        'transitivity': 'transitive',
        'tags': ['ability', 'modal']
    },
    {
        'infinitive': 'παίρνω',
        'english': 'to take',
        'frequency': 12,
        'difficulty': 2,
        'verb_group': 'A',
        'transitivity': 'transitive',
        'tags': ['action', 'possession']
    },
    {
        'infinitive': 'δίνω',
        'english': 'to give',
        'frequency': 13,
        'difficulty': 2,
        'verb_group': 'A',
        'transitivity': 'transitive',
        'tags': ['action', 'transfer']
    },
    {
        'infinitive': 'μένω',
        'english': 'to stay/live',
        'frequency': 14,
        'difficulty': 2,
        'verb_group': 'A',
        'transitivity': 'intransitive',
        'tags': ['residence', 'state']
    },
    {
        'infinitive': 'φεύγω',
        'english': 'to leave',
        'frequency': 15,
        'difficulty': 2,
        'verb_group': 'A',
        'transitivity': 'intransitive',
        'tags': ['movement', 'departure']
    },
    {
        'infinitive': 'τρώω',
        'english': 'to eat',
        'frequency': 16,
        'difficulty': 2,
        'verb_group': 'A',
        'transitivity': 'transitive',
        'tags': ['consumption', 'daily_life']
    },
    {
        'infinitive': 'πίνω',
        'english': 'to drink',
        'frequency': 17,
        'difficulty': 2,
        'verb_group': 'A',
        'transitivity': 'transitive',
        'tags': ['consumption', 'daily_life']
    },
    {
        'infinitive': 'αγαπώ',
        'english': 'to love',
        'frequency': 18,
        'difficulty': 2,
        'verb_group': 'A',
        'transitivity': 'transitive',
        'tags': ['emotion', 'relationships']
    },
    {
        'infinitive': 'καταλαβαίνω',
        'english': 'to understand',
        'frequency': 19,
        'difficulty': 3,
        'verb_group': 'A',
        'transitivity': 'transitive',
        'tags': ['cognition', 'comprehension']
    },
    {
        'infinitive': 'δουλεύω',
        'english': 'to work',
        'frequency': 20,
        'difficulty': 2,
        'verb_group': 'A',
        'transitivity': 'intransitive',
        'tags': ['work', 'activity']
    }
]

# Sample conjugations for multiple verbs
VERB_CONJUGATIONS = {
    'γράφω': [
        # Present tense
        {'tense': 'present', 'mood': 'indicative', 'voice': 'active', 'person': '1st', 'number': 'singular', 'form': 'γράφω'},
        {'tense': 'present', 'mood': 'indicative', 'voice': 'active', 'person': '2nd', 'number': 'singular', 'form': 'γράφεις'},
        {'tense': 'present', 'mood': 'indicative', 'voice': 'active', 'person': '3rd', 'number': 'singular', 'form': 'γράφει'},
        {'tense': 'present', 'mood': 'indicative', 'voice': 'active', 'person': '1st', 'number': 'plural', 'form': 'γράφουμε'},
        {'tense': 'present', 'mood': 'indicative', 'voice': 'active', 'person': '2nd', 'number': 'plural', 'form': 'γράφετε'},
        {'tense': 'present', 'mood': 'indicative', 'voice': 'active', 'person': '3rd', 'number': 'plural', 'form': 'γράφουν'},
        
        # Aorist tense
        {'tense': 'aorist', 'mood': 'indicative', 'voice': 'active', 'person': '1st', 'number': 'singular', 'form': 'έγραψα'},
        {'tense': 'aorist', 'mood': 'indicative', 'voice': 'active', 'person': '2nd', 'number': 'singular', 'form': 'έγραψες'},
        {'tense': 'aorist', 'mood': 'indicative', 'voice': 'active', 'person': '3rd', 'number': 'singular', 'form': 'έγραψε'},
        {'tense': 'aorist', 'mood': 'indicative', 'voice': 'active', 'person': '1st', 'number': 'plural', 'form': 'γράψαμε'},
        {'tense': 'aorist', 'mood': 'indicative', 'voice': 'active', 'person': '2nd', 'number': 'plural', 'form': 'γράψατε'},
        {'tense': 'aorist', 'mood': 'indicative', 'voice': 'active', 'person': '3rd', 'number': 'plural', 'form': 'έγραψαν'},
    ],
    'είμαι': [
        # Present tense
        {'tense': 'present', 'mood': 'indicative', 'voice': 'active', 'person': '1st', 'number': 'singular', 'form': 'είμαι'},
        {'tense': 'present', 'mood': 'indicative', 'voice': 'active', 'person': '2nd', 'number': 'singular', 'form': 'είσαι'},
        {'tense': 'present', 'mood': 'indicative', 'voice': 'active', 'person': '3rd', 'number': 'singular', 'form': 'είναι'},
        {'tense': 'present', 'mood': 'indicative', 'voice': 'active', 'person': '1st', 'number': 'plural', 'form': 'είμαστε'},
        {'tense': 'present', 'mood': 'indicative', 'voice': 'active', 'person': '2nd', 'number': 'plural', 'form': 'είστε'},
        {'tense': 'present', 'mood': 'indicative', 'voice': 'active', 'person': '3rd', 'number': 'plural', 'form': 'είναι'},
    ],
    'έχω': [
        # Present tense
        {'tense': 'present', 'mood': 'indicative', 'voice': 'active', 'person': '1st', 'number': 'singular', 'form': 'έχω'},
        {'tense': 'present', 'mood': 'indicative', 'voice': 'active', 'person': '2nd', 'number': 'singular', 'form': 'έχεις'},
        {'tense': 'present', 'mood': 'indicative', 'voice': 'active', 'person': '3rd', 'number': 'singular', 'form': 'έχει'},
        {'tense': 'present', 'mood': 'indicative', 'voice': 'active', 'person': '1st', 'number': 'plural', 'form': 'έχουμε'},
        {'tense': 'present', 'mood': 'indicative', 'voice': 'active', 'person': '2nd', 'number': 'plural', 'form': 'έχετε'},
        {'tense': 'present', 'mood': 'indicative', 'voice': 'active', 'person': '3rd', 'number': 'plural', 'form': 'έχουν'},
    ],
    'κάνω': [
        # Present tense
        {'tense': 'present', 'mood': 'indicative', 'voice': 'active', 'person': '1st', 'number': 'singular', 'form': 'κάνω'},
        {'tense': 'present', 'mood': 'indicative', 'voice': 'active', 'person': '2nd', 'number': 'singular', 'form': 'κάνεις'},
        {'tense': 'present', 'mood': 'indicative', 'voice': 'active', 'person': '3rd', 'number': 'singular', 'form': 'κάνει'},
        {'tense': 'present', 'mood': 'indicative', 'voice': 'active', 'person': '1st', 'number': 'plural', 'form': 'κάνουμε'},
        {'tense': 'present', 'mood': 'indicative', 'voice': 'active', 'person': '2nd', 'number': 'plural', 'form': 'κάνετε'},
        {'tense': 'present', 'mood': 'indicative', 'voice': 'active', 'person': '3rd', 'number': 'plural', 'form': 'κάνουν'},
    ],
    'λέω': [
        # Present tense
        {'tense': 'present', 'mood': 'indicative', 'voice': 'active', 'person': '1st', 'number': 'singular', 'form': 'λέω'},
        {'tense': 'present', 'mood': 'indicative', 'voice': 'active', 'person': '2nd', 'number': 'singular', 'form': 'λες'},
        {'tense': 'present', 'mood': 'indicative', 'voice': 'active', 'person': '3rd', 'number': 'singular', 'form': 'λέει'},
        {'tense': 'present', 'mood': 'indicative', 'voice': 'active', 'person': '1st', 'number': 'plural', 'form': 'λέμε'},
        {'tense': 'present', 'mood': 'indicative', 'voice': 'active', 'person': '2nd', 'number': 'plural', 'form': 'λέτε'},
        {'tense': 'present', 'mood': 'indicative', 'voice': 'active', 'person': '3rd', 'number': 'plural', 'form': 'λένε'},
    ]
}

def seed_database():
    with app.app_context():
        print("🗄️  Creating database tables...")
        db.create_all()
        
        print("🌱 Seeding verbs...")
        for verb_data in SAMPLE_VERBS:
            existing_verb = Verb.query.filter_by(infinitive=verb_data['infinitive']).first()
            if not existing_verb:
                # Convert tags list to string for SQLite storage
                verb_data_copy = verb_data.copy()
                if 'tags' in verb_data_copy and isinstance(verb_data_copy['tags'], list):
                    verb_data_copy['tags'] = ', '.join(verb_data_copy['tags'])
                
                verb = Verb(**verb_data_copy)
                db.session.add(verb)
                db.session.flush()  # Get the ID
                
                # Add conjugations for verbs that have them defined
                if verb_data['infinitive'] in VERB_CONJUGATIONS:
                    print(f"📝 Adding conjugations for {verb_data['infinitive']}...")
                    for conj_data in VERB_CONJUGATIONS[verb_data['infinitive']]:
                        conjugation = Conjugation(
                            verb_id=verb.id,
                            **conj_data
                        )
                        db.session.add(conjugation)
        
        db.session.commit()
        print("✅ Database seeded successfully!")
        print("🎯 Ready to start practicing Greek!")

if __name__ == '__main__':
    seed_database()