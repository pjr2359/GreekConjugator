# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Greek Conjugator is a full-stack web application for learning Greek verb conjugations. The app features spaced repetition learning, user authentication, and subscription-based access to verb sets.

## Architecture

### Monorepo Structure
```
greek-conjugator/
├── backend/          # Flask API server
├── frontend/         # React SPA
├── setup_dev.sh      # Development setup script  
└── start_dev.sh      # Development server launcher
```

### Backend (Flask)
- **Framework**: Flask with SQLAlchemy ORM
- **Database**: SQLite for development (models in `backend/app/models/__init__.py`)
- **Authentication**: Session-based auth with Flask-Session
- **API Routes**: RESTful endpoints in `backend/app/routes/`
  - `auth.py`: User registration, login, logout
  - `verbs.py`: Verb management, practice sessions, spaced repetition
- **Main Models**: User, Verb, Conjugation, UserProgress, PracticeSession
- **Spaced Repetition**: SM-2 algorithm implementation in `verbs.py:199`

### Frontend (React)
- **Framework**: React 18 with Create React App
- **Styling**: Tailwind CSS (PostCSS build pipeline)
- **State Management**: React hooks (useState, useEffect)
- **API Client**: Axios with session-based authentication
- **Main Components**:
  - `App.jsx`: Main application router and auth state
  - `AuthComponent.jsx`: User authentication
  - `PracticeSession.jsx`: Backend-powered practice sessions
  - `GreekConjugationApp.jsx`: Legacy practice component
  - `GreekKeyboard.jsx`: Greek text input helper

### Key Features
- **Subscription Tiers**: Free users limited to 50 most frequent verbs
- **Spaced Repetition**: Adaptive learning intervals based on user performance
- **Progress Tracking**: User statistics, streaks, and review scheduling
- **Multiple Practice Modes**: Verbs, nouns, adjectives, articles

## Common Development Commands

### Initial Setup
```bash
# Run from project root
cd greek-conjugator
./setup_dev.sh
```

### Development Server
```bash
# Run from project root  
cd greek-conjugator
./start_dev.sh
```
- Frontend: http://localhost:3000
- Backend API: http://localhost:5000

### Frontend Commands
```bash
cd frontend
npm run build:css          # Build Tailwind CSS
npm run watch:css          # Watch Tailwind CSS changes
npm start                  # Start React dev server
npm run build             # Production build
```

### Backend Commands
```bash
cd backend
source venv/bin/activate   # Activate virtual environment
python3 run_backend.py     # Start Flask server
python3 seed_db.py         # Seed database with sample data
```

## Database Schema

### Core Models
- **User**: Authentication and subscription management
- **Verb**: Greek verbs with frequency, difficulty, and grouping
- **Conjugation**: Verb forms with tense, mood, voice, person, number
- **UserProgress**: Spaced repetition state per user/conjugation
- **PracticeSession**: Session tracking for analytics

### Important Relationships
- User has many UserProgress records
- Verb has many Conjugations
- UserProgress tracks individual conjugation mastery

## Development Notes

### API Authentication
- Session-based authentication with Flask-Session
- `@login_required` decorator for protected routes
- CORS enabled for frontend-backend communication

### Database Considerations
- SQLite optimized schema (TEXT instead of JSON, FLOAT instead of NUMERIC)
- Automatic table creation on app startup
- Seeding script provides sample Greek verbs

### Frontend-Backend Integration
- Axios configured with `withCredentials: true` for sessions
- API base URL switches based on NODE_ENV
- Error handling with user-friendly messages

### CSS Build Process
- Tailwind CSS compiled via PostCSS
- Watch mode for development
- Custom configuration in `tailwind.config.js`

## File Organization

### Backend Structure
```
backend/
├── app/
│   ├── __init__.py       # Flask app factory
│   ├── models/           # SQLAlchemy models
│   ├── routes/           # API endpoints
│   │   ├── auth.py       # Authentication routes
│   │   ├── verbs.py      # Verb practice routes
│   │   └── text_validation.py  # Greek text processing API
│   └── services/         # Business logic services
│       └── greek_text.py # Greek text processing utilities
├── db/
│   └── schema.sql        # Database schema (empty)
├── requirements.txt      # Python dependencies
├── run_backend.py        # Development server
├── seed_db.py           # Database seeding
├── simple_test.py       # Basic Greek text processing test
└── test_greek_processing.py  # Comprehensive tests
```

### Frontend Structure
```
frontend/
├── src/
│   ├── components/       # React components
│   ├── services/         # API client
│   └── styles/          # Tailwind CSS
├── public/              # Static assets
└── package.json         # Node.js dependencies
```

## Testing and Quality

No testing framework is currently configured. Tests should be added using:
- Backend: pytest with Flask-Testing
- Frontend: React Testing Library (included in CRA)

## Greek Text Processing System

### New Features Added
- **Unicode Normalization**: Handles Greek text in standard Unicode forms
- **Accent-Insensitive Comparison**: Matches Greek words regardless of diacritical marks
- **Real-time Transliteration**: Converts Latin input to Greek automatically
- **Enhanced Virtual Keyboard**: Multiple layouts (basic, accented, uppercase)
- **Text Validation API**: Server-side validation with detailed feedback
- **Mobile-Responsive Design**: Touch-friendly virtual keyboard

### API Endpoints
- `POST /api/text/validate` - Validate Greek text input
- `POST /api/text/compare` - Compare two Greek texts
- `POST /api/text/transliterate` - Convert between Latin and Greek
- `POST /api/text/normalize` - Normalize Greek Unicode text
- `POST /api/text/check-answer` - Advanced answer validation
- `GET /api/text/keyboard-mapping` - Get transliteration mappings

### Key Components
- **GreekTextProcessor** (`backend/app/services/greek_text.py`): Core text processing
- **Enhanced GreekKeyboard** (`frontend/src/components/GreekKeyboard.jsx`): Virtual keyboard with transliteration
- **Text Validation Service** (`frontend/src/services/api.js`): Frontend API integration

### Usage Examples
```python
# Backend usage
from app.services.greek_text import compare_greek_texts, latin_to_greek
result = compare_greek_texts("γράφω", "γραφω")  # True (accent-insensitive)
greek = latin_to_greek("grapho")  # "γραφω"
```

```javascript
// Frontend usage
import { textValidationService } from '../services/api';
const result = await textValidationService.checkAnswer(userInput, correctAnswer);
```

### Testing
- Run `python3 simple_test.py` to test core functionality
- Enhanced practice sessions with real-time validation
- Fallback to client-side processing if API fails

## Performance Considerations

- Database queries use pagination for large verb sets
- Spaced repetition algorithm optimizes review scheduling
- Session-based auth minimizes API calls
- Frontend components use React hooks for efficient re-renders
- Greek text processing includes client-side fallbacks for reliability
- Debounced validation reduces API calls during typing