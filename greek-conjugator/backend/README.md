# Greek Conjugator Backend

A comprehensive backend for learning Greek verb conjugations with a robust database and testing suite.

## 🚀 Quick Start

### Setup Database
```bash
# Create database with sample data
python3 setup_and_test.py

# Or import your full verb dataset
python3 import_verbs_data.py
```

### Run Tests
```bash
# Quick database check
python3 quick_test.py

# Interactive verb checker
python3 verb_checker_simple.py

# Comprehensive database analysis
python3 simple_db_check.py
```

## 📊 Current Database Status

- **612 total verbs** imported successfully
- **4,884 total conjugations** across all verbs
- **80 verbs with complete conjugations** (most important/common verbs)
- **98.4% verb import rate**, **82.4% conjugation import rate**
- **Excellent data quality**: 0 empty forms, 0 orphaned records, 0 duplicates

### Database Coverage
- **Tenses**: Present (3,248), Imperfect (1,113), Future (443), Perfect (74), Aorist (6)
- **Moods**: Indicative (4,239), Imperative (449), Subjunctive (196)
- **Voices**: Active (2,515), Passive (2,369)
- **Verb Groups**: B-group (534), A-group (74), Irregular (4)

## 🧪 Testing Suite

### Quick Tests
- `quick_test.py` - Fast database health check
- `verb_checker_simple.py` - Interactive verb exploration tool
- `simple_db_check.py` - Comprehensive database analysis

### Advanced Tests
- `test_database_integrity.py` - Full integrity verification (requires Flask)
- `test_conjugation_completeness.py` - Conjugation pattern validation (requires Flask)
- `run_database_tests.py` - Complete test suite runner (requires Flask)

### Data Management
- `import_verbs_data.py` - Import verbs from extracted_verbs.json
- `fix_duplicate_conjugation.py` - Clean up duplicate data
- `setup_database.py` - Create database structure
- `setup_and_test.py` - Complete setup and verification

## 📁 Project Structure

```
backend/
├── app/                    # Flask application
│   ├── models/            # Database models
│   ├── routes/            # API endpoints
│   └── services/          # Business logic
├── tests/                 # Testing tools
│   ├── quick_test.py      # Fast database check
│   ├── verb_checker_simple.py  # Interactive verb tool
│   ├── simple_db_check.py # Comprehensive analysis
│   └── import_verbs_data.py    # Data import tool
├── greek_conjugator_dev.db # SQLite database
└── requirements.txt       # Python dependencies
```

## 🔧 Database Schema

### Verbs Table
- `id` - Primary key
- `infinitive` - Greek infinitive form
- `english` - English translation
- `frequency` - Usage frequency rank
- `difficulty` - Learning difficulty (1-3)
- `verb_group` - A, B, or irregular
- `transitivity` - transitive/intransitive
- `tags` - Comma-separated tags
- `audio_url` - Pronunciation audio URL

### Conjugations Table
- `id` - Primary key
- `verb_id` - Foreign key to verbs
- `tense` - present, imperfect, future, perfect, aorist
- `mood` - indicative, imperative, subjunctive
- `voice` - active, passive, middle
- `person` - 1st, 2nd, 3rd
- `number` - singular, plural
- `form` - Greek conjugation form
- `stress_pattern` - Accent pattern
- `morphology` - Grammatical analysis

## 🎯 Key Features

### Smart Practice System
- Adaptive question selection based on user progress
- Spaced repetition algorithm for optimal learning
- Session management with automatic completion
- Progress tracking and statistics

### Data Quality Assurance
- Comprehensive validation of verb and conjugation data
- Automatic detection of duplicates and orphaned records
- Import verification with detailed reporting
- Regular integrity checks

### User Management
- User registration and authentication
- Progress tracking per user
- Session history and statistics
- Personalized learning recommendations

## 🚀 Next Steps

1. **Expand conjugation coverage** for the 532 verbs without conjugations
2. **Improve smart practice algorithm** to handle larger datasets
3. **Add audio pronunciation** support
4. **Enhance UI/UX** with better mobile support
5. **Implement admin interface** for data management

## 📝 Development Notes

- Database uses SQLite for development (easily portable)
- All tests are designed to work without external dependencies
- Import process handles large datasets efficiently
- Data quality is maintained through comprehensive validation

## 🤝 Contributing

1. Run tests before making changes: `python3 quick_test.py`
2. Use the verb checker to verify specific functionality
3. Follow the existing code structure and naming conventions
4. Add tests for new features

## 📞 Support

For issues or questions:
1. Check the testing tools for database health
2. Review the import logs for data issues
3. Use the verb checker to examine specific problems
4. Consult the main TODO.txt for project priorities
