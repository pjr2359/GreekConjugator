import React, { useState } from 'react';
import { authService } from '../services/api';

const AuthComponent = ({ user, setUser }) => {
  const [isLogin, setIsLogin] = useState(true);
  const [formData, setFormData] = useState({
    email: '',
    username: '',
    password: ''
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    const email = formData.email.trim();
    const password = formData.password.trim();
    const username = formData.username.trim();

    if (!email || !password) {
      setError('Email and password are required.');
      setLoading(false);
      return;
    }

    try {
      if (isLogin) {
        const response = await authService.login(email, password);
        setUser(response.user);
      } else {
        await authService.register(email, username, password);
        // Auto-login after registration
        const loginResponse = await authService.login(email, password);
        setUser(loginResponse.user);
      }
    } catch (error) {
      setError(error.message);
    } finally {
      setLoading(false);
    }
  };

  const handleLogout = async () => {
    try {
      await authService.logout();
      setUser(null);
    } catch (error) {
      console.error('Logout failed:', error);
    }
  };

  // Logged in header bar
  if (user) {
    return (
      <div className="flex items-center justify-between p-4 bg-slate-800 border-b border-slate-700">
        <div className="flex items-center space-x-4">
          <div className="text-lg font-semibold text-white">
            Γεια σου, {user.username || user.email}!
          </div>
        </div>
        <button
          onClick={handleLogout}
          className="px-4 py-2 text-sm text-slate-400 hover:text-white hover:bg-slate-700 rounded-lg transition-colors"
        >
          Logout
        </button>
      </div>
    );
  }

  // Login/Register screen
  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-blue-900 to-slate-900 flex items-center justify-center p-4">
      <div className="max-w-md w-full">
        {/* Logo/Title */}
        <div className="text-center mb-8">
          <div className="text-6xl mb-4">🏛️</div>
          <h1 className="text-4xl font-bold text-white mb-2">
            Ελληνικά
          </h1>
          <p className="text-blue-300 text-lg">
            Greek Language Learning
          </p>
        </div>

        {/* Auth Card */}
        <div className="bg-slate-800 rounded-2xl border border-slate-700 shadow-2xl overflow-hidden">
          {/* Tab Switcher */}
          <div className="flex">
            <button
              onClick={() => setIsLogin(true)}
              type="button"
              className={`flex-1 py-4 text-center font-medium transition-colors ${isLogin
                  ? 'bg-gradient-to-r from-blue-500 to-cyan-500 text-white'
                  : 'bg-slate-700 text-slate-400 hover:text-white'
                }`}
            >
              Login
            </button>
            <button
              onClick={() => setIsLogin(false)}
              type="button"
              className={`flex-1 py-4 text-center font-medium transition-colors ${!isLogin
                  ? 'bg-gradient-to-r from-blue-500 to-cyan-500 text-white'
                  : 'bg-slate-700 text-slate-400 hover:text-white'
                }`}
            >
              Register
            </button>
          </div>

          <form onSubmit={handleSubmit} className="p-6 space-y-4">
            <div>
              <label className="block text-sm font-medium text-slate-400 mb-2">
                Email
              </label>
              <input
                type="email"
                required
                value={formData.email}
                onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                className="w-full px-4 py-3 bg-slate-700 border border-slate-600 rounded-xl text-white placeholder-slate-500 focus:outline-none focus:border-blue-500 focus:ring-1 focus:ring-blue-500"
                placeholder="your@email.com"
              />
            </div>

            {!isLogin && (
              <div>
                <label className="block text-sm font-medium text-slate-400 mb-2">
                  Username (optional)
                </label>
                <input
                  type="text"
                  value={formData.username}
                  onChange={(e) => setFormData({ ...formData, username: e.target.value })}
                  className="w-full px-4 py-3 bg-slate-700 border border-slate-600 rounded-xl text-white placeholder-slate-500 focus:outline-none focus:border-blue-500 focus:ring-1 focus:ring-blue-500"
                  placeholder="Your username"
                />
              </div>
            )}

            <div>
              <label className="block text-sm font-medium text-slate-400 mb-2">
                Password
              </label>
              <input
                type="password"
                required
                value={formData.password}
                onChange={(e) => setFormData({ ...formData, password: e.target.value })}
                className="w-full px-4 py-3 bg-slate-700 border border-slate-600 rounded-xl text-white placeholder-slate-500 focus:outline-none focus:border-blue-500 focus:ring-1 focus:ring-blue-500"
                placeholder="Your password"
              />
            </div>

            {error && (
              <div className="bg-red-500/20 border border-red-500/50 text-red-400 px-4 py-3 rounded-xl">
                {error}
              </div>
            )}

            <button
              type="submit"
              disabled={loading}
              className="w-full bg-gradient-to-r from-blue-500 to-cyan-500 text-white py-4 px-4 rounded-xl 
                hover:from-blue-600 hover:to-cyan-600 disabled:opacity-50 disabled:cursor-not-allowed 
                transition-all font-bold text-lg"
            >
              {loading ? (
                <span className="flex items-center justify-center gap-2">
                  <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white"></div>
                  Please wait...
                </span>
              ) : (
                isLogin ? 'Login' : 'Create Account'
              )}
            </button>
          </form>
        </div>

        {/* Features */}
        <div className="mt-8 grid grid-cols-3 gap-4 text-center">
          <div className="bg-slate-800/50 rounded-xl p-4 border border-slate-700">
            <div className="text-2xl mb-1">📚</div>
            <div className="text-white font-medium">2,500+</div>
            <div className="text-slate-500 text-xs">Words</div>
          </div>
          <div className="bg-slate-800/50 rounded-xl p-4 border border-slate-700">
            <div className="text-2xl mb-1">🔤</div>
            <div className="text-white font-medium">600+</div>
            <div className="text-slate-500 text-xs">Verbs</div>
          </div>
          <div className="bg-slate-800/50 rounded-xl p-4 border border-slate-700">
            <div className="text-2xl mb-1">🧠</div>
            <div className="text-white font-medium">SRS</div>
            <div className="text-slate-500 text-xs">Smart Learning</div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default AuthComponent;