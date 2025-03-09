import React, { useState, useEffect } from 'react';

const AdjectiveApp = ({ onBackToHome }) => {
  const [adjectiveData, setAdjectiveData] = useState({
    adjective: 'καλός',
    translation: 'good'
  });
  
  const [currentExample, setCurrentExample] = useState({
    noun: 'άνθρωπος',
    nounGender: 'αρσενικό',
    nounNumber: 'ενικός',
    nounCase: 'ονομαστική',
    correctForm: 'καλός'
  });
  
  const [userAnswer, setUserAnswer] = useState('');
  const [checked, setChecked] = useState(false);
  const [isCorrect, setIsCorrect] = useState(false);
  const [score, setScore] = useState(0);
  const [streak, setStreak] = useState(0);
  
  // Adjective database with full declensions
  const adjectives = [
    {
      adjective: 'καλός',
      translation: 'good',
      forms: {
        αρσενικό: {
          ενικός: {
            ονομαστική: 'καλός',
            γενική: 'καλού',
            αιτιατική: 'καλό'
          },
          πληθυντικός: {
            ονομαστική: 'καλοί',
            γενική: 'καλών',
            αιτιατική: 'καλούς'
          }
        },
        θηλυκό: {
          ενικός: {
            ονομαστική: 'καλή',
            γενική: 'καλής',
            αιτιατική: 'καλή'
          },
          πληθυντικός: {
            ονομαστική: 'καλές',
            γενική: 'καλών',
            αιτιατική: 'καλές'
          }
        },
        ουδέτερο: {
          ενικός: {
            ονομαστική: 'καλό',
            γενική: 'καλού',
            αιτιατική: 'καλό'
          },
          πληθυντικός: {
            ονομαστική: 'καλά',
            γενική: 'καλών',
            αιτιατική: 'καλά'
          }
        }
      }
    },
    {
      adjective: 'μεγάλος',
      translation: 'big',
      forms: {
        αρσενικό: {
          ενικός: {
            ονομαστική: 'μεγάλος',
            γενική: 'μεγάλου',
            αιτιατική: 'μεγάλο'
          },
          πληθυντικός: {
            ονομαστική: 'μεγάλοι',
            γενική: 'μεγάλων',
            αιτιατική: 'μεγάλους'
          }
        },
        θηλυκό: {
          ενικός: {
            ονομαστική: 'μεγάλη',
            γενική: 'μεγάλης',
            αιτιατική: 'μεγάλη'
          },
          πληθυντικός: {
            ονομαστική: 'μεγάλες',
            γενική: 'μεγάλων',
            αιτιατική: 'μεγάλες'
          }
        },
        ουδέτερο: {
          ενικός: {
            ονομαστική: 'μεγάλο',
            γενική: 'μεγάλου',
            αιτιατική: 'μεγάλο'
          },
          πληθυντικός: {
            ονομαστική: 'μεγάλα',
            γενική: 'μεγάλων',
            αιτιατική: 'μεγάλα'
          }
        }
      }
    },
    {
      adjective: 'ωραίος',
      translation: 'beautiful',
      forms: {
        αρσενικό: {
          ενικός: {
            ονομαστική: 'ωραίος',
            γενική: 'ωραίου',
            αιτιατική: 'ωραίο'
          },
          πληθυντικός: {
            ονομαστική: 'ωραίοι',
            γενική: 'ωραίων',
            αιτιατική: 'ωραίους'
          }
        },
        θηλυκό: {
          ενικός: {
            ονομαστική: 'ωραία',
            γενική: 'ωραίας',
            αιτιατική: 'ωραία'
          },
          πληθυντικός: {
            ονομαστική: 'ωραίες',
            γενική: 'ωραίων',
            αιτιατική: 'ωραίες'
          }
        },
        ουδέτερο: {
          ενικός: {
            ονομαστική: 'ωραίο',
            γενική: 'ωραίου',
            αιτιατική: 'ωραίο'
          },
          πληθυντικός: {
            ονομαστική: 'ωραία',
            γενική: 'ωραίων',
            αιτιατική: 'ωραία'
          }
        }
      }
    }
  ];
  
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
  
  const loadRandomAdjective = () => {
    // Select a random adjective
    const randomAdj = adjectives[Math.floor(Math.random() * adjectives.length)];
    
    // Select a random noun
    const randomNoun = nouns[Math.floor(Math.random() * nouns.length)];
    
    // Select random case and number
    const randomCase = cases[Math.floor(Math.random() * cases.length)];
    const randomNumber = numbers[Math.floor(Math.random() * numbers.length)];
    
    // Get the correct form of the adjective
    const correctForm = randomAdj.forms[randomNoun.gender][randomNumber][randomCase];
    
    setAdjectiveData({
      adjective: randomAdj.adjective,
      translation: randomAdj.translation
    });
    
    setCurrentExample({
      noun: randomNoun.noun,
      nounGender: randomNoun.gender,
      nounNumber: randomNumber,
      nounCase: randomCase,
      correctForm: correctForm
    });
    
    setUserAnswer('');
    setChecked(false);
  };
  
  useEffect(() => {
    loadRandomAdjective();
  }, []);
  
  const handleAnswerChange = (value) => {
    setUserAnswer(value);
  };
  
  const checkAnswer = () => {
    const isAnswerCorrect = userAnswer.trim().toLowerCase() === currentExample.correctForm.toLowerCase();
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
    loadRandomAdjective();
  };
  
  // Get the article for the noun based on gender, case, and number
  const getArticle = (gender, number, grammarCase) => {
    const articles = {
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
    
    return articles[gender][number][grammarCase];
  };
  
  return (
    <div className="flex flex-col items-center justify-center p-4 bg-gray-50 min-h-screen">
      <div className="w-full max-w-md">
        <header className="text-center mb-6">
          <h1 className="text-2xl font-bold text-blue-600">Ελληνική Γραμματική</h1>
          <p className="text-gray-600">Εξάσκηση στα Επίθετα</p>
        </header>
        
        <div className="bg-white shadow-lg rounded-lg overflow-hidden border">
          <div className="bg-blue-50 border-b pb-2 p-4">
            <div className="flex justify-between items-center">
              <div>
                <h2 className="text-xl font-bold text-blue-700">{adjectiveData.adjective} - {adjectiveData.translation}</h2>
                <p className="text-sm text-gray-600">
                  Συμφωνία επιθέτου με ουσιαστικό
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
              <p className="text-gray-700">Βρείτε τη σωστή μορφή του επιθέτου <span className="font-semibold">"{adjectiveData.adjective}"</span> για το ουσιαστικό:</p>
              <p className="mt-2 text-lg font-bold">
                {getArticle(currentExample.nounGender, currentExample.nounNumber, currentExample.nounCase)} {currentExample.noun}
                <span className="text-gray-500"> ({currentExample.nounGender})</span>
              </p>
              <p className="mt-1 text-sm text-gray-600">
                Πτώση: <span className="font-medium">{currentExample.nounCase}</span>, 
                Αριθμός: <span className="font-medium">{currentExample.nounNumber}</span>
              </p>
            </div>
            
            <div className="mt-6">
              <label className="block text-sm font-medium text-gray-700 mb-2">Η σωστή μορφή του επιθέτου είναι:</label>
              <div className="flex">
                <input
                  type="text"
                  value={userAnswer}
                  onChange={(e) => handleAnswerChange(e.target.value)}
                  className="flex-1 p-2 border rounded focus:outline-none focus:ring-2 focus:ring-blue-500"
                  disabled={checked}
                  placeholder="Γράψτε τη σωστή μορφή"
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
                        <span className="text-sm text-gray-600">{currentExample.correctForm}</span>
                      </div>
                    )}
                  </div>
                )}
              </div>
              
              {checked && !isCorrect && (
                <p className="mt-3 text-sm text-gray-600">
                  Η σωστή μορφή είναι: <span className="font-semibold">{currentExample.correctForm}</span>
                </p>
              )}
              
              {checked && isCorrect && (
                <p className="mt-3 text-sm text-green-600">
                  Μπράβο! Η απάντησή σας είναι σωστή!
                </p>
              )}
              
              {checked && (
                <div className="mt-4 p-3 bg-gray-50 rounded border">
                  <p className="text-sm">
                    Η πλήρης φράση είναι: <span className="font-medium">
                      {getArticle(currentExample.nounGender, currentExample.nounNumber, currentExample.nounCase)} {currentExample.correctForm} {currentExample.noun}
                    </span>
                  </p>
                </div>
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
          <h3 className="font-semibold text-gray-700 mb-2">Πίνακας Καταλήξεων των Επιθέτων σε -ος, -η/-α, -ο</h3>
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead>
                <tr>
                  <th className="px-2 py-2 text-left text-xs font-medium text-gray-500 uppercase">Γένος</th>
                  <th className="px-2 py-2 text-left text-xs font-medium text-gray-500 uppercase">Αριθμός</th>
                  <th className="px-2 py-2 text-left text-xs font-medium text-gray-500 uppercase">Ονομαστική</th>
                  <th className="px-2 py-2 text-left text-xs font-medium text-gray-500 uppercase">Γενική</th>
                  <th className="px-2 py-2 text-left text-xs font-medium text-gray-500 uppercase">Αιτιατική</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-200 text-sm">
                <tr className="bg-gray-50">
                  <td className="px-2 py-1 font-medium" rowSpan="2">Αρσενικό</td>
                  <td className="px-2 py-1">Ενικός</td>
                  <td className="px-2 py-1">-ος</td>
                  <td className="px-2 py-1">-ου</td>
                  <td className="px-2 py-1">-ο</td>
                </tr>
                <tr className="bg-gray-50">
                  <td className="px-2 py-1">Πληθυντικός</td>
                  <td className="px-2 py-1">-α</td>
                  <td className="px-2 py-1">-ων</td>
                  <td className="px-2 py-1">-α</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  );
};

export default AdjectiveApp; 