import React, { useState, useEffect } from 'react';
import { verbsService } from '../services/api';

const HomeScreen = ({ onStartPractice, onStartVocabulary, user }) => {
  // Practice mode state
  const [selectedMode, setSelectedMode] = useState('verb');
  const [stats, setStats] = useState(null);
  const [showGrammarOptions, setShowGrammarOptions] = useState(false);

  // Verb specific options
  const [verbSettings, setVerbSettings] = useState({
    tense: 'all',
    type: 'all',
    group: 'all'
  });

  // Noun specific options
  const [nounSettings, setNounSettings] = useState({
    case: 'all',
    number: 'all',
    gender: 'all'
  });

  // Load user stats on component mount
  useEffect(() => {
    const loadStats = async () => {
      try {
        const userStats = await verbsService.getUserStats();
        setStats(userStats);
      } catch (error) {
        console.error('Failed to load stats:', error);
      }
    };

    if (user) {
      loadStats();
    }
  }, [user]);

  const handleVerbSettingChange = (setting, value) => {
    setVerbSettings(prev => ({
      ...prev,
      [setting]: value
    }));
  };

  const handleNounSettingChange = (setting, value) => {
    setNounSettings(prev => ({
      ...prev,
      [setting]: value
    }));
  };

  // Start practice with current settings
  const startPractice = (useBackend = false) => {
    const settings = {
      mode: selectedMode,
      useBackend,
      ...(selectedMode === 'verb' ? verbSettings : {}),
      ...(selectedMode === 'noun' ? nounSettings : {})
    };

    onStartPractice(settings);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-blue-900 to-slate-900 p-4">
      <div className="max-w-2xl mx-auto pt-4">
        {/* Header */}
        <header className="text-center mb-8">
          <div className="text-5xl mb-3">🏛️</div>
          <h1 className="text-3xl font-bold text-white mb-1">
            Ελληνικά
          </h1>
          <p className="text-blue-300">Greek Language Learning</p>
        </header>

        {/* Quick Stats */}
        {stats && (
          <div className="grid grid-cols-4 gap-3 mb-6">
            <div className="bg-slate-800/50 rounded-xl p-3 text-center border border-slate-700">
              <div className="text-xl font-bold text-blue-400">{stats.total_verbs_practiced}</div>
              <div className="text-xs text-slate-500">Verbs</div>
            </div>
            <div className="bg-slate-800/50 rounded-xl p-3 text-center border border-slate-700">
              <div className="text-xl font-bold text-emerald-400">{stats.accuracy_rate}%</div>
              <div className="text-xs text-slate-500">Accuracy</div>
            </div>
            <div className="bg-slate-800/50 rounded-xl p-3 text-center border border-slate-700">
              <div className="text-xl font-bold text-amber-400">{stats.due_cards}</div>
              <div className="text-xs text-slate-500">Due</div>
            </div>
            <div className="bg-slate-800/50 rounded-xl p-3 text-center border border-slate-700">
              <div className="text-xl font-bold text-purple-400">{stats.total_attempts}</div>
              <div className="text-xs text-slate-500">Total</div>
            </div>
          </div>
        )}

        {/* Main Practice Cards */}
        <div className="space-y-4 mb-6">
          {/* Vocabulary Card - Primary */}
          <div className="bg-slate-800 rounded-2xl border border-slate-700 overflow-hidden">
            <div className="bg-gradient-to-r from-blue-600 to-cyan-600 p-6">
              <div className="flex items-center justify-between">
                <div>
                  <h2 className="text-2xl font-bold text-white flex items-center gap-2">
                    📚 Λεξιλόγιο
                  </h2>
                  <p className="text-blue-100 mt-1">Vocabulary Flashcards</p>
                </div>
                <div className="text-right">
                  <div className="text-3xl font-bold text-white">2,500+</div>
                  <div className="text-blue-200 text-sm">words</div>
                </div>
              </div>
            </div>
            <div className="p-4">
              <div className="grid grid-cols-3 gap-3 mb-4">
                <div className="bg-slate-700/50 rounded-lg p-3 text-center">
                  <div className="text-lg font-bold text-white">🧠</div>
                  <div className="text-xs text-slate-400">Smart SRS</div>
                </div>
                <div className="bg-slate-700/50 rounded-lg p-3 text-center">
                  <div className="text-lg font-bold text-white">🎯</div>
                  <div className="text-xs text-slate-400">Daily Goals</div>
                </div>
                <div className="bg-slate-700/50 rounded-lg p-3 text-center">
                  <div className="text-lg font-bold text-white">📈</div>
                  <div className="text-xs text-slate-400">Progress</div>
                </div>
              </div>
              <button
                onClick={onStartVocabulary}
                className="w-full py-4 bg-gradient-to-r from-blue-500 to-cyan-500 text-white font-bold rounded-xl 
                  hover:from-blue-600 hover:to-cyan-600 transition-all text-lg"
              >
                Study Vocabulary
              </button>
            </div>
          </div>

          {/* Conjugation Practice Card */}
          <div className="bg-slate-800 rounded-2xl border border-slate-700 overflow-hidden">
            <div className="bg-gradient-to-r from-purple-600 to-pink-600 p-6">
              <div className="flex items-center justify-between">
                <div>
                  <h2 className="text-2xl font-bold text-white flex items-center gap-2">
                    📝 Κλίσεις
                  </h2>
                  <p className="text-purple-100 mt-1">Conjugation Practice</p>
                </div>
                <div className="text-right">
                  <div className="text-3xl font-bold text-white">87</div>
                  <div className="text-purple-200 text-sm">verbs</div>
                </div>
              </div>
            </div>
            <div className="p-4">
              <button
                onClick={() => startPractice(true)}
                className="w-full py-4 bg-gradient-to-r from-purple-500 to-pink-500 text-white font-bold rounded-xl 
                  hover:from-purple-600 hover:to-pink-600 transition-all text-lg"
              >
                Practice Conjugations
              </button>
            </div>
          </div>
        </div>

        {/* Grammar Practice Toggle */}
        <button
          onClick={() => setShowGrammarOptions(!showGrammarOptions)}
          className="w-full py-3 text-slate-400 hover:text-slate-300 transition-colors flex items-center justify-center gap-2 mb-4"
        >
          <span>{showGrammarOptions ? '▲' : '▼'}</span>
          {showGrammarOptions ? 'Hide' : 'Show'} More Grammar Practice
        </button>

        {/* Grammar Options Panel */}
        {showGrammarOptions && (
          <div className="bg-slate-800/50 rounded-xl border border-slate-700 p-6 space-y-4">
            <h3 className="text-white font-semibold mb-4">Grammar Practice</h3>
            
            {/* Mode selection */}
            <div className="grid grid-cols-2 gap-3 mb-4">
              <button
                onClick={() => setSelectedMode('verb')}
                className={`p-4 rounded-xl border transition-all ${
                  selectedMode === 'verb' 
                    ? 'border-blue-500 bg-blue-500/20 text-white' 
                    : 'border-slate-600 text-slate-400 hover:border-slate-500'
                }`}
              >
                <div className="text-center">
                  <span className="text-2xl mb-2 block">🔤</span>
                  <span className="font-medium">Verbs</span>
                  <span className="text-xs block text-slate-500">Ρήματα</span>
                </div>
              </button>
              <button
                onClick={() => setSelectedMode('noun')}
                className={`p-4 rounded-xl border transition-all ${
                  selectedMode === 'noun' 
                    ? 'border-blue-500 bg-blue-500/20 text-white' 
                    : 'border-slate-600 text-slate-400 hover:border-slate-500'
                }`}
              >
                <div className="text-center">
                  <span className="text-2xl mb-2 block">📝</span>
                  <span className="font-medium">Nouns</span>
                  <span className="text-xs block text-slate-500">Ουσιαστικά</span>
                </div>
              </button>
              <button
                onClick={() => setSelectedMode('adjective')}
                className={`p-4 rounded-xl border transition-all ${
                  selectedMode === 'adjective' 
                    ? 'border-blue-500 bg-blue-500/20 text-white' 
                    : 'border-slate-600 text-slate-400 hover:border-slate-500'
                }`}
              >
                <div className="text-center">
                  <span className="text-2xl mb-2 block">🏷️</span>
                  <span className="font-medium">Adjectives</span>
                  <span className="text-xs block text-slate-500">Επίθετα</span>
                </div>
              </button>
              <button
                onClick={() => setSelectedMode('article')}
                className={`p-4 rounded-xl border transition-all ${
                  selectedMode === 'article' 
                    ? 'border-blue-500 bg-blue-500/20 text-white' 
                    : 'border-slate-600 text-slate-400 hover:border-slate-500'
                }`}
              >
                <div className="text-center">
                  <span className="text-2xl mb-2 block">🔍</span>
                  <span className="font-medium">Articles</span>
                  <span className="text-xs block text-slate-500">Άρθρα</span>
                </div>
              </button>
            </div>

            {/* Verb options */}
            {selectedMode === 'verb' && (
              <div className="space-y-4">
                <div>
                  <label className="block text-sm text-slate-400 mb-2">Tense (Χρόνος)</label>
                  <select
                    value={verbSettings.tense}
                    onChange={(e) => handleVerbSettingChange('tense', e.target.value)}
                    className="w-full p-3 bg-slate-700 border border-slate-600 rounded-xl text-white"
                  >
                    <option value="all">All Tenses</option>
                    <option value="ενεστώτας">Present (Ενεστώτας)</option>
                    <option value="αόριστος">Aorist (Αόριστος)</option>
                    <option value="παρατατικός">Imperfect (Παρατατικός)</option>
                    <option value="μέλλοντας">Future (Μέλλοντας)</option>
                  </select>
                </div>

                <div>
                  <label className="block text-sm text-slate-400 mb-2">Voice (Φωνή)</label>
                  <select
                    value={verbSettings.type}
                    onChange={(e) => handleVerbSettingChange('type', e.target.value)}
                    className="w-full p-3 bg-slate-700 border border-slate-600 rounded-xl text-white"
                  >
                    <option value="all">All Voices</option>
                    <option value="ενεργητική φωνή">Active</option>
                    <option value="παθητική φωνή">Passive</option>
                  </select>
                </div>

                <button
                  onClick={() => startPractice(false)}
                  className="w-full py-3 bg-slate-700 text-white font-medium rounded-xl hover:bg-slate-600 transition-colors"
                >
                  Start Practice
                </button>
              </div>
            )}

            {/* Noun options */}
            {selectedMode === 'noun' && (
              <div className="space-y-4">
                <div>
                  <label className="block text-sm text-slate-400 mb-2">Case (Πτώση)</label>
                  <select
                    value={nounSettings.case}
                    onChange={(e) => handleNounSettingChange('case', e.target.value)}
                    className="w-full p-3 bg-slate-700 border border-slate-600 rounded-xl text-white"
                  >
                    <option value="all">All Cases</option>
                    <option value="ονομαστική">Nominative</option>
                    <option value="γενική">Genitive</option>
                    <option value="αιτιατική">Accusative</option>
                    <option value="κλητική">Vocative</option>
                  </select>
                </div>

                <div>
                  <label className="block text-sm text-slate-400 mb-2">Gender (Γένος)</label>
                  <select
                    value={nounSettings.gender}
                    onChange={(e) => handleNounSettingChange('gender', e.target.value)}
                    className="w-full p-3 bg-slate-700 border border-slate-600 rounded-xl text-white"
                  >
                    <option value="all">All Genders</option>
                    <option value="αρσενικό">Masculine</option>
                    <option value="θηλυκό">Feminine</option>
                    <option value="ουδέτερο">Neuter</option>
                  </select>
                </div>

                <button
                  onClick={() => startPractice(false)}
                  className="w-full py-3 bg-slate-700 text-white font-medium rounded-xl hover:bg-slate-600 transition-colors"
                >
                  Start Practice
                </button>
              </div>
            )}

            {/* Adjective options */}
            {selectedMode === 'adjective' && (
              <div className="space-y-4">
                <p className="text-slate-400 text-sm">
                  Practice adjective agreement with nouns in gender, number, and case.
                </p>
                <button
                  onClick={() => startPractice(false)}
                  className="w-full py-3 bg-slate-700 text-white font-medium rounded-xl hover:bg-slate-600 transition-colors"
                >
                  Start Practice
                </button>
              </div>
            )}

            {/* Article options */}
            {selectedMode === 'article' && (
              <div className="space-y-4">
                <p className="text-slate-400 text-sm">
                  Practice using definite and indefinite articles correctly.
                </p>
                <button
                  onClick={() => startPractice(false)}
                  className="w-full py-3 bg-slate-700 text-white font-medium rounded-xl hover:bg-slate-600 transition-colors"
                >
                  Start Practice
                </button>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
};

export default HomeScreen;