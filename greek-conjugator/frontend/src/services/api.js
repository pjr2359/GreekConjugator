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

  async startPracticeSession(sessionType = 'graded', difficulty = 1, verbCount = 10) {
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
  }
};

export default api;