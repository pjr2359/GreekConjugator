import React, { useState, useEffect } from 'react';
import GreekKeyboard, { compareGreekTexts } from './GreekKeyboard';
import { verbsService, textValidationService } from '../services/api';

// Grammar term definitions for tooltips (lowercase keys to match database values)
const grammarTerms = {
  // Tenses (lowercase)
  'present': { greek: 'Ενεστώτας', desc: 'Action happening now', example: 'γράφω (I write)' },
  'imperfect': { greek: 'Παρατατικός', desc: 'Continuous past action', example: 'έγραφα (I was writing)' },
  'aorist': { greek: 'Αόριστος', desc: 'Simple past action', example: 'έγραψα (I wrote)' },
  'future': { greek: 'Μέλλοντας', desc: 'Action that will happen', example: 'θα γράψω (I will write)' },
  'perfect': { greek: 'Παρακείμενος', desc: 'Completed action', example: 'έχω γράψει (I have written)' },
  // Moods (lowercase)
  'indicative': { greek: 'Οριστική', desc: 'Stating facts', example: 'Γράφει γράμματα' },
  'subjunctive': { greek: 'Υποτακτική', desc: 'Wishes, possibilities', example: 'να γράψω' },
  'imperative': { greek: 'Προστακτική', desc: 'Commands', example: 'Γράψε! (Write!)' },
  // Voice (lowercase)
  'active': { greek: 'Ενεργητική', desc: 'Subject does action', example: 'πλένω (I wash)' },
  'passive': { greek: 'Παθητική', desc: 'Subject receives action', example: 'πλένομαι (I am washed)' },
  // Number (lowercase)
  'singular': { greek: 'Ενικός', desc: 'One person', example: 'γράφω' },
  'plural': { greek: 'Πληθυντικός', desc: 'Multiple people', example: 'γράφουμε' },
};

// Tooltip component for grammar terms
const GrammarTerm = ({ term }) => {
  if (!term) return null;
  const key = term.toLowerCase();
  const info = grammarTerms[key];
  
  // Capitalize for display
  const displayTerm = term.charAt(0).toUpperCase() + term.slice(1);
  
  if (!info) return <span className="font-medium">{displayTerm}</span>;
  
  return (
    <span className="relative group inline-block">
      <span className="font-medium underline decoration-dotted decoration-purple-400/70 cursor-help">
        {displayTerm}
      </span>
      <span className="absolute bottom-full left-1/2 -translate-x-1/2 mb-2 px-3 py-2 bg-slate-900 text-white text-xs rounded-lg 
        opacity-0 group-hover:opacity-100 transition-opacity pointer-events-none whitespace-nowrap z-50 shadow-xl border border-slate-700">
        <span className="font-bold text-purple-400">{info.greek}</span>
        <br />
        <span className="text-slate-300">{info.desc}</span>
        <br />
        <span className="text-slate-400 italic">e.g. {info.example}</span>
        <span className="absolute top-full left-1/2 -translate-x-1/2 border-4 border-transparent border-t-slate-900"></span>
      </span>
    </span>
  );
};

// Parse and render conjugation prompt with tooltips
const ConjugationPrompt = ({ tense, mood, voice, number }) => {
  return (
    <span className="text-white/90 flex flex-wrap justify-center gap-2">
      {tense && <GrammarTerm term={tense} />}
      {mood && <><span className="text-white/50">•</span><GrammarTerm term={mood} /></>}
      {voice && <><span className="text-white/50">•</span><GrammarTerm term={voice} /></>}
      {number && <><span className="text-white/50">•</span><GrammarTerm term={number} /></>}
    </span>
  );
};

