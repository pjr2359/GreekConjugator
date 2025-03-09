import React, { useState, useEffect } from 'react';

const NounDeclinationApp = ({ settings, onBackToHome }) => {
  const [nounData, setNounData] = useState({
    noun: 'άνθρωπος',
    translation: 'human, person',
    gender: 'αρσενικό',
    group: 'Α'
  });
  
  const [userAnswers, setUserAnswers] = useState({
    ονομαστική_ενικός: '',
    γενική_ενικός: '',
    αιτιατική_ενικός: '',
    κλητική_ενικός: '',
    ονομαστική_πληθυντικός: '',
    γενική_πληθυντικός: '',
    αιτιατική_πληθυντικός: '',
    κλητική_πληθυντικός: ''
  });
  
  const [correctAnswers, setCorrectAnswers] = useState({
    ονομαστική_ενικός: 'ο άνθρωπος',
    γενική_ενικός: 'του ανθρώπου',
    αιτιατική_ενικός: 'τον άνθρωπο',
    κλητική_ενικός: 'άνθρωπε',
    ονομαστική_πληθυντικός: 'οι άνθρωποι',
    γενική_πληθυντικός: 'των ανθρώπων',
    αιτιατική_πληθυντικός: 'τους ανθρώπους',
    κλητική_πληθυντικός: 'άνθρωποι'
  });
  
  const [checked, setChecked] = useState(false);
  const [score, setScore] = useState(0);
  const [streak, setStreak] = useState(0);
  
  // Greek nouns database
  const nouns = [
    {
      noun: 'άνθρωπος',
      translation: 'human, person',
      gender: 'αρσενικό',
      group: 'Α',
      declination: {
        ονομαστική_ενικός: 'ο άνθρωπος',
        γενική_ενικός: 'του ανθρώπου',
        αιτιατική_ενικός: 'τον άνθρωπο',
        κλητική_ενικός: 'άνθρωπε',
        ονομαστική_πληθυντικός: 'οι άνθρωποι',
        γενική_πληθυντικός: 'των ανθρώπων',
        αιτιατική_πληθυντικός: 'τους ανθρώπους',
        κλητική_πληθυντικός: 'άνθρωποι'
      }
    },
    {
      noun: 'γυναίκα',
      translation: 'woman',
      gender: 'θηλυκό',
      group: 'Α',
      declination: {
        ονομαστική_ενικός: 'η γυναίκα',
        γενική_ενικός: 'της γυναίκας',
        αιτιατική_ενικός: 'τη γυναίκα',
        κλητική_ενικός: 'γυναίκα',
        ονομαστική_πληθυντικός: 'οι γυναίκες',
        γενική_πληθυντικός: 'των γυναικών',
        αιτιατική_πληθυντικός: 'τις γυναίκες',
        κλητική_πληθυντικός: 'γυναίκες'
      }
    },
    {
      noun: 'παιδί',
      translation: 'child',
      gender: 'ουδέτερο',
      group: 'Β',
      declination: {
        ονομαστική_ενικός: 'το παιδί',
        γενική_ενικός: 'του παιδιού',
        αιτιατική_ενικός: 'το παιδί',
        κλητική_ενικός: 'παιδί',
        ονομαστική_πληθυντικός: 'τα παιδιά',
        γενική_πληθυντικός: 'των παιδιών',
        αιτιατική_πληθυντικός: 'τα παιδιά',
        κλητική_πληθυντικός: 'παιδιά'
      }
    },
    {
      noun: 'πόλη',
      translation: 'city',
      gender: 'θηλυκό',
      group: 'Β',
      declination: {
        ονομαστική_ενικός: 'η πόλη',
        γενική_ενικός: 'της πόλης',
        αιτιατική_ενικός: 'την πόλη',
        κλητική_ενικός: 'πόλη',
        ονομαστική_πληθυντικός: 'οι πόλεις',
        γενική_πληθυντικός: 'των πόλεων',
        αιτιατική_πληθυντικός: 'τις πόλεις',
        κλητική_πληθυντικός: 'πόλεις'
      }
    },
    {
      noun: 'σπίτι',
      translation: 'house',
      gender: 'ουδέτερο',
      group: 'Α',
      declination: {
        ονομαστική_ενικός: 'το σπίτι',
        γενική_ενικός: 'του σπιτιού',
        αιτιατική_ενικός: 'το σπίτι',
        κλητική_ενικός: 'σπίτι',
        ονομαστική_πληθυντικός: 'τα σπίτια',
        γενική_πληθυντικός: 'των σπιτιών',
        αιτιατική_πληθυντικός: 'τα σπίτια',
        κλητική_πληθυντικός: 'σπίτια'
      }
    }
  ];
  
  const filterNounsBySettings = () => {
    return nouns.filter(noun => {
      // Skip filtering if "all" is selected
      const caseMatch = settings.case === 'all'; // Case filtering is handled in renderForm()
      const numberMatch = settings.number === 'all'; // Number filtering is handled in renderForm()
      const genderMatch = settings.gender === 'all' || noun.gender === settings.gender;
      
      return caseMatch && numberMatch && genderMatch;
    });
  };
  
  const loadRandomNoun = () => {
    const filteredNouns = filterNounsBySettings();
    
    // If no nouns match the filter, use all nouns
    const nounsToUse = filteredNouns.length ? filteredNouns : nouns;
    
    const randomIndex = Math.floor(Math.random() * nounsToUse.length);
    const newNoun = nounsToUse[randomIndex];
    
    setNounData({
      noun: newNoun.noun,
      translation: newNoun.translation,
      gender: newNoun.gender,
      group: newNoun.group
    });
    
    setCorrectAnswers(newNoun.declination);
    
    // Reset user answers
    const emptyAnswers = {};
    Object.keys(newNoun.declination).forEach(key => {
      emptyAnswers[key] = '';
    });
    setUserAnswers(emptyAnswers);
    
    setChecked(false);
  };
  
  useEffect(() => {
    loadRandomNoun();
  }, []);
  
  const handleInputChange = (caseNumber, value) => {
    setUserAnswers(prev => ({
      ...prev,
      [caseNumber]: value
    }));
  };
  
  const checkAnswers = () => {
    setChecked(true);
    let correct = 0;
    let total = 0;
    
    // Only check the cases that are displayed based on settings
    Object.keys(userAnswers).forEach(caseNumber => {
      // Skip if this case/number is not being displayed
      if (shouldShowField(caseNumber)) {
        total++;
        if (userAnswers[caseNumber].trim().toLowerCase() === correctAnswers[caseNumber].trim().toLowerCase()) {
          correct++;
        }
      }
    });
    
    if (correct === total && total > 0) {
      setStreak(streak + 1);
      setScore(score + 5 + (streak * 2)); // Bonus for streaks
    } else {
      setStreak(0);
      setScore(score + correct);
    }
    
    return correct;
  };
  
  const nextQuestion = () => {
    loadRandomNoun();
  };
  
  // Helper to determine if a field should be shown based on settings
  const shouldShowField = (caseNumber) => {
    const [caseType, number] = caseNumber.split('_');
    
    const caseMatch = settings.case === 'all' || settings.case === caseType;
    const numberMatch = settings.number === 'all' || settings.number === number;
    
    return caseMatch && numberMatch;
  };
  
  // Render only the fields that match the current settings
  const renderForm = () => {
    const fields = [];
    
    // Define our case and number options
    const caseTypes = ['ονομαστική', 'γενική', 'αιτιατική', 'κλητική'];
    const numbers = ['ενικός', 'πληθυντικός'];
    
    // Create a form field for each combination that should be shown
    caseTypes.forEach(caseType => {
      numbers.forEach(number => {
        const caseNumber = `${caseType}_${number}`;
        
        if (shouldShowField(caseNumber)) {
          fields.push(
            <div key={caseNumber} className="flex items-center mb-3">
              <label className="w-1/3 font-medium text-gray-700">
                {caseType} ({number})
              </label>
              <div className="w-2/3 flex">
                <input
                  type="text"
                  value={userAnswers[caseNumber]}
                  onChange={(e) => handleInputChange(caseNumber, e.target.value)}
                  className="flex-1 p-2 border rounded focus:outline-none focus:ring-2 focus:ring-blue-500"
                  disabled={checked}
                  placeholder={`π.χ. ${correctAnswers[caseNumber].split(' ')[0] || ''}`}
                />
                {checked && (
                  <div className="ml-2">
                    {userAnswers[caseNumber].trim().toLowerCase() === correctAnswers[caseNumber].trim().toLowerCase() ? (
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
                        <span className="text-sm text-gray-600">{correctAnswers[caseNumber]}</span>
                      </div>
                    )}
                  </div>
                )}
              </div>
            </div>
          );
        }
      });
    });
    
    return fields;
  };
  
  return (
    <div className="flex flex-col items-center justify-center p-4 bg-gray-50 min-h-screen">
      <div className="w-full max-w-md">
        <header className="text-center mb-6">
          <h1 className="text-2xl font-bold text-blue-600">Ελληνική Γραμματική</h1>
          <p className="text-gray-600">Εξάσκηση στα Ουσιαστικά</p>
        </header>
        
        <div className="bg-white shadow-lg rounded-lg overflow-hidden border">
          <div className="bg-blue-50 border-b pb-2 p-4">
            <div className="flex justify-between items-center">
              <div>
                <h2 className="text-xl font-bold text-blue-700">{nounData.noun} - {nounData.translation}</h2>
                <p className="text-sm text-gray-600">
                  {nounData.gender} • Ομάδα {nounData.group}
                </p>
              </div>
              <div className="text-right">
                <p className="text-sm font-semibold">Σκορ: {score}</p>
                <p className="text-xs">Σερί: {streak}</p>
              </div>
            </div>
          </div>
          
          <div className="p-6">
            <div className="grid grid-cols-1 gap-2">
              {renderForm()}
            </div>
          </div>
          
          <div className="bg-gray-50 border-t p-4 flex justify-between">
            {!checked ? (
              <button onClick={checkAnswers} className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700">
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
      </div>
    </div>
  );
};

export default NounDeclinationApp;