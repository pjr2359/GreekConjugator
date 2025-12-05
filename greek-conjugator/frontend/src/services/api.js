import axios from 'axios';

// Configure axios defaults
const API_BASE_URL = process.env.NODE_ENV === 'production'
  ? 'https://yourusername.pythonanywhere.com/api'
  : 'http://localhost:5000/api'; // Local Flask backend

const api = axios.create({
  baseURL: API_BASE_URL,
  withCredentials: true, // Important for session-based auth
  headers: {
    'Content-Type': 'application/json',
  },
});

// Auth service
export const authService = {
  async register(email, username, password) {
    try {
      const response = await api.post('/auth/register', {
        email,
        username,
        password
      });
      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.error || 'Registration failed');
    }
  },

  async login(email, password) {
    try {
      const response = await api.post('/auth/login', {
        email,
        password
      });
      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.error || 'Login failed');
    }
  },

  async logout() {
    try {
      const response = await api.post('/auth/logout');
      return response.data;
    } catch (error) {
      throw new Error('Logout failed');
    }
  },

  async checkAuth() {
    try {
      const response = await api.get('/auth/check');
      return response.data;
    } catch (error) {
      return { authenticated: false };
    }
  }
};

// Verbs service
export const verbsService = {
  async getVerbs(page = 1, perPage = 20, filters = {}) {
    try {
      const params = new URLSearchParams({
        page: page.toString(),
        per_page: perPage.toString(),
        ...filters
      });
      const response = await api.get(`/verbs?${params}`);
      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.error || 'Failed to fetch verbs');
    }
  },

  async getVerb(verbId) {
    try {
      const response = await api.get(`/verbs/${verbId}`);
      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.error || 'Failed to fetch verb');
    }
  },

  async getConjugations(verbId) {
    try {
      const response = await api.get(`/verbs/${verbId}/conjugations`);
      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.error || 'Failed to fetch conjugations');
    }
  },

  async startPracticeSession(sessionType = 'graded', difficulty = 3, verbCount = 20) {
    try {
      const response = await api.post('/verbs/practice/session', {
        session_type: sessionType,
        difficulty,
        verb_count: verbCount
      });
      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.error || 'Failed to start practice session');
    }
  },

  async submitAnswer(sessionId, conjugationId, answer, isCorrect) {
    try {
      const response = await api.post('/verbs/practice/answer', {
        session_id: sessionId,
        conjugation_id: conjugationId,
        answer,
        is_correct: isCorrect
      });
      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.error || 'Failed to submit answer');
    }
  },

  async getReviewCards() {
    try {
      const response = await api.get('/verbs/practice/review');
      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.error || 'Failed to fetch review cards');
    }
  },

  async getUserStats() {
    try {
      const response = await api.get('/verbs/stats');
      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.error || 'Failed to fetch statistics');
    }
  },

  async generatePracticeQuestion(sessionId, verbId, questionType = 'conjugation') {
    try {
      const response = await api.post('/verbs/practice/question', {
        session_id: sessionId,
        verb_id: verbId,
        question_type: questionType
      });
      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.error || 'Failed to generate practice question');
    }
  }
};

// Text validation service
// Vocabulary service
export const vocabularyService = {
  async getWords(page = 1, perPage = 20, filters = {}) {
    try {
      const params = new URLSearchParams({
        page: page.toString(),
        per_page: perPage.toString(),
        ...filters
      });
      const response = await api.get(`/vocabulary/words?${params}`);
      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.error || 'Failed to fetch words');
    }
  },

  async getStats() {
    try {
      const response = await api.get('/vocabulary/stats');
      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.error || 'Failed to fetch vocabulary stats');
    }
  },

  async startPractice(options = {}) {
    try {
      const response = await api.post('/vocabulary/practice/start', options);
      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.error || 'Failed to start vocabulary practice');
    }
  },

  async startSmartPractice(options = {}) {
    try {
      const response = await api.post('/vocabulary/practice/smart', options);
      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.error || 'Failed to start smart practice');
    }
  },

  async getQuestion(wordId, direction = 'greek_to_english', questionType = 'multiple_choice') {
    try {
      const response = await api.post('/vocabulary/practice/question', {
        word_id: wordId,
        direction,
        question_type: questionType
      });
      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.error || 'Failed to get question');
    }
  },

  async submitAnswer(wordId, answer, correctAnswer, direction) {
    try {
      const response = await api.post('/vocabulary/practice/answer', {
        word_id: wordId,
        answer,
        correct_answer: correctAnswer,
        direction
      });
      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.error || 'Failed to submit answer');
    }
  },

  async getCategories() {
    try {
      const response = await api.get('/vocabulary/categories');
      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.error || 'Failed to fetch categories');
    }
  },

  async getWord(wordId) {
    try {
      const response = await api.get(`/vocabulary/word/${wordId}`);
      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.error || 'Failed to fetch word');
    }
  }
};

// Text validation service
export const textValidationService = {
  async validate(text) {
    try {
      const response = await api.post('/text/validate', { text });
      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.error || 'Validation failed');
    }
  },

  async compare(text1, text2, strict = false) {
    try {
      const response = await api.post('/text/compare', {
        text1,
        text2,
        strict
      });
      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.error || 'Comparison failed');
    }
  },

  async transliterate(text, direction = 'to_greek') {
    try {
      const response = await api.post('/text/transliterate', {
        text,
        direction
      });
      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.error || 'Transliteration failed');
    }
  },

  async normalize(text) {
    try {
      const response = await api.post('/text/normalize', { text });
      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.error || 'Normalization failed');
    }
  },

  async checkAnswer(userAnswer, correctAnswer, tolerance = 'lenient') {
    try {
      const response = await api.post('/text/check-answer', {
        user_answer: userAnswer,
        correct_answer: correctAnswer,
        tolerance
      });
      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.error || 'Answer checking failed');
    }
  },

  async getKeyboardMapping() {
    try {
      const response = await api.get('/text/keyboard-mapping');
      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.error || 'Failed to get keyboard mapping');
    }
  }
};

export default api;