import React, { useState, useEffect } from 'react';

const GreekConjugationApp = () => {
  const [mode, setMode] = useState('practice'); // 'practice' or 'story'
  const [verbData, setVerbData] = useState({
    verb: 'γράφω',
    translation: 'to write',
    tense: 'ενεστώτας', // present tense
    type: 'ενεργητική φωνή', // active voice
    group: 'A'
  });
  
  const [userAnswers, setUserAnswers] = useState({
    εγώ: '',
    εσύ: '',
    αυτός: '',
    εμείς: '',
    εσείς: '',
    αυτοί: ''
  });
  
  const [correctAnswers, setCorrectAnswers] = useState({
    εγώ: 'γράφω',
    εσύ: 'γράφεις',
    αυτός: 'γράφει',
    εμείς: 'γράφουμε',
    εσείς: 'γράφετε',
    αυτοί: 'γράφουν'
  });
  
  const [checked, setChecked] = useState(false);
  const [score, setScore] = useState(0);
  const [streak, setStreak] = useState(0);
  
  // For story mode
  const [storyContext, setStoryContext] = useState(
    'Ο Γιώργος και η Μαρία πηγαίνουν στην αγορά. Εκεί, ο Γιώργος ___ (γράφω) ένα μήνυμα στο κινητό του.'
  );
  
  const verbs = [
    {
      verb: 'γράφω',
      translation: 'to write',
      tense: 'ενεστώτας',
      type: 'ενεργητική φωνή',
      group: 'A',
      conjugation: {
        εγώ: 'γράφω',
        εσύ: 'γράφεις',
        αυτός: 'γράφει',
        εμείς: 'γράφουμε',
        εσείς: 'γράφετε',
        αυτοί: 'γράφουν'
      }
    },
    {
      verb: 'μιλάω',
      translation: 'to speak',
      tense: 'ενεστώτας',
      type: 'ενεργητική φωνή',
      group: 'A',
      conjugation: {
        εγώ: 'μιλάω',
        εσύ: 'μιλάς',
        αυτός: 'μιλάει',
        εμείς: 'μιλάμε',
        εσείς: 'μιλάτε',
        αυτοί: 'μιλάνε'
      }
    },
    {
      verb: 'τρώω',
      translation: 'to eat',
      tense: 'ενεστώτας',
      type: 'ενεργητική φωνή',
      group: 'B',
      conjugation: {
        εγώ: 'τρώω',
        εσύ: 'τρως',
        αυτός: 'τρώει',
        εμείς: 'τρώμε',
        εσείς: 'τρώτε',
        αυτοί: 'τρώνε'
      }
    }
  ];
  
  const stories = [
    {
      text: 'Ο Γιώργος και η Μαρία πηγαίνουν στην αγορά. Εκεί, ο Γιώργος ___ (γράφω) ένα μήνυμα στο κινητό του.',
      verb: 'γράφω',
      pronoun: 'αυτός',
      answer: 'γράφει'
    },
    {
      text: 'Στο πρωινό, εμείς ___ (τρώω) ψωμί με μέλι και ___ (πίνω) καφέ.',
      verb: 'τρώω',
      pronoun: 'εμείς',
      answer: 'τρώμε'
    }
  ];
  
  const loadRandomVerb = () => {
    const randomIndex = Math.floor(Math.random() * verbs.length);
    const newVerb = verbs[randomIndex];
    
    setVerbData({
      verb: newVerb.verb,
      translation: newVerb.translation,
      tense: newVerb.tense,
      type: newVerb.type,
      group: newVerb.group
    });
    
    setCorrectAnswers(newVerb.conjugation);
    setUserAnswers({
      εγώ: '',
      εσύ: '',
      αυτός: '',
      εμείς: '',
      εσείς: '',
      αυτοί: ''
    });
    
    setChecked(false);
  };
  
  const loadRandomStory = () => {
    const randomIndex = Math.floor(Math.random() * stories.length);
    const newStory = stories[randomIndex];
    
    setStoryContext(newStory.text);
    // Set up just the needed verb and pronoun for the story
    const verbObj = verbs.find(v => v.verb === newStory.verb);
    
    setVerbData({
      verb: newStory.verb,
      translation: verbObj.translation,
      tense: verbObj.tense,
      type: verbObj.type,
      group: verbObj.group
    });
    
    // We only need one answer in story mode
    const emptyAnswers = {
      εγώ: '',
      εσύ: '',
      αυτός: '',
      εμείς: '',
      εσείς: '',
      αυτοί: ''
    };
    
    setUserAnswers(emptyAnswers);
    setCorrectAnswers(verbObj.conjugation);
    setChecked(false);
  };
  
  useEffect(() => {
    loadRandomVerb();
  }, []);
  
  const handleInputChange = (pronoun, value) => {
    setUserAnswers(prev => ({
      ...prev,
      [pronoun]: value
    }));
  };
  
  const checkAnswers = () => {
    setChecked(true);
    let correct = 0;
    
    if (mode === 'practice') {
      // Check all pronouns in practice mode
      Object.keys(userAnswers).forEach(pronoun => {
        if (userAnswers[pronoun] === correctAnswers[pronoun]) {
          correct++;
        }
      });
      
      if (correct === 6) {
        setStreak(streak + 1);
        setScore(score + 10 + (streak * 2)); // Bonus for streaks
      } else {
        setStreak(0);
        setScore(score + correct);
      }
    } else {
      // In story mode, we only check the specific pronoun needed
      const story = stories.find(s => s.text === storyContext);
      if (userAnswers[story.pronoun] === correctAnswers[story.pronoun]) {
        setStreak(streak + 1);
        setScore(score + 5 + streak);
        correct = 1;
      } else {
        setStreak(0);
      }
    }
    
    return correct;
  };
  
  const nextQuestion = () => {
    if (mode === 'practice') {
      loadRandomVerb();
    } else {
      loadRandomStory();
    }
  };
  
  const switchMode = (newMode) => {
    setMode(newMode);
    if (newMode === 'practice') {
      loadRandomVerb();
    } else {
      loadRandomStory();
    }
  };
  
  return (
    <div className="flex flex-col items-center justify-center p-4 bg-gray-50 min-h-screen">
      <div className="w-full max-w-md">
        <header className="text-center mb-6">
          <h1 className="text-2xl font-bold text-blue-600">Ελληνική Γραμματική</h1>
          <p className="text-gray-600">Εξάσκηση στα Ρήματα</p>
          
          <div className="flex justify-center mt-4 space-x-4">
            <button 
              onClick={() => switchMode('practice')} 
              className={`px-4 py-2 rounded ${mode === 'practice' ? 'bg-blue-600 text-white' : 'bg-gray-200'}`}
            >
              Πρακτική
            </button>
            <button 
              onClick={() => switchMode('story')} 
              className={`px-4 py-2 rounded flex items-center ${mode === 'story' ? 'bg-blue-600 text-white' : 'bg-gray-200'}`}
            >
              <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="mr-2 h-4 w-4">
                <path d="M2 3h6a4 4 0 0 1 4 4v14a3 3 0 0 0-3-3H2z"></path>
                <path d="M22 3h-6a4 4 0 0 0-4 4v14a3 3 0 0 1 3-3h7z"></path>
              </svg>
              Ιστορία
            </button>
          </div>
        </header>
        
        <div className="bg-white shadow-lg rounded-lg overflow-hidden border">
          <div className="bg-blue-50 border-b pb-2 p-4">
            <div className="flex justify-between items-center">
              <div>
                <h2 className="text-xl font-bold text-blue-700">{verbData.verb} - {verbData.translation}</h2>
                <p className="text-sm text-gray-600">
                  {verbData.tense} • {verbData.type} • Ομάδα {verbData.group}
                </p>
              </div>
              <div className="text-right">
                <p className="text-sm font-semibold">Σκορ: {score}</p>
                <p className="text-xs">Σερί: {streak}</p>
              </div>
            </div>
          </div>
          
          <div className="p-6">
            {mode === 'practice' ? (
              <div className="grid grid-cols-1 gap-4">
                {Object.keys(userAnswers).map(pronoun => (
                  <div key={pronoun} className="flex items-center">
                    <label className="w-16 font-medium text-gray-700">{pronoun}</label>
                    <input
                      type="text"
                      value={userAnswers[pronoun]}
                      onChange={(e) => handleInputChange(pronoun, e.target.value)}
                      className="flex-1 p-2 border rounded focus:outline-none focus:ring-2 focus:ring-blue-500"
                      disabled={checked}
                    />
                    {checked && (
                      <div className="ml-2">
                        {userAnswers[pronoun] === correctAnswers[pronoun] ? (
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
                            <span className="text-sm text-gray-600">{correctAnswers[pronoun]}</span>
                          </div>
                        )}
                      </div>
                    )}
                  </div>
                ))}
              </div>
            ) : (
              <div className="space-y-4">
                <p className="text-gray-800 text-lg">{storyContext}</p>
                <div className="mt-4">
                  <p className="text-sm text-gray-600 mb-2">Συμπληρώστε το κενό με το σωστό τύπο του ρήματος "{verbData.verb}"</p>
                  <input
                    type="text"
                    value={userAnswers[stories.find(s => s.text === storyContext)?.pronoun || 'αυτός']}
                    onChange={(e) => handleInputChange(stories.find(s => s.text === storyContext)?.pronoun || 'αυτός', e.target.value)}
                    className="w-full p-2 border rounded focus:outline-none focus:ring-2 focus:ring-blue-500"
                    disabled={checked}
                  />
                  {checked && (
                    <div className="mt-2">
                      {userAnswers[stories.find(s => s.text === storyContext)?.pronoun || 'αυτός'] === 
                      correctAnswers[stories.find(s => s.text === storyContext)?.pronoun || 'αυτός'] ? (
                        <div className="text-green-600 flex items-center">
                          <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="h-5 w-5 mr-2">
                            <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"></path>
                            <polyline points="22 4 12 14.01 9 11.01"></polyline>
                          </svg>
                          <span>Σωστά!</span>
                        </div>
                      ) : (
                        <div className="text-red-600 flex items-center">
                          <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="h-5 w-5 mr-2">
                            <circle cx="12" cy="12" r="10"></circle>
                            <line x1="15" y1="9" x2="9" y2="15"></line>
                            <line x1="9" y1="9" x2="15" y2="15"></line>
                          </svg>
                          <span>Η σωστή απάντηση είναι: {correctAnswers[stories.find(s => s.text === storyContext)?.pronoun || 'αυτός']}</span>
                        </div>
                      )}
                    </div>
                  )}
                </div>
              </div>
            )}
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
          </div>
        </div>
      </div>
    </div>
  );
};

export default GreekConjugationApp;