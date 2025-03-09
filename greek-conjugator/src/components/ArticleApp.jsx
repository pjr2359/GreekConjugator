import React, { useState, useEffect } from 'react';

const ArticleApp = ({ onBackToHome }) => {
  const [currentQuestion, setCurrentQuestion] = useState({
    noun: '',
    gender: '',
    type: '',
    case: '',
    number: '',
    article: ''
  });
  
  const [userAnswer, setUserAnswer] = useState('');
  const [checked, setChecked] = useState(false);
  const [isCorrect, setIsCorrect] = useState(false);
  const [score, setScore] = useState(0);
  const [streak, setStreak] = useState(0);
  
  // Greek article data
  const definiteArticles = {
    // Masculine
    αρσενικό: {
      ενικός: {
        ονομαστική: 'ο',
        γενική: 'του',
        αιτιατική: 'τον',
      },
      πληθυντικός: {
        ονομαστική: 'οι',
        γενική: 'των',
        αιτιατική: 'τους',
      }
    },
    // Feminine
    θηλυκό: {
      ενικός: {
        ονομαστική: 'η',
        γενική: 'της',
        αιτιατική: 'την',
      },
      πληθυντικός: {
        ονομαστική: 'οι',
        γενική: 'των',
        αιτιατική: 'τις',
      }
    },
    // Neuter
    ουδέτερο: {
      ενικός: {
        ονομαστική: 'το',
        γενική: 'του',
        αιτιατική: 'το',
      },
      πληθυντικός: {
        ονομαστική: 'τα',
        γενική: 'των',
        αιτιατική: 'τα',
      }
    }
  };
  
  const indefiniteArticles = {
    // Masculine
    αρσενικό: {
      ενικός: {
        ονομαστική: 'ένας',
        γενική: 'ενός',
        αιτιατική: 'έναν',
      },
      πληθυντικός: {
        ονομαστική: '-',
        γενική: '-',
        αιτιατική: '-',
      }
    },
    // Feminine
    θηλυκό: {
      ενικός: {
        ονομαστική: 'μία',
        γενική: 'μίας',
        αιτιατική: 'μία',
      },
      πληθυντικός: {
        ονομαστική: '-',
        γενική: '-',
        αιτιατική: '-',
      }
    },
    // Neuter
    ουδέτερο: {
      ενικός: {
        ονομαστική: 'ένα',
        γενική: 'ενός',
        αιτιατική: 'ένα',
      },
      πληθυντικός: {
        ονομαστική: '-',
        γενική: '-',
        αιτιατική: '-',
      }
    }
  };
  
  // Sample nouns for practice
  const nouns = [
    { noun: 'άνθρωπος', gender: 'αρσενικό' },
    { noun: 'γυναίκα', gender: 'θηλυκό' },
    { noun: 'παιδί', gender: 'ουδέτερο' },
    { noun: 'πόλη', gender: 'θηλυκό' },
    { noun: 'σπίτι', gender: 'ουδέτερο' },
    { noun: 'δρόμος', gender: 'αρσενικό' },
    { noun: 'θάλασσα', gender: 'θηλυκό' },
    { noun: 'βιβλίο', gender: 'ουδέτερο' }
  ];
  
  const cases = ['ονομαστική', 'γενική', 'αιτιατική'];
  const numbers = ['ενικός', 'πληθυντικός'];
  const types = ['οριστικό', 'αόριστο'];
  
  const generateQuestion = () => {
    // Select a random noun
    const randomNoun = nouns[Math.floor(Math.random() * nouns.length)];
    
    // Select random case, number, and article type
    const randomCase = cases[Math.floor(Math.random() * cases.length)];
    const randomNumber = numbers[Math.floor(Math.random() * numbers.length)];
    const randomType = types[Math.floor(Math.random() * types.length)];
    
    // Skip indefinite articles for plural (they don't exist in Greek)
    if (randomType === 'αόριστο' && randomNumber === 'πληθυντικός') {
      // Try again with a different type or number
      return generateQuestion();
    }
    
    // Get the correct article
    const articlesSource = randomType === 'οριστικό' ? definiteArticles : indefiniteArticles;
    const correctArticle = articlesSource[randomNoun.gender][randomNumber][randomCase];
    
    return {
      noun: randomNoun.noun,
      gender: randomNoun.gender,
      type: randomType,
      case: randomCase,
      number: randomNumber,
      article: correctArticle
    };
  };
  
  const loadNewQuestion = () => {
    const newQuestion = generateQuestion();
    setCurrentQuestion(newQuestion);
    setUserAnswer('');
    setChecked(false);
  };
  
  useEffect(() => {
    loadNewQuestion();
  }, []);
  
  const handleAnswerChange = (value) => {
    setUserAnswer(value);
  };
  
  const checkAnswer = () => {
    const isAnswerCorrect = userAnswer.trim().toLowerCase() === currentQuestion.article.toLowerCase();
    setIsCorrect(isAnswerCorrect);
    setChecked(true);
    
    if (isAnswerCorrect) {
      setStreak(streak + 1);
      setScore(score + 1 + Math.floor(streak / 3)); // Small bonus for streaks
    } else {
      setStreak(0);
    }
  };
  
  const nextQuestion = () => {
    loadNewQuestion();
  };
  
  return (
    <div className="flex flex-col items-center justify-center p-4 bg-gray-50 min-h-screen">
      <div className="w-full max-w-md">
        <header className="text-center mb-6">
          <h1 className="text-2xl font-bold text-blue-600">Ελληνική Γραμματική</h1>
          <p className="text-gray-600">Εξάσκηση στα Άρθρα</p>
        </header>
        
        <div className="bg-white shadow-lg rounded-lg overflow-hidden border">
          <div className="bg-blue-50 border-b pb-2 p-4">
            <div className="flex justify-between items-center">
              <div>
                <h2 className="text-xl font-bold text-blue-700">Άρθρα</h2>
                <p className="text-sm text-gray-600">
                  Οριστικά και Αόριστα
                </p>
              </div>
              <div className="text-right">
                <p className="text-sm font-semibold">Σκορ: {score}</p>
                <p className="text-xs">Σερί: {streak}</p>
              </div>
            </div>
          </div>
          
          <div className="p-6">
            <div className="mb-4 p-4 bg-blue-50 rounded-lg">
              <p className="text-gray-700">Βρείτε το σωστό <span className="font-semibold">{currentQuestion.type}</span> άρθρο για το ουσιαστικό:</p>
              <p className="mt-2 text-lg font-bold">"{currentQuestion.noun}" <span className="text-gray-500">({currentQuestion.gender})</span></p>
              <p className="mt-1 text-sm text-gray-600">
                Πτώση: <span className="font-medium">{currentQuestion.case}</span>, 
                Αριθμός: <span className="font-medium">{currentQuestion.number}</span>
              </p>
            </div>
            
            <div className="mt-6">
              <label className="block text-sm font-medium text-gray-700 mb-2">Το σωστό άρθρο είναι:</label>
              <div className="flex">
                <input
                  type="text"
                  value={userAnswer}
                  onChange={(e) => handleAnswerChange(e.target.value)}
                  className="flex-1 p-2 border rounded focus:outline-none focus:ring-2 focus:ring-blue-500"
                  disabled={checked}
                  placeholder="Γράψτε το άρθρο"
                />
                
                {checked && (
                  <div className="ml-3 flex items-center">
                    {isCorrect ? (
                      <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="h-6 w-6 text-green-500">
                        <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"></path>
                        <polyline points="22 4 12 14.01 9 11.01"></polyline>
                      </svg>
                    ) : (
                      <div className="flex items-center">
                        <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="h-6 w-6 text-red-500 mr-2">
                          <circle cx="12" cy="12" r="10"></circle>
                          <line x1="15" y1="9" x2="9" y2="15"></line>
                          <line x1="9" y1="9" x2="15" y2="15"></line>
                        </svg>
                        <span className="text-sm text-gray-600">{currentQuestion.article}</span>
                      </div>
                    )}
                  </div>
                )}
              </div>
              
              {checked && !isCorrect && (
                <p className="mt-3 text-sm text-gray-600">
                  Το σωστό άρθρο είναι: <span className="font-semibold">{currentQuestion.article}</span>
                </p>
              )}
              
              {checked && isCorrect && (
                <p className="mt-3 text-sm text-green-600">
                  Μπράβο! Η απάντησή σας είναι σωστή!
                </p>
              )}
            </div>
          </div>
          
          <div className="bg-gray-50 border-t p-4 flex justify-between">
            {!checked ? (
              <button onClick={checkAnswer} className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700">
                Έλεγχος
              </button>
            ) : (
              <button onClick={nextQuestion} className="bg-green-600 text-white px-4 py-2 rounded hover:bg-green-700 flex items-center">
                <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="mr-2 h-4 w-4">
                  <polygon points="5 4 15 12 5 20 5 4"></polygon>
                  <line x1="19" y1="5" x2="19" y2="19"></line>
                </svg>
                Επόμενο
              </button>
            )}
            
            <button onClick={onBackToHome} className="text-gray-700 px-4 py-2 rounded hover:bg-gray-200">
              Επιστροφή
            </button>
          </div>
        </div>
        
        <div className="mt-4 bg-white p-4 rounded-lg shadow border">
          <h3 className="font-semibold text-gray-700 mb-2">Πίνακας Άρθρων</h3>
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead>
                <tr>
                  <th className="px-2 py-2 text-left text-xs font-medium text-gray-500 uppercase">Γένος</th>
                  <th className="px-2 py-2 text-left text-xs font-medium text-gray-500 uppercase">Αριθμός</th>
                  <th className="px-2 py-2 text-left text-xs font-medium text-gray-500 uppercase">Πτώση</th>
                  <th className="px-2 py-2 text-left text-xs font-medium text-gray-500 uppercase">Οριστικό</th>
                  <th className="px-2 py-2 text-left text-xs font-medium text-gray-500 uppercase">Αόριστο</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-200 text-sm">
                {['αρσενικό', 'θηλυκό', 'ουδέτερο'].map(gender => 
                  ['ενικός', 'πληθυντικός'].map(number => 
                    ['ονομαστική', 'γενική', 'αιτιατική'].map((grammarCase, idx) => (
                      <tr key={`${gender}-${number}-${grammarCase}`} className={idx % 2 === 0 ? 'bg-gray-50' : 'bg-white'}>
                        <td className="px-2 py-1">{idx === 0 ? gender : ''}</td>
                        <td className="px-2 py-1">{idx === 0 ? number : ''}</td>
                        <td className="px-2 py-1">{grammarCase}</td>
                        <td className="px-2 py-1 font-medium">{definiteArticles[gender][number][grammarCase]}</td>
                        <td className="px-2 py-1 font-medium">
                          {indefiniteArticles[gender][number][grammarCase]}
                        </td>
                      </tr>
                    ))
                  )
                )}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ArticleApp;