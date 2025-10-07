# Database Testing Tools for Greek Conjugator

This directory contains comprehensive testing tools to verify that all verbs and conjugations have been properly imported into the database.

## 📋 Overview

The testing suite consists of three main components:

1. **Database Integrity Checker** - Verifies all verbs and conjugations from `extracted_verbs.json` are in the database
2. **Conjugation Completeness Checker** - Checks that conjugations follow proper Greek grammar patterns
3. **Verb Checker** - Interactive tool to examine specific verbs and their conjugations

## 🚀 Quick Start

### Run All Tests
```bash
cd backend
python run_database_tests.py
```

This will run both integrity and completeness checks and provide a comprehensive summary report.

### Run Individual Tests

#### Database Integrity Check
```bash
python test_database_integrity.py
```

#### Conjugation Completeness Check
```bash
python test_conjugation_completeness.py
```

#### Interactive Verb Checker
```bash
python check_specific_verbs.py
```

## 📊 What the Tests Check

### Database Integrity Check (`test_database_integrity.py`)

- **Verb Coverage**: Ensures all verbs from `extracted_verbs.json` are in the database
- **Conjugation Coverage**: Verifies all conjugations from the JSON file are stored
- **Data Quality**: Checks for:
  - Verbs without conjugations
  - Orphaned conjugations (conjugations without verbs)
  - Duplicate conjugations
- **Statistics**: Provides distributions of verb groups, tenses, moods, and voices

### Conjugation Completeness Check (`test_conjugation_completeness.py`)

- **Pattern Completeness**: Checks if verbs have expected conjugation patterns:
  - Present indicative active (6 forms)
  - Present indicative passive (6 forms)
  - Aorist indicative active (6 forms)
  - Aorist indicative passive (6 forms)
  - Imperfect indicative active (6 forms)
  - Future indicative active (6 forms)
  - Present subjunctive active (6 forms)
  - Present imperative active (4 forms)
- **Person/Number Combinations**: Verifies correct person and number combinations
- **Form Validation**: Checks for empty, invalid, or suspicious conjugation forms
- **Greek Grammar Rules**: Validates against expected Greek conjugation patterns

### Verb Checker (`check_specific_verbs.py`)

Interactive tool that allows you to:
- Check specific verbs and their conjugations in detail
- List verbs with the most conjugations
- Search for verbs by infinitive or English meaning
- View detailed conjugation breakdowns by tense/mood/voice

## 📈 Understanding the Results

### Success Indicators
- ✅ **All tests passed**: Database integrity is excellent
- ⚠️ **Some tests passed**: Minor issues to address
- ❌ **All tests failed**: Significant database issues

### Key Metrics
- **Verb Coverage**: Percentage of JSON verbs in database
- **Conjugation Coverage**: Percentage of JSON conjugations in database
- **Completeness Score**: How complete each verb's conjugations are
- **Data Quality**: Number of orphaned, duplicate, or missing relationships

### Common Issues and Solutions

#### Missing Verbs
**Problem**: Verbs from `extracted_verbs.json` not in database
**Solution**: Re-run the import process or check the import script

#### Missing Conjugations
**Problem**: Conjugations from JSON not stored in database
**Solution**: Check the conjugation import logic in `seed_db.py`

#### Incomplete Conjugations
**Problem**: Verbs missing expected conjugation patterns
**Solution**: Review the conjugation data in `extracted_verbs.json`

#### Data Quality Issues
**Problem**: Orphaned or duplicate records
**Solution**: Clean the database and re-import

## 🔧 Customization

### Adding New Conjugation Patterns

To add new conjugation patterns to check, modify `test_conjugation_completeness.py`:

```python
self.expected_conjugation_patterns = {
    # ... existing patterns ...
    'new_pattern': {
        'tense': 'new_tense',
        'mood': 'new_mood',
        'voice': 'new_voice',
        'expected_forms': 6,
        'persons': ['1st', '2nd', '3rd'],
        'numbers': ['singular', 'plural']
    }
}
```

### Custom Validation Rules

Add custom validation rules in `validate_conjugation_forms()`:

```python
def validate_conjugation_forms(self, verb_infinitive: str, verb_data: Dict) -> List[str]:
    # ... existing validation ...
    
    # Add custom rules
    for conjugation in db_conjugations:
        if your_custom_rule(conjugation):
            issues.append(f'Custom issue: {conjugation.form}')
    
    return issues
```

## 📝 Example Usage

### Check a Specific Verb
```bash
python check_specific_verbs.py
# Choose option 1
# Enter: γράφω
```

### Run Tests and Get Report
```bash
python run_database_tests.py
```

### Check for Missing Data
```bash
python test_database_integrity.py
# Look for "MISSING VERBS" and "MISSING CONJUGATIONS" sections
```

## 🐛 Troubleshooting

### Common Errors

#### Import Errors
```
ModuleNotFoundError: No module named 'app'
```
**Solution**: Make sure you're running from the `backend` directory

#### Database Connection Errors
```
sqlite3.OperationalError: no such table
```
**Solution**: Run the database setup first:
```bash
python seed_db.py
```

#### File Not Found
```
FileNotFoundError: extracted_verbs.json not found
```
**Solution**: Make sure `extracted_verbs.json` exists in the project root

### Performance Tips

- For large datasets, the tests may take several minutes
- Use `check_specific_verbs.py` for quick checks of individual verbs
- The integrity check loads the entire JSON file into memory

## 📊 Expected Results

### Good Database Health
- Verb coverage: >95%
- Conjugation coverage: >90%
- No data quality issues
- Complete conjugation patterns for common verbs

### Typical Issues
- Some verbs may have incomplete conjugations (normal for rare verbs)
- Missing passive voice conjugations (common for intransitive verbs)
- Irregular verbs may have fewer standard patterns

## 🤝 Contributing

When adding new verbs or conjugations:

1. Run the tests before and after changes
2. Ensure new verbs have complete conjugation patterns
3. Update the expected patterns if adding new grammatical forms
4. Document any new validation rules

## 📞 Support

If you encounter issues:

1. Check the troubleshooting section above
2. Run individual tests to isolate the problem
3. Use the verb checker to examine specific cases
4. Review the database schema in `app/models/__init__.py` 