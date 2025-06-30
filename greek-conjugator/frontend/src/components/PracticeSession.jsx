import React, { useState, useEffect } from 'react';
import GreekKeyboard from './GreekKeyboard';
import { verbsService } from '../services/api';

const PracticeSession = ({ user }) => {
  const [sessionData, setSessionData] = useState(null);
  const [currentQuestionIndex, setCurrentQuestionIndex] = useState(0);
  const [userAnswer, setUserAnswer] = useState('');
  const [showResult, setShowResult] = useState(false);
  const [isCorrect, setIsCorrect] = useState(false);
  const [score, setScore] = useState({ correct: 0, total: 0 });
  const [loading, setLoading] = useState(false);
  const [sessionComplete, setSessionComplete] = useState(false);
  const [conjugations, setConjugations] = useState({});

  // Start a new practice session
  const startSession = async (sessionType = 'graded', difficulty = 1) => {
    setLoading(true);
    try {
      const session = await verbsService.startPracticeSession(sessionType, difficulty, 10);
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

    // Pick a random conjugation for this question
    const randomConjugation = verbConjugations[Math.floor(Math.random() * verbConjugations.length)];

    return {
      verb,
      conjugation: randomConjugation,
      prompt: `Conjugate "${verb.infinitive}" (${verb.english}) in ${randomConjugation.tense} tense, ${randomConjugation.mood} mood, ${randomConjugation.person} person ${randomConjugation.number}`
    };
  };

  // Check if answer is correct
  const checkAnswer = (userInput, correctAnswer) => {
    // Remove accents and normalize for comparison
    const normalize = (text) => {
      return text.toLowerCase()
        .trim()
        .replace(/[άἀἁἂἃἄἅἆἇᾀᾁᾂᾃᾄᾅᾆᾇᾲᾳᾴᾶᾷ]/g, 'α')
        .replace(/[έἐἑἒἓἔἕ]/g, 'ε')
        .replace(/[ήἠἡἢἣἤἥἦἧᾐᾑᾒᾓᾔᾕᾖᾗῂῃῄῆῇ]/g, 'η')
        .replace(/[ίἰἱἲἳἴἵἶἷῐῑῒΐῖῗ]/g, 'ι')
        .replace(/[όὀὁὂὃὄὅ]/g, 'ο')
        .replace(/[ύὐὑὒὓὔὕὖὗῠῡῢΰῦῧ]/g, 'υ')
        .replace(/[ώὠὡὢὣὤὥὦὧᾠᾡᾢᾣᾤᾥᾦᾧῲῳῴῶῷ]/g, 'ω');
    };

    return normalize(userInput) === normalize(correctAnswer);
  };

  // Submit answer
  const submitAnswer = async () => {
    const question = getCurrentQuestion();
    if (!question) return;

    const correct = checkAnswer(userAnswer, question.conjugation.form);
    setIsCorrect(correct);
    setShowResult(true);

    // Update score
    const newScore = {
      correct: score.correct + (correct ? 1 : 0),
      total: score.total + 1
    };
    setScore(newScore);

    // Submit to backend
    try {
      await verbsService.submitAnswer(
        sessionData.session_id,
        question.conjugation.id,
        userAnswer,
        correct
      );
    } catch (error) {
      console.error('Failed to submit answer:', error);
    }
  };

  // Move to next question
  const nextQuestion = () => {
    setShowResult(false);
    setUserAnswer('');

    if (currentQuestionIndex + 1 >= sessionData.verbs.length) {
      setSessionComplete(true);
    } else {
      setCurrentQuestionIndex(currentQuestionIndex + 1);
    }
  };

  // Start session on component mount
  useEffect(() => {
    if (user && !sessionData) {
      // startSession(); // Prevent automatic session start
    }
  }, [user, sessionData]);

  const question = getCurrentQuestion();

  if (loading || !sessionData) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="animate-spin rounded-full h-16 w-16 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  if (sessionComplete) {
    const accuracy = Math.round((score.correct / score.total) * 100);
    return (
      <div className="max-w-2xl mx-auto p-6 bg-white rounded-lg shadow-lg">
        <div className="text-center">
          <h2 className="text-3xl font-bold text-gray-800 mb-4">Session Complete! 🎉</h2>
          <div className="text-6xl mb-4">{accuracy >= 80 ? '🏆' : accuracy >= 60 ? '👏' : '💪'}</div>
          <p className="text-xl text-gray-600 mb-6">
            You scored {score.correct} out of {score.total} ({accuracy}%)
          </p>

          <div className="space-y-4">
            <button
              onClick={() => startSession('graded', 1)}
              className="w-full bg-blue-600 text-white py-3 px-6 rounded-lg hover:bg-blue-700 transition-colors"
            >
              Start New Session
            </button>
            <button
              onClick={() => startSession('flashcards', 1)}
              className="w-full bg-green-600 text-white py-3 px-6 rounded-lg hover:bg-green-700 transition-colors"
            >
              Try Flashcard Mode
            </button>
          </div>
        </div>
      </div>
    );
  }

  if (!question) {
    return (
      <div className="max-w-2xl mx-auto p-6 bg-white rounded-lg shadow-lg">
        <div className="text-center">
          <h2 className="text-2xl font-bold text-gray-800 mb-4">Loading Question...</h2>
          <button
            onClick={() => startSession()}
            className="bg-blue-600 text-white py-2 px-4 rounded hover:bg-blue-700"
          >
            Start Practice Session
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-2xl mx-auto p-6 bg-white rounded-lg shadow-lg">
      {/* Progress bar */}
      <div className="mb-6">
        <div className="flex justify-between text-sm text-gray-600 mb-2">
          <span>Question {currentQuestionIndex + 1} of {sessionData?.verbs.length || 0}</span>
          <span>Score: {score.correct}/{score.total}</span>
        </div>
        <div className="w-full bg-gray-200 rounded-full h-2">
          <div
            className="bg-blue-600 h-2 rounded-full transition-all duration-300"
            style={{ width: `${((currentQuestionIndex + 1) / (sessionData?.verbs.length || 1)) * 100}%` }}
          ></div>
        </div>
      </div>

      {/* Question */}
      <div className="mb-6">
        <h2 className="text-2xl font-bold text-gray-800 mb-2">
          Conjugate the Verb
        </h2>
        <div className="bg-blue-50 p-4 rounded-lg mb-4">
          <p className="text-lg text-gray-700">
            {question.prompt}
          </p>
        </div>

        <div className="text-center mb-4">
          <span className="text-3xl font-bold text-blue-600" style={{ fontFamily: 'Georgia, "Times New Roman", serif' }}>
            {question.verb.infinitive}
          </span>
          <p className="text-gray-600 mt-1">{question.verb.english}</p>
        </div>
      </div>

      {/* Answer input */}
      {!showResult ? (
        <div className="mb-6">
          <GreekKeyboard
            value={userAnswer}
            onTextChange={setUserAnswer}
            placeholder="Type your answer..."
          />

          <div className="mt-4 text-center">
            <button
              onClick={submitAnswer}
              disabled={!userAnswer.trim()}
              className="bg-blue-600 text-white py-3 px-8 rounded-lg hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed transition-colors"
            >
              Submit Answer
            </button>
          </div>
        </div>
      ) : (
        /* Result display */
        <div className="mb-6">
          <div className={`p-4 rounded-lg mb-4 ${isCorrect ? 'bg-green-50 border-green-200' : 'bg-red-50 border-red-200'} border`}>
            <div className="flex items-center mb-2">
              <span className="text-2xl mr-2">{isCorrect ? '✅' : '❌'}</span>
              <span className={`font-bold ${isCorrect ? 'text-green-800' : 'text-red-800'}`}>
                {isCorrect ? 'Correct!' : 'Incorrect'}
              </span>
            </div>

            <div className="space-y-2">
              <p><strong>Your answer:</strong> <span style={{ fontFamily: 'Georgia, "Times New Roman", serif' }}>{userAnswer}</span></p>
              {!isCorrect && (
                <p><strong>Correct answer:</strong> <span style={{ fontFamily: 'Georgia, "Times New Roman", serif' }}>{question.conjugation.form}</span></p>
              )}
            </div>
          </div>

          <div className="text-center">
            <button
              onClick={nextQuestion}
              className="bg-blue-600 text-white py-3 px-8 rounded-lg hover:bg-blue-700 transition-colors"
            >
              {currentQuestionIndex + 1 >= sessionData.verbs.length ? 'Finish Session' : 'Next Question'}
            </button>
          </div>
        </div>
      )}

      {/* Hints */}
      <div className="text-sm text-gray-600 bg-gray-50 p-3 rounded">
        💡 <strong>Tip:</strong> You can type in Latin characters (e.g., "grapho") and they'll be converted to Greek automatically.
      </div>
    </div>
  );
};

export default PracticeSession;