const PracticeSession = ({ user, onBackToHome }) => {
  const [sessionData, setSessionData] = useState(null);
  const [currentQuestionIndex, setCurrentQuestionIndex] = useState(0);
  const [userAnswer, setUserAnswer] = useState('');
  const [showResult, setShowResult] = useState(false);
  const [isCorrect, setIsCorrect] = useState(false);
  const [score, setScore] = useState({ correct: 0, total: 0 });
  const [loading, setLoading] = useState(false);
  const [sessionComplete, setSessionComplete] = useState(false);
  const [conjugations, setConjugations] = useState({});
  const [validationResult, setValidationResult] = useState(null);
  const [showHints, setShowHints] = useState(false);
  const [currentQuestion, setCurrentQuestion] = useState(null);
  const [isEndlessMode, setIsEndlessMode] = useState(true); // Default to endless mode
  // New smart practice features
  const [practiceMode, setPracticeMode] = useState('conjugation'); // 'conjugation', 'multiple_choice', 'smart', 'flashcard'
  const [answerMode, setAnswerMode] = useState('multiple_choice'); // 'multiple_choice', 'type', 'flashcard'
  const [smartQuestion, setSmartQuestion] = useState(null);
  const [selectedMultipleChoice, setSelectedMultipleChoice] = useState(null);
  const [flashcardRevealed, setFlashcardRevealed] = useState(false);
  const [practiceStats, setPracticeStats] = useState({
    totalQuestions: 0,
    correctAnswers: 0,
    accuracy: 0,
    streak: 0,
    maxStreak: 0
  });

  // Start a new practice session
  const startSession = async (sessionType = 'graded', difficulty = 3) => {
    setLoading(true);
    try {
      const session = await verbsService.startPracticeSession(sessionType, difficulty, 20);
      setSessionData(session);

      // Load conjugations for all verbs in the session
      const conjPromises = session.verbs.map(verb =>
        verbsService.getConjugations(verb.id)
      );
      const allConjugations = await Promise.all(conjPromises);

      const conjugationsMap = {};
      session.verbs.forEach((verb, index) => {
        conjugationsMap[verb.id] = allConjugations[index];
      });
      setConjugations(conjugationsMap);

      setCurrentQuestionIndex(0);
      setScore({ correct: 0, total: 0 });
      setSessionComplete(false);
      setPracticeStats(prev => ({
        ...prev,
        totalQuestions: prev.totalQuestions,
        correctAnswers: prev.correctAnswers,
        accuracy: prev.totalQuestions > 0 ? Math.round((prev.correctAnswers / prev.totalQuestions) * 100) : 0
      }));
    } catch (error) {
      console.error('Failed to start session:', error);
    } finally {
      setLoading(false);
    }
  };

  // Get current question data
  const getCurrentQuestion = () => {
    if (!sessionData || !sessionData.verbs[currentQuestionIndex]) return null;

    const verb = sessionData.verbs[currentQuestionIndex];
    const verbConjugations = conjugations[verb.id] || [];

    if (verbConjugations.length === 0) return null;

    // If we don't have a current question or the verb has changed, generate a new one
    if (!currentQuestion || currentQuestion.verb.id !== verb.id) {
      // Pick a random conjugation for this question
      const randomConjugation = verbConjugations[Math.floor(Math.random() * verbConjugations.length)];

      const newQuestion = {
        verb,
        conjugation: randomConjugation,
        prompt: `Conjugate "${verb.infinitive}" (${verb.english}) in ${randomConjugation.tense} tense, ${randomConjugation.mood} mood, ${randomConjugation.person} person ${randomConjugation.number}`
      };

      setCurrentQuestion(newQuestion);
      return newQuestion;
    }

    return currentQuestion;
  };

  // Enhanced answer checking with Greek text processing
  const checkAnswer = async (userInput, correctAnswer) => {
    try {
      // Use the enhanced Greek text processing API
      const result = await textValidationService.checkAnswer(userInput, correctAnswer, 'lenient');
      setValidationResult(result);
      return result.correct;
    } catch (error) {
      console.error('API validation failed, falling back to compareGreekTexts:', error);
      // Fallback to client-side comparison
      return await compareGreekTexts(userInput, correctAnswer, 'lenient');
    }
  };

  // Submit answer
  const submitAnswer = async () => {
    const question = getCurrentQuestion();
    if (!question) return;

    setLoading(true);
    try {
      const correct = await checkAnswer(userAnswer, question.conjugation.form);
      setIsCorrect(correct);
      setShowResult(true);

      // Update score
      const newScore = {
        correct: score.correct + (correct ? 1 : 0),
        total: score.total + 1
      };
      setScore(newScore);

      // Update practice stats
      const newTotalQuestions = practiceStats.totalQuestions + 1;
      const newCorrectAnswers = practiceStats.correctAnswers + (correct ? 1 : 0);
      const newStreak = correct ? practiceStats.streak + 10 : 0;
      const newMaxStreak = Math.max(practiceStats.maxStreak, newStreak);

      setPracticeStats({
        totalQuestions: newTotalQuestions,
        correctAnswers: newCorrectAnswers,
        accuracy: Math.round((newCorrectAnswers / newTotalQuestions) * 100),
        streak: newStreak,
        maxStreak: newMaxStreak
      });

      // Submit to backend
      await verbsService.submitAnswer(
        sessionData.session_id,
        question.conjugation.id,
        userAnswer,
        correct
      );
    } catch (error) {
      console.error('Failed to submit answer:', error);
      // Still show result even if API fails
      setShowResult(true);
    } finally {
      setLoading(false);
    }
  };

  // Move to next question
  const nextQuestion = () => {
    setShowResult(false);
    setUserAnswer('');
    setValidationResult(null);
    setCurrentQuestion(null); // Clear current question to force generation of new one
    setSmartQuestion(null); // Clear smart question
    setSelectedMultipleChoice(null); // Clear multiple choice selection

    if (isEndlessMode) {
      // In endless mode, just move to the next verb or cycle back
      let nextIndex = currentQuestionIndex + 1;
      if (nextIndex >= sessionData.verbs.length) {
        // Cycle back to the beginning for endless practice
        nextIndex = 0;
      }
      setCurrentQuestionIndex(nextIndex);
    } else {
      // Fixed session mode (5 questions)
      const questionsPerSession = 5;
      if (score.total >= questionsPerSession) {
        setSessionComplete(true);
      } else {
        // Try to find the next verb with conjugations
        let nextIndex = currentQuestionIndex + 1;
        while (nextIndex < sessionData.verbs.length) {
          const nextVerb = sessionData.verbs[nextIndex];
          const nextVerbConjugations = conjugations[nextVerb.id] || [];
          if (nextVerbConjugations.length > 0) {
            setCurrentQuestionIndex(nextIndex);
            return;
          }
          nextIndex++;
        }
        // If we can't find more verbs with conjugations, end the session
        setSessionComplete(true);
      }
    }
  };

  // Generate smart practice question
  const generateSmartQuestion = async () => {
    if (!sessionData || !sessionData.verbs[currentQuestionIndex]) return null;

    const verb = sessionData.verbs[currentQuestionIndex];
    
    try {
      const questionType = practiceMode === 'smart' ? 
        (Math.random() > 0.5 ? 'multiple_choice' : 'conjugation') : 
        practiceMode;
        
      const response = await verbsService.generatePracticeQuestion(
        sessionData.session_id,
        verb.id,
        questionType
      );
      
      setSmartQuestion(response);
      setSelectedMultipleChoice(null);
      return response;
    } catch (error) {
      console.error('Failed to generate smart question:', error);
      // Fallback to regular question
      return getCurrentQuestion();
    }
  };

  // Handle multiple choice selection
  const handleMultipleChoiceSelect = (option) => {
    setSelectedMultipleChoice(option);
    setUserAnswer(option);
  };

  // Submit smart practice answer
  const submitSmartAnswer = async () => {
    if (!smartQuestion) return;

    setLoading(true);
    try {
      const userInput = practiceMode === 'multiple_choice' || smartQuestion.type === 'multiple_choice' 
        ? selectedMultipleChoice 
        : userAnswer;
        
      if (!userInput) {
        setLoading(false);
        return;
      }

      const correct = userInput === smartQuestion.correct_answer;
      setIsCorrect(correct);
      setShowResult(true);

      // Update score and stats
      const newScore = {
        correct: score.correct + (correct ? 1 : 0),
        total: score.total + 1
      };
      setScore(newScore);

      const newTotalQuestions = practiceStats.totalQuestions + 1;
      const newCorrectAnswers = practiceStats.correctAnswers + (correct ? 1 : 0);
      const newStreak = correct ? practiceStats.streak + 1 : 0;
      const newMaxStreak = Math.max(practiceStats.maxStreak, newStreak);

      setPracticeStats({
        totalQuestions: newTotalQuestions,
        correctAnswers: newCorrectAnswers,
        accuracy: Math.round((newCorrectAnswers / newTotalQuestions) * 100),
        streak: newStreak,
        maxStreak: newMaxStreak
      });

      // Submit to backend
      await verbsService.submitAnswer(
        sessionData.session_id,
        smartQuestion.conjugation.id,
        userInput,
        correct
      );
    } catch (error) {
      console.error('Failed to submit smart answer:', error);
      setShowResult(true);
    } finally {
      setLoading(false);
    }
  };

  // Toggle between endless and fixed session modes
  const toggleMode = () => {
    setIsEndlessMode(!isEndlessMode);
    setSessionComplete(false);
    setCurrentQuestionIndex(0);
    setScore({ correct: 0, total: 0 });
  };

  // Don't auto-start - wait for user to click Start Practice

  // Generate smart question when practice mode changes or new question is needed
  useEffect(() => {
    const loadSmartQuestion = async () => {
      if (!sessionData || (practiceMode !== 'smart' && practiceMode !== 'multiple_choice')) return;
      if (showResult) return; // Don't generate new question if showing result

      try {
        await generateSmartQuestion();
      } catch (error) {
        console.error('Failed to load smart question:', error);
      }
    };

    loadSmartQuestion();
  }, [sessionData, practiceMode, currentQuestionIndex]);

  const question = getCurrentQuestion();

  // Show loading spinner only when actively loading
  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-900 via-blue-900 to-slate-900 flex justify-center items-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-16 w-16 border-b-2 border-purple-500 mx-auto mb-4"></div>
          <p className="text-slate-400">Loading practice session...</p>
        </div>
      </div>
    );
  }

  // Show start screen when no session data
  if (!sessionData) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-900 via-blue-900 to-slate-900 p-6 flex items-center justify-center">
        <div className="max-w-md w-full bg-slate-800 rounded-2xl border border-slate-700 overflow-hidden">
          {/* Header */}
          <div className="bg-gradient-to-r from-purple-600 to-pink-600 p-6 text-center">
            <div className="text-5xl mb-2">📝</div>
            <h2 className="text-2xl font-bold text-white">Κλίση Ρημάτων</h2>
            <p className="text-purple-100">Conjugation Practice</p>
          </div>
          
          <div className="p-6">
            {/* Stats */}
            <div className="grid grid-cols-3 gap-3 mb-6">
              <div className="bg-slate-700/50 rounded-lg p-3 text-center">
                <div className="text-lg font-bold text-white">87</div>
                <div className="text-xs text-slate-400">Verbs</div>
              </div>
              <div className="bg-slate-700/50 rounded-lg p-3 text-center">
                <div className="text-lg font-bold text-white">5,400+</div>
                <div className="text-xs text-slate-400">Forms</div>
              </div>
              <div className="bg-slate-700/50 rounded-lg p-3 text-center">
                <div className="text-lg font-bold text-white">🧠</div>
                <div className="text-xs text-slate-400">SRS</div>
              </div>
            </div>
            
            {/* Answer Mode Selection */}
            <div className="mb-6">
              <label className="block text-slate-400 text-sm mb-3">Answer Mode</label>
              <div className="grid grid-cols-3 gap-2">
                <button
                  onClick={() => setAnswerMode('multiple_choice')}
                  className={`p-3 rounded-xl border transition-all text-center ${
                    answerMode === 'multiple_choice'
                      ? 'border-purple-500 bg-purple-500/20 text-white'
                      : 'border-slate-600 text-slate-400 hover:border-slate-500'
                  }`}
                >
                  <div className="text-xl mb-1">🔘</div>
                  <div className="text-xs">Multiple<br/>Choice</div>
                </button>
                <button
                  onClick={() => setAnswerMode('type')}
                  className={`p-3 rounded-xl border transition-all text-center ${
                    answerMode === 'type'
                      ? 'border-purple-500 bg-purple-500/20 text-white'
                      : 'border-slate-600 text-slate-400 hover:border-slate-500'
                  }`}
                >
                  <div className="text-xl mb-1">⌨️</div>
                  <div className="text-xs">Type<br/>Answer</div>
                </button>
                <button
                  onClick={() => setAnswerMode('flashcard')}
                  className={`p-3 rounded-xl border transition-all text-center ${
                    answerMode === 'flashcard'
                      ? 'border-purple-500 bg-purple-500/20 text-white'
                      : 'border-slate-600 text-slate-400 hover:border-slate-500'
                  }`}
                >
                  <div className="text-xl mb-1">🃏</div>
                  <div className="text-xs">Flashcard<br/>Self-Grade</div>
                </button>
              </div>
              <p className="text-slate-500 text-xs mt-2 text-center">
                {answerMode === 'multiple_choice' && 'Pick the correct conjugation from options'}
                {answerMode === 'type' && 'Type the conjugation in Greek'}
                {answerMode === 'flashcard' && 'Think of answer, then reveal and self-grade'}
              </p>
            </div>
            
            <button
              onClick={() => {
                setPracticeMode(answerMode);
                setFlashcardRevealed(false);
                startSession();
              }}
              className="w-full py-4 bg-gradient-to-r from-purple-500 to-pink-500 text-white font-bold rounded-xl 
                hover:from-purple-600 hover:to-pink-600 transition-all text-lg mb-3"
            >
              ▶️ Start Practice
            </button>
            
            {onBackToHome && (
              <button
                onClick={onBackToHome}
                className="w-full py-3 bg-slate-700 text-slate-300 rounded-xl hover:bg-slate-600 transition-colors"
              >
                ← Back to Home
              </button>
            )}
          </div>
        </div>
      </div>
    );
  }

  if (sessionComplete && !isEndlessMode) {
    const accuracy = Math.round((score.correct / score.total) * 100);
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-900 via-blue-900 to-slate-900 p-6 flex items-center justify-center">
        <div className="max-w-md w-full bg-slate-800 rounded-2xl border border-slate-700 shadow-2xl overflow-hidden">
          <div className="text-center py-8 bg-gradient-to-r from-purple-600 to-pink-600">
            <div className="text-6xl mb-2">{accuracy >= 80 ? '🏆' : accuracy >= 60 ? '👏' : '💪'}</div>
            <h2 className="text-2xl font-bold text-white">Session Complete!</h2>
          </div>
          <div className="p-6">
            <div className="text-center mb-6">
              <div className="text-4xl font-bold text-white mb-1">{accuracy}%</div>
              <p className="text-slate-400">{score.correct} / {score.total} correct</p>
            </div>

            <div className="space-y-3">
              <button
                onClick={() => startSession('graded', 3)}
                className="w-full py-4 bg-gradient-to-r from-purple-500 to-pink-500 text-white font-bold rounded-xl hover:from-purple-600 hover:to-pink-600 transition-all"
              >
                Start New Session
              </button>
              <button
                onClick={() => {
                  setIsEndlessMode(true);
                  setSessionComplete(false);
                  setCurrentQuestionIndex(0);
                  setScore({ correct: 0, total: 0 });
                }}
                className="w-full py-3 bg-slate-700 text-white rounded-xl hover:bg-slate-600 transition-colors"
              >
                Endless Mode
              </button>
              {onBackToHome && (
                <button
                  onClick={onBackToHome}
                  className="w-full py-3 bg-slate-700/50 text-slate-300 rounded-xl hover:bg-slate-600 transition-colors"
                >
                  Back to Home
                </button>
              )}
            </div>
          </div>
        </div>
      </div>
    );
  }

  if (!question) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-900 via-blue-900 to-slate-900 p-6 flex items-center justify-center">
        <div className="max-w-md w-full bg-slate-800 rounded-2xl border border-slate-700 p-8 text-center">
          <div className="text-5xl mb-4">⏳</div>
          <h2 className="text-xl font-bold text-white mb-4">Preparing Question...</h2>
          <p className="text-slate-400 mb-4">Loading verb conjugations</p>
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-purple-500 mx-auto"></div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-blue-900 to-slate-900 p-4">
      <div className="max-w-2xl mx-auto">
        <div className="bg-slate-800 rounded-2xl border border-slate-700 shadow-xl overflow-hidden">
          {/* Header */}
          <div className="p-4 border-b border-slate-700 flex justify-between items-center">
            <div className="flex items-center space-x-4">
              {onBackToHome && (
                <button
                  onClick={onBackToHome}
                  className="text-slate-400 hover:text-white transition-colors"
                >
                  ← Back
                </button>
              )}
              <h1 className="text-lg font-bold text-white">
                {isEndlessMode ? '∞ Endless' : 'Practice Session'}
              </h1>
            </div>
            <button
              onClick={toggleMode}
              className="text-sm text-slate-400 hover:text-white transition-colors"
            >
              {isEndlessMode ? 'Session Mode' : 'Endless Mode'}
            </button>
          </div>

          <div className="p-6">
            {/* Practice Mode Selector */}
            <div className="mb-6 p-4 bg-slate-700/50 rounded-xl">
              <h3 className="font-semibold text-slate-300 mb-3 text-sm">Practice Mode</h3>
              <div className="flex flex-wrap gap-2">
                <button
                  onClick={() => setPracticeMode('conjugation')}
                  className={`py-2 px-4 rounded-lg transition-colors text-sm ${
                    practiceMode === 'conjugation'
                      ? 'bg-purple-600 text-white'
                      : 'bg-slate-600 text-slate-300 hover:bg-slate-500'
                  }`}
          >
            ✍️ Type Answer
          </button>
          <button
            onClick={() => setPracticeMode('multiple_choice')}
            className={`py-2 px-4 rounded-lg transition-colors text-sm ${
              practiceMode === 'multiple_choice'
                ? 'bg-emerald-600 text-white'
                : 'bg-slate-600 text-slate-300 hover:bg-slate-500'
            }`}
          >
            📝 Multiple Choice
          </button>
          <button
            onClick={() => setPracticeMode('smart')}
            className={`py-2 px-4 rounded-lg transition-colors text-sm ${
              practiceMode === 'smart'
                ? 'bg-pink-600 text-white'
                : 'bg-slate-600 text-slate-300 hover:bg-slate-500'
            }`}
          >
            🧠 Smart Mix
          </button>
              </div>
            </div>

            {/* Real-time practice statistics */}
            <div className="mb-6 grid grid-cols-4 gap-3">
              <div className="text-center p-3 bg-slate-700/50 rounded-xl">
                <div className="text-xl font-bold text-blue-400">{practiceStats.totalQuestions}</div>
                <div className="text-xs text-slate-500">Total</div>
              </div>
              <div className="text-center p-3 bg-slate-700/50 rounded-xl">
                <div className="text-xl font-bold text-emerald-400">{practiceStats.correctAnswers}</div>
                <div className="text-xs text-slate-500">Correct</div>
              </div>
              <div className="text-center p-3 bg-slate-700/50 rounded-xl">
                <div className="text-xl font-bold text-amber-400">{practiceStats.accuracy}%</div>
                <div className="text-xs text-slate-500">Accuracy</div>
              </div>
              <div className="text-center p-3 bg-slate-700/50 rounded-xl">
                <div className="text-xl font-bold text-pink-400">{practiceStats.streak} 🔥</div>
                <div className="text-xs text-slate-500">Streak</div>
              </div>
            </div>

            {/* Progress bar (only for session mode) */}
            {!isEndlessMode && (
              <div className="mb-6">
                <div className="flex justify-between text-sm text-slate-400 mb-2">
                  <span>{currentQuestionIndex + 1} / {sessionData?.verbs.length || 0}</span>
                  <span>{score.correct}/{score.total} correct</span>
                </div>
                <div className="w-full bg-slate-700 rounded-full h-2">
                  <div
                    className="bg-gradient-to-r from-purple-500 to-pink-500 h-2 rounded-full transition-all duration-300"
                    style={{ width: `${((currentQuestionIndex + 1) / (sessionData?.verbs.length || 1)) * 100}%` }}
                  ></div>
                </div>
              </div>
            )}

            {/* Question */}
            <div className="mb-6">
              {smartQuestion && (practiceMode === 'smart' || practiceMode === 'multiple_choice') ? (
                // Smart Practice Question
                <div className="bg-gradient-to-r from-purple-600 to-pink-600 rounded-xl p-6 mb-4">
                  <div className="text-white/80 text-sm mb-2">
                    {smartQuestion.type === 'multiple_choice' ? '📝 Multiple Choice' : '✍️ Conjugate'}
                  </div>
                  <div className="text-center mb-4">
                    <span className="text-3xl font-bold text-white" style={{ fontFamily: 'Georgia, serif' }}>
                      {smartQuestion.verb.infinitive}
                    </span>
                    <p className="text-white/70 mt-1">"{smartQuestion.translation}"</p>
                  </div>
                  <div className="text-center text-sm bg-white/10 rounded-lg p-3">
                    <ConjugationPrompt 
                      tense={smartQuestion.tense || 'present'}
                      mood={smartQuestion.mood || 'indicative'}
                      voice={smartQuestion.voice}
                      number={smartQuestion.number || 'singular'}
                    />
                    <p className="text-white/50 text-xs mt-2">💡 Hover over underlined terms for definitions</p>
                  </div>
                  {smartQuestion.hint && (
                    <p className="text-sm text-white/60 mt-3 italic text-center">{smartQuestion.hint}</p>
                  )}
                </div>
              ) : (
                // Regular Practice Question
                <div className="bg-gradient-to-r from-purple-600 to-pink-600 rounded-xl p-6 mb-4">
                  <div className="text-white/80 text-sm mb-2">✍️ Conjugate the Verb</div>
                  <div className="text-center mb-4">
                    <span className="text-3xl font-bold text-white" style={{ fontFamily: 'Georgia, serif' }}>
                      {question.verb.infinitive}
                    </span>
                    <p className="text-white/70 mt-1">"{question.verb.english}"</p>
                  </div>
                  <div className="text-center text-sm bg-white/10 rounded-lg p-3">
                    <ConjugationPrompt 
                      tense={question.conjugation.tense}
                      mood={question.conjugation.mood}
                      voice={question.conjugation.voice}
                      number={question.conjugation.number}
                    />
                    <p className="text-white/50 text-xs mt-2">💡 Hover over underlined terms for definitions</p>
                  </div>
                </div>
              )}
            </div>

            {/* Answer input */}
            {!showResult ? (
              <div className="mb-6">
                {/* Flashcard Mode */}
                {answerMode === 'flashcard' ? (
                  <div className="text-center">
                    {!flashcardRevealed ? (
                      <>
                        <p className="text-slate-400 mb-4">Think of the answer, then reveal to check</p>
                        <button
                          onClick={() => setFlashcardRevealed(true)}
                          className="w-full py-4 bg-gradient-to-r from-purple-500 to-pink-500 text-white font-bold rounded-xl 
                            hover:from-purple-600 hover:to-pink-600 transition-all text-lg"
                        >
                          👁️ Reveal Answer
                        </button>
                      </>
                    ) : (
                      <>
                        <div className="bg-slate-700/50 rounded-xl p-6 mb-4">
                          <p className="text-slate-400 text-sm mb-2">Correct Answer:</p>
                          <p className="text-3xl font-bold text-white" style={{ fontFamily: 'Georgia, serif' }}>
                            {question.conjugation.form}
                          </p>
                        </div>
                        <p className="text-slate-400 mb-4">Did you get it right?</p>
                        <div className="grid grid-cols-2 gap-3">
                          <button
                            onClick={() => {
                              setIsCorrect(false);
                              setShowResult(true);
                              setFlashcardRevealed(false);
                              setPracticeStats(prev => ({
                                ...prev,
                                totalQuestions: prev.totalQuestions + 1,
                                streak: 0,
                                accuracy: Math.round((prev.correctAnswers / (prev.totalQuestions + 1)) * 100)
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
                              setPracticeStats(prev => ({
                                ...prev,
                                totalQuestions: prev.totalQuestions + 1,
                                correctAnswers: prev.correctAnswers + 1,
                                streak: prev.streak + 1,
                                maxStreak: Math.max(prev.maxStreak, prev.streak + 1),
                                accuracy: Math.round(((prev.correctAnswers + 1) / (prev.totalQuestions + 1)) * 100)
                              }));
                            }}
                            className="py-4 bg-emerald-500/20 border border-emerald-500 text-emerald-400 font-bold rounded-xl hover:bg-emerald-500/30 transition-all"
                          >
                            ✓ Correct
                          </button>
                        </div>
                      </>
                    )}
                  </div>
                ) : answerMode === 'multiple_choice' || (smartQuestion && smartQuestion.type === 'multiple_choice') ? (
                  // Multiple Choice Options
                  <div className="space-y-3">
                    {(smartQuestion?.options || [question.conjugation.form, 'γράφει', 'γράφουν', 'γράφουμε'].sort(() => Math.random() - 0.5)).map((option, index) => (
                      <button
                        key={index}
                        onClick={() => handleMultipleChoiceSelect(option)}
                        className={`w-full p-4 text-left rounded-xl border-2 transition-all ${
                          selectedMultipleChoice === option
                            ? 'border-purple-500 bg-purple-500/20 text-white'
                            : 'border-slate-600 bg-slate-700/50 text-slate-200 hover:border-slate-500'
                        }`}
                        style={{ fontFamily: 'Georgia, serif' }}
                      >
                        <span className="text-lg">{option}</span>
                      </button>
                    ))}
                    
                    <button
                      onClick={submitSmartAnswer}
                      disabled={!selectedMultipleChoice || loading}
                      className="w-full mt-4 py-4 bg-gradient-to-r from-purple-500 to-pink-500 text-white font-bold rounded-xl 
                        hover:from-purple-600 hover:to-pink-600 disabled:opacity-50 disabled:cursor-not-allowed transition-all"
                    >
                      {loading ? 'Checking...' : 'Submit Answer'}
                    </button>
                  </div>
                ) : (
            // Type Answer Mode
            <div>
              <GreekKeyboard
                value={userAnswer}
                onTextChange={setUserAnswer}
                placeholder="Type the conjugation in Greek..."
                showValidation={true}
                correctAnswer={smartQuestion ? smartQuestion.correct_answer : question.conjugation.form}
                autoTransliterate={true}
              />

              <button
                onClick={smartQuestion ? submitSmartAnswer : submitAnswer}
                disabled={!userAnswer.trim() || loading}
                className="w-full mt-4 py-4 bg-gradient-to-r from-purple-500 to-pink-500 text-white font-bold rounded-xl 
                  hover:from-purple-600 hover:to-pink-600 disabled:opacity-50 disabled:cursor-not-allowed transition-all"
              >
                {loading ? 'Checking...' : 'Submit Answer'}
              </button>
              
              <p className="text-slate-500 text-xs text-center mt-2">
                💡 Type in Latin (e.g., "grapho" → "γραφω") • Accents optional
              </p>
            </div>
          )}
        </div>
      ) : (
        /* Enhanced result display */
        <div className="mb-6">
          <div className={`p-4 rounded-lg mb-4 ${isCorrect ? 'bg-green-50 border-green-200' : 'bg-red-50 border-red-200'} border`}>
            <div className="flex items-center mb-3">
              <span className="text-2xl mr-2">{isCorrect ? '✅' : '❌'}</span>
              <span className={`font-bold ${isCorrect ? 'text-green-800' : 'text-red-800'}`}>
                {validationResult?.feedback || (isCorrect ? 'Correct!' : 'Incorrect')}
              </span>
            </div>

            <div className="space-y-2">
              <p><strong>Your answer:</strong> <span style={{ fontFamily: 'Georgia, "Times New Roman", serif' }}>{userAnswer}</span></p>
              {!isCorrect && (
                <p><strong>Correct answer:</strong> <span style={{ fontFamily: 'Georgia, "Times New Roman", serif' }}>{question.conjugation.form}</span></p>
              )}

              {/* Show similarity score and suggestions from enhanced validation */}
              {validationResult && (
                <div className="mt-3 pt-3 border-t border-gray-200">
                  {validationResult.similarity_score !== undefined && (
                    <p className="text-sm text-gray-600">
                      <strong>Similarity:</strong> {Math.round(validationResult.similarity_score * 100)}%
                    </p>
                  )}
                  {validationResult.suggestions && validationResult.suggestions.length > 0 && (
                    <div className="mt-2">
                      <p className="text-sm text-gray-600"><strong>Suggestions:</strong></p>
                      <ul className="text-sm text-gray-600 ml-4">
                        {validationResult.suggestions.map((suggestion, index) => (
                          <li key={index}>• {suggestion}</li>
                        ))}
                      </ul>
                    </div>
                  )}
                </div>
              )}
            </div>
          </div>

          <button
            onClick={nextQuestion}
            className="w-full py-4 bg-gradient-to-r from-purple-500 to-pink-500 text-white font-bold rounded-xl 
              hover:from-purple-600 hover:to-pink-600 transition-all"
          >
            {isEndlessMode ? 'Next Question →' : 'Continue →'}
          </button>
        </div>
      )}

            {/* Hints */}
            <div className="text-sm text-slate-400 bg-slate-700/50 p-4 rounded-xl mt-6">
              💡 <strong className="text-slate-300">Tip:</strong> Type in Latin characters (e.g., "grapho") for automatic Greek conversion.
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default PracticeSession;