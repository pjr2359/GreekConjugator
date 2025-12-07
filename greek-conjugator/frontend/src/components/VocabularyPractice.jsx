import React, { useState, useEffect, useCallback } from 'react';
import { vocabularyService } from '../services/api';

const VocabularyPractice = ({ user, onBackToHome }) => {
  // Practice state
  const [words, setWords] = useState([]);
  const [currentIndex, setCurrentIndex] = useState(0);
  const [currentQuestion, setCurrentQuestion] = useState(null);
  const [selectedAnswer, setSelectedAnswer] = useState(null);
  const [showResult, setShowResult] = useState(false);
  const [isCorrect, setIsCorrect] = useState(false);
  const [loading, setLoading] = useState(false);
  const [sessionComplete, setSessionComplete] = useState(false);
  
  // Settings state
  const [direction, setDirection] = useState('greek_to_english');
  const [practiceType, setPracticeType] = useState('random');
  const [wordType, setWordType] = useState('');
  const [category, setCategory] = useState('');
  const [questionType, setQuestionType] = useState('multiple_choice'); // 'multiple_choice', 'type', 'flashcard'
  const [wordCount, setWordCount] = useState(10);
  const [dailyNewLimit, setDailyNewLimit] = useState(10);
  const [flashcardRevealed, setFlashcardRevealed] = useState(false);
  
  // Stats state
  const [stats, setStats] = useState(null);
  const [statsLoading, setStatsLoading] = useState(true);
  const [sessionStats, setSessionStats] = useState({ correct: 0, total: 0, streak: 0, maxStreak: 0 });
  const [categories, setCategories] = useState({ categories: {}, word_types: {} });
  
  // Setup/config view
  const [showSetup, setShowSetup] = useState(true);
  const [showCustomSettings, setShowCustomSettings] = useState(false);
  const [typedAnswer, setTypedAnswer] = useState('');

  // Load initial data
  useEffect(() => {
    loadStats();
    loadCategories();
  }, []);

  const loadStats = async () => {
    setStatsLoading(true);
    try {
      const data = await vocabularyService.getStats();
      setStats(data);
    } catch (error) {
      console.error('Failed to load stats:', error);
    } finally {
      setStatsLoading(false);
    }
  };

  const loadCategories = async () => {
    try {
      const data = await vocabularyService.getCategories();
      setCategories(data);
    } catch (error) {
      console.error('Failed to load categories:', error);
    }
  };

  // Error state for graceful error handling
  const [practiceError, setPracticeError] = useState(null);

  // Anki-style smart practice
  const startSmartPractice = async () => {
    setLoading(true);
    setPracticeError(null);
    try {
      const data = await vocabularyService.startSmartPractice({
        daily_new_limit: dailyNewLimit,
        direction
      });
      
      // Check if no cards available
      if (data.error === 'all_done' || !data.words || data.words.length === 0) {
        setPracticeError({
          title: '🎉 All done for now!',
          message: `You've completed all your reviews and learned ${data.today_new_count || 0}/${dailyNewLimit} new words today.`,
          suggestion: 'Come back later for more reviews, or increase your daily limit.',
          isSuccess: true
        });
        return;
      }
      
      setWords(data.words);
      setCurrentIndex(0);
      setSessionStats({ 
        correct: 0, 
        total: 0, 
        streak: 0, 
        maxStreak: 0,
        newCount: data.new_count || 0,
        reviewCount: data.review_count || 0
      });
      setSessionComplete(false);
      setShowSetup(false);
      setShowCustomSettings(false);
      
      // Load first question
      await loadQuestion(data.words[0].id);
    } catch (error) {
      console.error('Failed to start smart practice:', error);
      setPracticeError({
        title: '❌ Unable to start practice',
        message: error.message || 'Something went wrong. Please try again.',
        suggestion: 'Make sure the backend is running.'
      });
    } finally {
      setLoading(false);
    }
  };

  const startPractice = async () => {
    setLoading(true);
    setPracticeError(null);
    try {
      const options = {
        type: practiceType,
        count: wordCount,
        direction,
      };
      if (wordType) options.word_type = wordType;
      if (category) options.category = category;
      
      const data = await vocabularyService.startPractice(options);
      
      if (!data.words || data.words.length === 0) {
        throw new Error('No words found');
      }
      
      setWords(data.words);
      setCurrentIndex(0);
      setSessionStats({ correct: 0, total: 0, streak: 0, maxStreak: 0 });
      setSessionComplete(false);
      setShowSetup(false);
      
      // Load first question
      await loadQuestion(data.words[0].id);
    } catch (error) {
      console.error('Failed to start practice:', error);
      // Set friendly error messages based on practice type
      if (practiceType === 'review') {
        setPracticeError({
          title: '🎉 All caught up!',
          message: 'You have no words due for review right now. Great job staying on top of your learning!',
          suggestion: 'Try practicing some new words or random words instead.'
        });
      } else if (practiceType === 'new') {
        setPracticeError({
          title: '📚 No new words available',
          message: 'You\'ve practiced all unlocked words! Keep mastering them to unlock more.',
          suggestion: 'Try reviewing your existing words or switch to random practice.'
        });
      } else {
        setPracticeError({
          title: '❌ Unable to start practice',
          message: error.message || 'Something went wrong. Please try again.',
          suggestion: 'Make sure the backend is running and try different settings.'
        });
      }
    } finally {
      setLoading(false);
    }
  };

  const loadQuestion = useCallback(async (wordId) => {
    setLoading(true);
    setSelectedAnswer(null);
    setShowResult(false);
    setTypedAnswer('');
    
    try {
      const question = await vocabularyService.getQuestion(wordId, direction, questionType);
      setCurrentQuestion(question);
    } catch (error) {
      console.error('Failed to load question:', error);
    } finally {
      setLoading(false);
    }
  }, [direction, questionType]);

  const handleSelectAnswer = (answer) => {
    if (showResult) return;
    setSelectedAnswer(answer);
  };

  const handleSubmitAnswer = async () => {
    if (!selectedAnswer && !typedAnswer) return;
    
    const answer = questionType === 'multiple_choice' ? selectedAnswer : typedAnswer;
    
    try {
      const result = await vocabularyService.submitAnswer(
        currentQuestion.word_id,
        answer,
        currentQuestion.correct_answer,
        direction
      );
      
      setIsCorrect(result.correct);
      setShowResult(true);
      
      // Update session stats
      setSessionStats(prev => {
        const newStreak = result.correct ? prev.streak + 1 : 0;
        return {
          correct: prev.correct + (result.correct ? 1 : 0),
          total: prev.total + 1,
          streak: newStreak,
          maxStreak: Math.max(prev.maxStreak, newStreak)
        };
      });
    } catch (error) {
      console.error('Failed to submit answer:', error);
    }
  };

  const handleDontKnow = async () => {
    try {
      // Submit as incorrect answer to update spaced repetition
      await vocabularyService.submitAnswer(
        currentQuestion.word_id,
        '',  // Empty answer
        currentQuestion.correct_answer,
        direction
      );
      
      setIsCorrect(false);
      setShowResult(true);
      
      // Update session stats (counts as incorrect)
      setSessionStats(prev => ({
        correct: prev.correct,
        total: prev.total + 1,
        streak: 0,  // Reset streak
        maxStreak: prev.maxStreak
      }));
    } catch (error) {
      console.error('Failed to submit:', error);
    }
  };

  const handleNext = async () => {
    const nextIndex = currentIndex + 1;
    
    if (nextIndex >= words.length) {
      await loadStats(); // Refresh stats before showing completion
      setSessionComplete(true);
    } else {
      setCurrentIndex(nextIndex);
      await loadQuestion(words[nextIndex].id);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter') {
      if (showResult) {
        handleNext();
      } else if (typedAnswer || selectedAnswer) {
        handleSubmitAnswer();
      }
    }
  };

  // Setup Screen - Anki Style
  if (showSetup) {
    const dueCount = stats?.due_for_review || 0;
    const newRemaining = stats?.new_words_remaining ?? dailyNewLimit;
    const todayNew = stats?.today_new_count || 0;
    const totalCards = dueCount + Math.min(newRemaining, stats?.new_available || 0);
    
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-900 via-blue-900 to-slate-900 p-4">
        <div className="max-w-lg mx-auto">
          {/* Header */}
          <div className="flex items-center justify-between mb-6">
            <button
              onClick={onBackToHome}
              className="flex items-center text-blue-300 hover:text-white transition-colors"
            >
              <svg className="w-5 h-5 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
              </svg>
              Back
            </button>
            <div className="text-blue-300 text-sm">
              Level {stats?.level || 1} • {stats?.unlocked_words || 100} words unlocked
            </div>
          </div>

          {/* Main Study Card */}
          <div className="bg-gradient-to-br from-slate-800 to-slate-900 rounded-2xl shadow-2xl overflow-hidden border border-slate-700 mb-6">
            {/* Title */}
            <div className="text-center py-8 px-6 border-b border-slate-700">
              <div className="text-6xl mb-3">📚</div>
              <h1 className="text-3xl font-bold text-white mb-1">Λεξιλόγιο</h1>
              <p className="text-blue-300">Greek Vocabulary</p>
            </div>
            
            {/* Today's Stats */}
            <div className="grid grid-cols-3 divide-x divide-slate-700 border-b border-slate-700">
              <div className="p-4 text-center">
                <div className="text-3xl font-bold text-blue-400">
                  {statsLoading ? '...' : dueCount}
                </div>
                <div className="text-xs text-slate-400 uppercase tracking-wide">Due</div>
              </div>
              <div className="p-4 text-center">
                <div className="text-3xl font-bold text-emerald-400">
                  {statsLoading ? '...' : Math.min(newRemaining, stats?.new_available || 0)}
                </div>
                <div className="text-xs text-slate-400 uppercase tracking-wide">New</div>
              </div>
              <div className="p-4 text-center">
                <div className="text-3xl font-bold text-white">
                  {statsLoading ? '...' : totalCards}
                </div>
                <div className="text-xs text-slate-400 uppercase tracking-wide">Total</div>
              </div>
            </div>
            
            {/* Study Now Button */}
            <div className="p-6">
              {statsLoading ? (
                <div className="text-center py-4">
                  <div className="flex items-center justify-center gap-2">
                    <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-blue-400"></div>
                    <span className="text-slate-400">Loading...</span>
                  </div>
                </div>
              ) : totalCards > 0 ? (
                <button
                  onClick={startSmartPractice}
                  disabled={loading}
                  className="w-full py-5 bg-gradient-to-r from-blue-500 to-cyan-500 text-white text-xl font-bold rounded-xl 
                    hover:from-blue-600 hover:to-cyan-600 transition-all transform hover:scale-[1.02] 
                    disabled:opacity-50 disabled:transform-none shadow-lg"
                >
                  {loading ? (
                    <span className="flex items-center justify-center gap-2">
                      <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white"></div>
                      Loading...
                    </span>
                  ) : (
                    <span className="flex items-center justify-center gap-3">
                      <span className="text-2xl">▶️</span>
                      Study Now
                    </span>
                  )}
                </button>
              ) : (
                <div className="text-center py-4">
                  <div className="text-4xl mb-2">🎉</div>
                  <div className="text-white font-medium">All done for today!</div>
                  <div className="text-slate-400 text-sm mt-1">
                    You've learned {todayNew}/{dailyNewLimit} new words
                  </div>
                  <div className="text-blue-400 text-sm mt-3">
                    ↓ Want more? Use Custom Practice below
                  </div>
                </div>
              )}
            </div>
            
            {/* Daily New Word Setting */}
            <div className="px-6 pb-6">
              <div className="flex items-center justify-between bg-slate-700/50 rounded-lg p-3">
                <div className="text-slate-300 text-sm">
                  <span className="mr-2">✨</span>
                  New words/day
                </div>
                <div className="flex items-center gap-2">
                  <button 
                    onClick={() => setDailyNewLimit(Math.max(5, dailyNewLimit - 5))}
                    className="w-8 h-8 rounded bg-slate-600 text-white hover:bg-slate-500"
                  >-</button>
                  <span className="text-white font-bold w-8 text-center">{dailyNewLimit}</span>
                  <button 
                    onClick={() => setDailyNewLimit(Math.min(50, dailyNewLimit + 5))}
                    className="w-8 h-8 rounded bg-slate-600 text-white hover:bg-slate-500"
                  >+</button>
                </div>
              </div>
            </div>
          </div>

          {/* Error Message */}
          {practiceError && (
            <div className={`rounded-xl p-5 mb-6 ${practiceError.isSuccess ? 'bg-emerald-900/50 border border-emerald-700' : 'bg-amber-900/50 border border-amber-700'}`}>
              <div className="text-xl mb-2 text-white">{practiceError.title}</div>
              <p className="text-slate-300 mb-2">{practiceError.message}</p>
              <p className="text-slate-400 text-sm">{practiceError.suggestion}</p>
              <button 
                onClick={() => setPracticeError(null)}
                className="mt-3 text-blue-400 underline text-sm"
              >
                Dismiss
              </button>
            </div>
          )}

          {/* Custom Practice Toggle */}
          <button
            onClick={() => setShowCustomSettings(!showCustomSettings)}
            className="w-full py-3 text-blue-400 hover:text-blue-300 transition-colors flex items-center justify-center gap-2"
          >
            <span>{showCustomSettings ? '▲' : '▼'}</span>
            {showCustomSettings ? 'Hide' : 'Show'} Custom Practice Options
          </button>
          {!showCustomSettings && (
            <p className="text-center text-slate-500 text-xs mt-1">
              Want to practice beyond your daily limit? Expand custom options above.
            </p>
          )}

          {/* Custom Settings Panel */}
          {showCustomSettings && (
            <div className="bg-slate-800/50 rounded-xl border border-slate-700 p-6 mt-4 space-y-5">
              <h3 className="text-white font-semibold flex items-center gap-2">
                <span>⚙️</span> Custom Practice
              </h3>
              
              {/* Direction */}
              <div>
                <label className="block text-slate-400 text-sm mb-2">Direction</label>
                <div className="grid grid-cols-2 gap-2">
                  <button
                    onClick={() => setDirection('greek_to_english')}
                    className={`p-3 rounded-lg border transition-all ${
                      direction === 'greek_to_english'
                        ? 'border-blue-500 bg-blue-500/20 text-white'
                        : 'border-slate-600 text-slate-400 hover:border-slate-500'
                    }`}
                  >
                    🇬🇷 → 🇬🇧
                  </button>
                  <button
                    onClick={() => setDirection('english_to_greek')}
                    className={`p-3 rounded-lg border transition-all ${
                      direction === 'english_to_greek'
                        ? 'border-blue-500 bg-blue-500/20 text-white'
                        : 'border-slate-600 text-slate-400 hover:border-slate-500'
                    }`}
                  >
                    🇬🇧 → 🇬🇷
                  </button>
                </div>
              </div>

              {/* Practice Mode */}
              <div>
                <label className="block text-slate-400 text-sm mb-2">Practice Mode</label>
                <div className="grid grid-cols-3 gap-2">
                  {[
                    { value: 'random', icon: '🎲', label: 'Random' },
                    { value: 'new', icon: '✨', label: 'New Only' },
                    { value: 'review', icon: '🔁', label: 'Review' }
                  ].map(mode => (
                    <button
                      key={mode.value}
                      onClick={() => setPracticeType(mode.value)}
                      className={`p-3 rounded-lg border transition-all text-center ${
                        practiceType === mode.value
                          ? 'border-blue-500 bg-blue-500/20 text-white'
                          : 'border-slate-600 text-slate-400 hover:border-slate-500'
                      }`}
                    >
                      <div className="text-lg">{mode.icon}</div>
                      <div className="text-xs">{mode.label}</div>
                    </button>
                  ))}
                </div>
              </div>

              {/* Word Type */}
              <div>
                <label className="block text-slate-400 text-sm mb-2">Word Type</label>
                <select
                  value={wordType}
                  onChange={(e) => setWordType(e.target.value)}
                  className="w-full p-3 bg-slate-700 border border-slate-600 rounded-lg text-white focus:border-blue-500"
                >
                  <option value="">All Types</option>
                  {Object.entries(categories.word_types || {}).map(([type, count]) => (
                    <option key={type} value={type}>
                      {type.charAt(0).toUpperCase() + type.slice(1)} ({count})
                    </option>
                  ))}
                </select>
              </div>

              {/* Question Type */}
              <div>
                <label className="block text-slate-400 text-sm mb-2">Answer Style</label>
                <div className="grid grid-cols-3 gap-2">
                  <button
                    onClick={() => setQuestionType('multiple_choice')}
                    className={`p-3 rounded-lg border transition-all text-center ${
                      questionType === 'multiple_choice'
                        ? 'border-blue-500 bg-blue-500/20 text-white'
                        : 'border-slate-600 text-slate-400 hover:border-slate-500'
                    }`}
                  >
                    <div className="text-lg">🔘</div>
                    <div className="text-xs">Multiple</div>
                  </button>
                  <button
                    onClick={() => setQuestionType('type')}
                    className={`p-3 rounded-lg border transition-all text-center ${
                      questionType === 'type'
                        ? 'border-blue-500 bg-blue-500/20 text-white'
                        : 'border-slate-600 text-slate-400 hover:border-slate-500'
                    }`}
                  >
                    <div className="text-lg">⌨️</div>
                    <div className="text-xs">Type</div>
                  </button>
                  <button
                    onClick={() => setQuestionType('flashcard')}
                    className={`p-3 rounded-lg border transition-all text-center ${
                      questionType === 'flashcard'
                        ? 'border-blue-500 bg-blue-500/20 text-white'
                        : 'border-slate-600 text-slate-400 hover:border-slate-500'
                    }`}
                  >
                    <div className="text-lg">🃏</div>
                    <div className="text-xs">Flashcard</div>
                  </button>
                </div>
              </div>

              {/* Word Count */}
              <div>
                <label className="block text-slate-400 text-sm mb-2 flex justify-between">
                  <span>Number of Words</span>
                  <span className="text-white font-bold">{wordCount}</span>
                </label>
                <input
                  type="range"
                  min="5"
                  max="50"
                  step="5"
                  value={wordCount}
                  onChange={(e) => setWordCount(parseInt(e.target.value))}
                  className="w-full h-2 bg-slate-700 rounded-full appearance-none cursor-pointer
                    [&::-webkit-slider-thumb]:appearance-none [&::-webkit-slider-thumb]:w-5 [&::-webkit-slider-thumb]:h-5 
                    [&::-webkit-slider-thumb]:rounded-full [&::-webkit-slider-thumb]:bg-blue-500 [&::-webkit-slider-thumb]:cursor-pointer"
                />
              </div>

              {/* Start Custom Practice Button */}
              <button
                onClick={startPractice}
                disabled={loading}
                className="w-full py-3 bg-slate-700 text-white font-medium rounded-lg 
                  hover:bg-slate-600 transition-all disabled:opacity-50"
              >
                {loading ? 'Loading...' : 'Start Custom Practice'}
              </button>
            </div>
          )}
        </div>
      </div>
    );
  }

  // Session Complete Screen
  if (sessionComplete) {
    const accuracy = sessionStats.total > 0 ? Math.round((sessionStats.correct / sessionStats.total) * 100) : 0;
    
    // Handle going back to vocab setup
    const handleBackToVocabSetup = async () => {
      await loadStats(); // Refresh stats first
      setSessionComplete(false);
      setShowSetup(true);
    };
    
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-900 via-blue-900 to-slate-900 p-4 flex items-center justify-center">
        <div className="max-w-md w-full">
          <div className="bg-slate-800 rounded-2xl shadow-2xl border border-slate-700 overflow-hidden">
            {/* Header */}
            <div className="text-center py-8 bg-gradient-to-r from-emerald-600 to-cyan-600">
              <div className="text-6xl mb-2">🎉</div>
              <h2 className="text-2xl font-bold text-white">Session Complete!</h2>
            </div>
            
            {/* Stats */}
            <div className="p-6">
              <div className="grid grid-cols-3 gap-3 mb-6">
                <div className="text-center p-3 bg-slate-700/50 rounded-xl">
                  <div className="text-2xl font-bold text-emerald-400">{sessionStats.correct}</div>
                  <div className="text-xs text-slate-400">Correct</div>
                </div>
                <div className="text-center p-3 bg-slate-700/50 rounded-xl">
                  <div className="text-2xl font-bold text-red-400">{sessionStats.total - sessionStats.correct}</div>
                  <div className="text-xs text-slate-400">Wrong</div>
                </div>
                <div className="text-center p-3 bg-slate-700/50 rounded-xl">
                  <div className="text-2xl font-bold text-amber-400">{sessionStats.maxStreak}</div>
                  <div className="text-xs text-slate-400">Streak</div>
                </div>
              </div>

              {/* Accuracy Circle */}
              <div className="flex justify-center mb-6">
                <div className="relative w-28 h-28">
                  <svg className="w-full h-full transform -rotate-90">
                    <circle cx="56" cy="56" r="48" fill="none" stroke="#334155" strokeWidth="10"/>
                    <circle 
                      cx="56" cy="56" r="48" fill="none" 
                      stroke={accuracy >= 80 ? '#10b981' : accuracy >= 60 ? '#f59e0b' : '#ef4444'}
                      strokeWidth="10"
                      strokeLinecap="round"
                      strokeDasharray={`${accuracy * 3.02} 302`}
                    />
                  </svg>
                  <div className="absolute inset-0 flex items-center justify-center">
                    <span className="text-2xl font-bold text-white">{accuracy}%</span>
                  </div>
                </div>
              </div>
              
              {/* New/Review breakdown */}
              {(sessionStats.newCount > 0 || sessionStats.reviewCount > 0) && (
                <div className="flex justify-center gap-4 mb-6 text-sm">
                  {sessionStats.newCount > 0 && (
                    <span className="text-emerald-400">✨ {sessionStats.newCount} new</span>
                  )}
                  {sessionStats.reviewCount > 0 && (
                    <span className="text-blue-400">🔁 {sessionStats.reviewCount} reviewed</span>
                  )}
                </div>
              )}
              
              {/* Buttons */}
              <div className="space-y-3">
                <button
                  onClick={handleBackToVocabSetup}
                  className="w-full py-4 bg-gradient-to-r from-blue-500 to-cyan-500 text-white font-bold rounded-xl 
                    hover:from-blue-600 hover:to-cyan-600 transition-all"
                >
                  Continue Studying
                </button>
                <button
                  onClick={onBackToHome}
                  className="w-full py-3 bg-slate-700 text-slate-300 rounded-xl hover:bg-slate-600 transition-colors"
                >
                  Back to Home
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    );
  }

  // Practice Screen
  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-blue-900 to-slate-900 p-4" onKeyPress={handleKeyPress}>
      <div className="max-w-lg mx-auto">
        {/* Header */}
        <div className="flex items-center justify-between mb-4">
          <button
            onClick={() => setShowSetup(true)}
            className="text-slate-400 hover:text-white transition-colors"
          >
            ✕ End
          </button>
          <div className="text-slate-400">
            {currentIndex + 1} / {words.length}
          </div>
          <div className="text-amber-400 font-medium">
            🔥 {sessionStats.streak}
          </div>
        </div>

        {/* Progress Bar */}
        <div className="w-full bg-slate-700 rounded-full h-2 mb-6">
          <div
            className="bg-gradient-to-r from-blue-500 to-cyan-500 h-2 rounded-full transition-all duration-300"
            style={{ width: `${((currentIndex + 1) / words.length) * 100}%` }}
          />
        </div>

        {/* Question Card */}
        {loading ? (
          <div className="bg-slate-800 rounded-xl border border-slate-700 p-8 text-center">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500 mx-auto"></div>
            <p className="mt-4 text-slate-400">Loading question...</p>
          </div>
        ) : currentQuestion && (
          <div className="bg-slate-800 rounded-xl border border-slate-700 overflow-hidden">
            {/* Question */}
            <div className="p-6 bg-gradient-to-r from-blue-600 to-cyan-600 text-white">
              <div className="text-sm opacity-80 mb-2">
                {direction === 'greek_to_english' ? '🇬🇷 Translate to English:' : '🇬🇧 Translate to Greek:'}
              </div>
              <div className="text-3xl font-bold">{currentQuestion.question}</div>
              <div className="text-sm opacity-80 mt-2">
                ({currentQuestion.word_type})
              </div>
            </div>

            {/* Answer Area */}
            <div className="p-6">
              {questionType === 'flashcard' ? (
                // Flashcard Mode
                <div className="text-center">
                  {!flashcardRevealed && !showResult ? (
                    <>
                      <p className="text-slate-400 mb-4">Think of the answer, then reveal to check</p>
                      <button
                        onClick={() => setFlashcardRevealed(true)}
                        className="w-full py-4 bg-gradient-to-r from-blue-500 to-cyan-500 text-white font-bold rounded-xl 
                          hover:from-blue-600 hover:to-cyan-600 transition-all text-lg"
                      >
                        👁️ Reveal Answer
                      </button>
                    </>
                  ) : !showResult ? (
                    <>
                      <div className="bg-slate-700/50 rounded-xl p-6 mb-4">
                        <p className="text-slate-400 text-sm mb-2">Correct Answer:</p>
                        <p className="text-3xl font-bold text-white">
                          {currentQuestion.correct_answer}
                        </p>
                        {currentQuestion.full_translation && (
                          <p className="text-slate-400 text-sm mt-2">{currentQuestion.full_translation}</p>
                        )}
                      </div>
                      <p className="text-slate-400 mb-4">Did you get it right?</p>
                      <div className="grid grid-cols-2 gap-3">
                        <button
                          onClick={() => {
                            setIsCorrect(false);
                            setShowResult(true);
                            setFlashcardRevealed(false);
                            setSessionStats(prev => ({
                              ...prev,
                              total: prev.total + 1,
                              streak: 0
                            }));
                          }}
                          className="py-4 bg-red-500/20 border border-red-500 text-red-400 font-bold rounded-xl hover:bg-red-500/30 transition-all"
                        >
                          ❌ Wrong
                        </button>
                        <button
                          onClick={() => {
                            setIsCorrect(true);
                            setShowResult(true);
                            setFlashcardRevealed(false);
                            setSessionStats(prev => ({
                              ...prev,
                              correct: prev.correct + 1,
                              total: prev.total + 1,
                              streak: prev.streak + 1,
                              maxStreak: Math.max(prev.maxStreak, prev.streak + 1)
                            }));
                          }}
                          className="py-4 bg-emerald-500/20 border border-emerald-500 text-emerald-400 font-bold rounded-xl hover:bg-emerald-500/30 transition-all"
                        >
                          ✓ Correct
                        </button>
                      </div>
                    </>
                  ) : null}
                </div>
              ) : questionType === 'multiple_choice' ? (
                // Multiple Choice Options
                <div className="space-y-3">
                  {currentQuestion.options?.map((option, index) => (
                    <button
                      key={index}
                      onClick={() => handleSelectAnswer(option)}
                      disabled={showResult}
                      className={`w-full p-4 text-left rounded-xl border-2 transition-all ${
                        showResult
                          ? option === currentQuestion.correct_answer
                            ? 'border-emerald-500 bg-emerald-500/20 text-emerald-400'
                            : option === selectedAnswer
                              ? 'border-red-500 bg-red-500/20 text-red-400'
                              : 'border-slate-600 opacity-50 text-slate-500'
                          : selectedAnswer === option
                            ? 'border-blue-500 bg-blue-500/20 text-white'
                            : 'border-slate-600 hover:border-blue-400 text-slate-200 hover:bg-slate-700'
                      }`}
                    >
                      <span className="font-medium">{option}</span>
                      {showResult && option === currentQuestion.correct_answer && (
                        <span className="float-right text-emerald-400">✓</span>
                      )}
                      {showResult && option === selectedAnswer && option !== currentQuestion.correct_answer && (
                        <span className="float-right text-red-400">✗</span>
                      )}
                    </button>
                  ))}
                </div>
              ) : (
                // Type Answer
                <div>
                  <input
                    type="text"
                    value={typedAnswer}
                    onChange={(e) => setTypedAnswer(e.target.value)}
                    disabled={showResult}
                    placeholder={direction === 'english_to_greek' ? 'Type in Greek...' : 'Type in English...'}
                    className={`w-full p-4 text-lg border-2 rounded-xl bg-slate-700 text-white placeholder-slate-400 focus:outline-none ${
                      showResult
                        ? isCorrect
                          ? 'border-emerald-500 bg-emerald-500/20'
                          : 'border-red-500 bg-red-500/20'
                        : 'border-slate-600 focus:border-blue-500'
                    }`}
                    autoFocus
                  />
                  {showResult && !isCorrect && (
                    <div className="mt-2 text-sm text-slate-400">
                      Correct: <span className="font-bold text-emerald-400">{currentQuestion.correct_answer}</span>
                    </div>
                  )}
                </div>
              )}

              {/* Result Message */}
              {showResult && (
                <div className={`mt-4 p-4 rounded-xl ${isCorrect ? 'bg-emerald-500/20 border border-emerald-500/50' : 'bg-amber-500/20 border border-amber-500/50'}`}>
                  <div className={`font-bold ${isCorrect ? 'text-emerald-400' : 'text-amber-400'}`}>
                    {isCorrect ? '🎉 Correct!' : '📖 The answer is:'}
                  </div>
                  {!isCorrect && (
                    <div className="mt-2 text-lg font-bold text-white">
                      {currentQuestion.correct_answer}
                    </div>
                  )}
                  {currentQuestion.full_translation && (
                    <div className="mt-2 text-sm text-slate-400">
                      Full meaning: {currentQuestion.full_translation}
                    </div>
                  )}
                </div>
              )}

              {/* Action Buttons */}
              <div className="mt-6 space-y-3">
                {!showResult ? (
                  <>
                    <button
                      onClick={handleSubmitAnswer}
                      disabled={!selectedAnswer && !typedAnswer}
                      className="w-full py-4 bg-gradient-to-r from-blue-500 to-cyan-500 text-white font-bold rounded-xl 
                        hover:from-blue-600 hover:to-cyan-600 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                    >
                      Check Answer
                    </button>
                    <button
                      onClick={handleDontKnow}
                      className="w-full py-3 bg-slate-700 text-slate-300 font-medium rounded-xl hover:bg-slate-600 transition-colors"
                    >
                      🤷 I don't know
                    </button>
                  </>
                ) : (
                  <button
                    onClick={handleNext}
                    className="w-full py-4 bg-gradient-to-r from-blue-500 to-cyan-500 text-white font-bold rounded-xl 
                      hover:from-blue-600 hover:to-cyan-600 transition-colors"
                  >
                    {currentIndex + 1 >= words.length ? '🏁 Finish' : 'Next →'}
                  </button>
                )}
              </div>
            </div>
          </div>
        )}

        {/* Session Stats */}
        <div className="mt-4 bg-slate-800/50 border border-slate-700 rounded-xl p-4 flex justify-around text-sm">
          <div className="text-center">
            <div className="font-bold text-emerald-400">{sessionStats.correct}</div>
            <div className="text-slate-500">Correct</div>
          </div>
          <div className="text-center">
            <div className="font-bold text-slate-300">{sessionStats.total}</div>
            <div className="text-slate-500">Total</div>
          </div>
          <div className="text-center">
            <div className="font-bold text-amber-400">{sessionStats.maxStreak}</div>
            <div className="text-slate-500">Best Streak</div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default VocabularyPractice;

