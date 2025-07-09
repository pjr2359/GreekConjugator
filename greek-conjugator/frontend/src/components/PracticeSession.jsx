import React, { useState, useEffect } from 'react';
import GreekKeyboard, { compareGreekTexts } from './GreekKeyboard';
import { verbsService, textValidationService } from '../services/api';

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
  const [validationResult, setValidationResult] = useState(null);
  const [showHints, setShowHints] = useState(false);
  const [currentQuestion, setCurrentQuestion] = useState(null);

  // Start a new practice session
  const startSession = async (sessionType = 'graded', difficulty = 1) => {
    setLoading(true);
    try {
      const session = await verbsService.startPracticeSession(sessionType, difficulty, 5);
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

    // Check if we've completed enough questions (let's say 5 questions per session)
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
  };

  // Start session on component mount
  useEffect(() => {
    if (user && !sessionData) {
      startSession(); // Start session automatically when component loads
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
            showValidation={true}
            correctAnswer={question.conjugation.form}
            autoTransliterate={true}
          />

          <div className="flex justify-center gap-4 mt-4">
            <button
              onClick={submitAnswer}
              disabled={!userAnswer.trim() || loading}
              className="bg-blue-600 text-white py-3 px-8 rounded-lg hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed transition-colors flex items-center gap-2"
            >
              {loading && <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>}
              Submit Answer
            </button>

            <button
              onClick={() => setShowHints(!showHints)}
              className="bg-gray-500 text-white py-3 px-6 rounded-lg hover:bg-gray-600 transition-colors"
            >
              {showHints ? 'Hide Hints' : 'Show Hints'}
            </button>
          </div>

          {/* Enhanced hints section */}
          {showHints && (
            <div className="mt-4 p-4 bg-blue-50 rounded-lg border border-blue-200">
              <h4 className="font-semibold text-blue-800 mb-2">💡 Hints:</h4>
              <ul className="text-sm text-blue-700 space-y-1">
                <li>• <strong>Tense:</strong> {question.conjugation.tense}</li>
                <li>• <strong>Mood:</strong> {question.conjugation.mood}</li>
                <li>• <strong>Voice:</strong> {question.conjugation.voice}</li>
                <li>• <strong>Person:</strong> {question.conjugation.person}</li>
                <li>• <strong>Number:</strong> {question.conjugation.number}</li>
                <li>• You can type Latin characters (e.g., "grapho" → "γραφω")</li>
                <li>• Accents are optional for matching - focus on the base letters first</li>
              </ul>
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