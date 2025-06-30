import React, { useState, useEffect } from 'react';
import { verbsService } from '../services/api';

const HomeScreen = ({ onStartPractice, user }) => {
  // Practice mode state
  const [selectedMode, setSelectedMode] = useState('verb');
  const [stats, setStats] = useState(null);

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
    <div className="flex flex-col items-center justify-center p-4 bg-gray-50 min-h-screen">
      <div className="w-full max-w-4xl">
        <header className="text-center mb-6">
          <h1 className="text-3xl font-bold text-blue-600 mb-2">
            Greek Grammar Practice
            <span className="text-gray-500 text-xl block mt-1">(Εξάσκηση Ελληνικής Γραμματικής)</span>
          </h1>
          <p className="text-gray-600">Master Greek with spaced repetition and smart practice</p>
        </header>

        {/* User Stats Dashboard */}
        {stats && (
          <div className="bg-white rounded-lg shadow-lg p-6 mb-6">
            <h2 className="text-xl font-bold text-gray-800 mb-4">📊 Your Progress</h2>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <div className="text-center p-4 bg-blue-50 rounded-lg">
                <div className="text-2xl font-bold text-blue-600">{stats.total_verbs_practiced}</div>
                <div className="text-sm text-gray-600">Verbs Practiced</div>
              </div>
              <div className="text-center p-4 bg-green-50 rounded-lg">
                <div className="text-2xl font-bold text-green-600">{stats.accuracy_rate}%</div>
                <div className="text-sm text-gray-600">Accuracy Rate</div>
              </div>
              <div className="text-center p-4 bg-yellow-50 rounded-lg">
                <div className="text-2xl font-bold text-yellow-600">{stats.due_cards}</div>
                <div className="text-sm text-gray-600">Due for Review</div>
              </div>
              <div className="text-center p-4 bg-purple-50 rounded-lg">
                <div className="text-2xl font-bold text-purple-600">{stats.total_attempts}</div>
                <div className="text-sm text-gray-600">Total Attempts</div>
              </div>
            </div>
          </div>
        )}

        <div className="bg-white shadow-lg rounded-lg overflow-hidden border mb-6">
          <div className="bg-blue-50 border-b p-4">
            <h2 className="text-xl font-bold text-blue-700">
              What would you like to practice?
              <span className="text-gray-500 text-lg block mt-1">(Τι θα θέλατε να εξασκήσετε;)</span>
            </h2>
          </div>

          <div className="p-6">
            {/* Mode selection */}
            <div className="grid grid-cols-2 gap-4 mb-6">
              <button
                onClick={() => setSelectedMode('verb')}
                className={`p-4 rounded-lg border transition-colors ${selectedMode === 'verb' ? 'bg-blue-100 border-blue-500' : 'border-gray-200 hover:bg-gray-50'}`}
              >
                <div className="text-center">
                  <span className="text-2xl mb-2 block">🔤</span>
                  <span className="font-medium">Verbs <span className="text-sm text-gray-500">(Ρήματα)</span></span>
                </div>
              </button>
              <button
                onClick={() => setSelectedMode('noun')}
                className={`p-4 rounded-lg border transition-colors ${selectedMode === 'noun' ? 'bg-blue-100 border-blue-500' : 'border-gray-200 hover:bg-gray-50'}`}
              >
                <div className="text-center">
                  <span className="text-2xl mb-2 block">📝</span>
                  <span className="font-medium">Nouns <span className="text-sm text-gray-500">(Ουσιαστικά)</span></span>
                </div>
              </button>
              <button
                onClick={() => setSelectedMode('adjective')}
                className={`p-4 rounded-lg border transition-colors ${selectedMode === 'adjective' ? 'bg-blue-100 border-blue-500' : 'border-gray-200 hover:bg-gray-50'}`}
              >
                <div className="text-center">
                  <span className="text-2xl mb-2 block">🏷️</span>
                  <span className="font-medium">Adjectives <span className="text-sm text-gray-500">(Επίθετα)</span></span>
                </div>
              </button>
              <button
                onClick={() => setSelectedMode('article')}
                className={`p-4 rounded-lg border transition-colors ${selectedMode === 'article' ? 'bg-blue-100 border-blue-500' : 'border-gray-200 hover:bg-gray-50'}`}
              >
                <div className="text-center">
                  <span className="text-2xl mb-2 block">🔍</span>
                  <span className="font-medium">Articles <span className="text-sm text-gray-500">(Άρθρα)</span></span>
                </div>
              </button>
            </div>

            {/* Verb options with new smart practice */}
            {selectedMode === 'verb' && (
              <div className="space-y-6">
                {/* New Backend Practice Option */}
                <div className="border-2 border-blue-200 rounded-lg p-4 bg-blue-50">
                  <div className="flex items-center justify-between mb-3">
                    <h3 className="text-lg font-bold text-blue-800">🧠 Smart Practice (Recommended)</h3>
                    <span className="px-2 py-1 bg-blue-600 text-white text-xs rounded-full">NEW</span>
                  </div>
                  <p className="text-blue-700 mb-4">
                    Practice with {user?.subscription_tier === 'premium' ? '1000+' : '50'} real Greek verbs using spaced repetition algorithm.
                    Progress tracking and personalized difficulty.
                  </p>
                  <button
                    onClick={() => startPractice(true)}
                    className="w-full bg-blue-600 text-white px-4 py-3 rounded-lg hover:bg-blue-700 font-medium transition-colors"
                  >
                    🚀 Start Smart Practice
                  </button>
                </div>

                {/* Traditional Practice Options */}
                <div className="border rounded-lg p-4">
                  <h3 className="text-lg font-semibold text-gray-800 mb-4">⚙️ Traditional Practice Options</h3>
                  <div className="space-y-4">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">Tense <span className="text-gray-500">(Χρόνος)</span></label>
                      <select
                        value={verbSettings.tense}
                        onChange={(e) => handleVerbSettingChange('tense', e.target.value)}
                        className="w-full p-2 border rounded focus:ring-2 focus:ring-blue-500"
                      >
                        <option value="all">All Tenses (Όλοι οι Χρόνοι)</option>
                        <option value="ενεστώτας">Present (Ενεστώτας)</option>
                        <option value="αόριστος">Aorist (Αόριστος)</option>
                        <option value="παρατατικός">Imperfect (Παρατατικός)</option>
                        <option value="μέλλοντας">Future (Μέλλοντας)</option>
                        <option value="παρακείμενος">Perfect (Παρακείμενος)</option>
                        <option value="υπερσυντέλικος">Pluperfect (Υπερσυντέλικος)</option>
                      </select>
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">Voice <span className="text-gray-500">(Φωνή)</span></label>
                      <select
                        value={verbSettings.type}
                        onChange={(e) => handleVerbSettingChange('type', e.target.value)}
                        className="w-full p-2 border rounded focus:ring-2 focus:ring-blue-500"
                      >
                        <option value="all">All Voices (Όλες οι Φωνές)</option>
                        <option value="ενεργητική φωνή">Active (Ενεργητική φωνή)</option>
                        <option value="παθητική φωνή">Passive (Παθητική φωνή)</option>
                        <option value="μέση φωνή">Middle (Μέση φωνή)</option>
                      </select>
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">Group <span className="text-gray-500">(Ομάδα)</span></label>
                      <select
                        value={verbSettings.group}
                        onChange={(e) => handleVerbSettingChange('group', e.target.value)}
                        className="w-full p-2 border rounded focus:ring-2 focus:ring-blue-500"
                      >
                        <option value="all">All Groups (Όλες οι Ομάδες)</option>
                        <option value="A">Group A (Ομάδα Α)</option>
                        <option value="B">Group B (Ομάδα Β)</option>
                      </select>
                    </div>

                    <button
                      onClick={() => startPractice(false)}
                      className="w-full bg-gray-600 text-white px-4 py-2 rounded-lg hover:bg-gray-700 transition-colors"
                    >
                      Start Traditional Practice
                    </button>
                  </div>
                </div>
              </div>
            )}

            {/* Noun options */}
            {selectedMode === 'noun' && (
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Case <span className="text-gray-500">(Πτώση)</span></label>
                  <select
                    value={nounSettings.case}
                    onChange={(e) => handleNounSettingChange('case', e.target.value)}
                    className="w-full p-2 border rounded focus:ring-2 focus:ring-blue-500"
                  >
                    <option value="all">All Cases (Όλες οι Πτώσεις)</option>
                    <option value="ονομαστική">Nominative (Ονομαστική)</option>
                    <option value="γενική">Genitive (Γενική)</option>
                    <option value="αιτιατική">Accusative (Αιτιατική)</option>
                    <option value="κλητική">Vocative (Κλητική)</option>
                  </select>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Number <span className="text-gray-500">(Αριθμός)</span></label>
                  <select
                    value={nounSettings.number}
                    onChange={(e) => handleNounSettingChange('number', e.target.value)}
                    className="w-full p-2 border rounded focus:ring-2 focus:ring-blue-500"
                  >
                    <option value="all">All Numbers (Όλοι οι Αριθμοί)</option>
                    <option value="ενικός">Singular (Ενικός)</option>
                    <option value="πληθυντικός">Plural (Πληθυντικός)</option>
                  </select>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Gender <span className="text-gray-500">(Γένος)</span></label>
                  <select
                    value={nounSettings.gender}
                    onChange={(e) => handleNounSettingChange('gender', e.target.value)}
                    className="w-full p-2 border rounded focus:ring-2 focus:ring-blue-500"
                  >
                    <option value="all">All Genders (Όλα τα Γένη)</option>
                    <option value="αρσενικό">Masculine (Αρσενικό)</option>
                    <option value="θηλυκό">Feminine (Θηλυκό)</option>
                    <option value="ουδέτερο">Neuter (Ουδέτερο)</option>
                  </select>
                </div>

                <button
                  onClick={() => startPractice(false)}
                  className="w-full bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition-colors"
                >
                  Start Noun Practice
                </button>
              </div>
            )}

            {/* Adjective options (simplified) */}
            {selectedMode === 'adjective' && (
              <div className="space-y-4">
                <div className="p-4 bg-gray-50 rounded">
                  <p>Practice adjectives - agreement with nouns in gender, number, and case. <span className="text-gray-500">(Εξάσκηση επιθέτων - συμφωνία με ουσιαστικά σε γένος, αριθμό και πτώση.)</span></p>
                </div>
                <button
                  onClick={() => startPractice(false)}
                  className="w-full bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition-colors"
                >
                  Start Adjective Practice
                </button>
              </div>
            )}

            {/* Article options (simplified) */}
            {selectedMode === 'article' && (
              <div className="space-y-4">
                <div className="p-4 bg-gray-50 rounded">
                  <p>Practice using articles - definite and indefinite articles. <span className="text-gray-500">(Εξάσκηση στη χρήση άρθρων - οριστικά και αόριστα άρθρα.)</span></p>
                </div>
                <button
                  onClick={() => startPractice(false)}
                  className="w-full bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition-colors"
                >
                  Start Article Practice
                </button>
              </div>
            )}
          </div>
        </div>

        <div className="text-center text-sm text-gray-600">
          <p>Greek Grammar - Production Learning Platform <span className="text-gray-500">(Ελληνική Γραμματική - Πλατφόρμα Εκμάθησης)</span></p>
        </div>
      </div>
    </div>
  );
};

export default HomeScreen;