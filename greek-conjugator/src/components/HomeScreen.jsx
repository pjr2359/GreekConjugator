import React, { useState } from 'react';

const HomeScreen = ({ onStartPractice }) => {
  // Practice mode state
  const [selectedMode, setSelectedMode] = useState('verb'); // 'verb', 'noun', 'adjective', 'article'
  
  // Verb specific options
  const [verbSettings, setVerbSettings] = useState({
    tense: 'all',       // Selected tense
    type: 'all',        // Selected verb type
    group: 'all'        // Selected verb group
  });
  
  // Noun specific options
  const [nounSettings, setNounSettings] = useState({
    case: 'all',        // nominative, genitive, etc.
    number: 'all',      // singular, plural
    gender: 'all'       // masculine, feminine, neuter
  });
  
  // Handle settings changes
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
  const startPractice = () => {
    const settings = {
      mode: selectedMode,
      ...(selectedMode === 'verb' ? verbSettings : {}),
      ...(selectedMode === 'noun' ? nounSettings : {})
    };
    
    onStartPractice(settings);
  };
  
  return (
    <div className="flex flex-col items-center justify-center p-4 bg-gray-50 min-h-screen">
      <div className="w-full max-w-md">
        <header className="text-center mb-6">
          <h1 className="text-2xl font-bold text-blue-600">Greek Grammar Practice <span className="text-gray-500">(Εξάσκηση Ελληνικής Γραμματικής)</span></h1>
          <p className="text-gray-600">Choose your exercises <span className="text-gray-500">(Επιλέξτε τις ασκήσεις σας)</span></p>
        </header>
        
        <div className="bg-white shadow-lg rounded-lg overflow-hidden border mb-6">
          <div className="bg-blue-50 border-b p-4">
            <h2 className="text-xl font-bold text-blue-700">What would you like to practice? <span className="text-gray-500 text-lg">(Τι θα θέλατε να εξασκήσετε;)</span></h2>
          </div>
          
          <div className="p-6">
            {/* Mode selection */}
            <div className="grid grid-cols-2 gap-4 mb-6">
              <button 
                onClick={() => setSelectedMode('verb')}
                className={`p-4 rounded-lg border ${selectedMode === 'verb' ? 'bg-blue-100 border-blue-500' : 'border-gray-200'}`}
              >
                <div className="text-center">
                  <span className="text-xl mb-2 block">🔤</span>
                  <span className="font-medium">Verbs <span className="text-sm text-gray-500">(Ρήματα)</span></span>
                </div>
              </button>
              <button 
                onClick={() => setSelectedMode('noun')}
                className={`p-4 rounded-lg border ${selectedMode === 'noun' ? 'bg-blue-100 border-blue-500' : 'border-gray-200'}`}
              >
                <div className="text-center">
                  <span className="text-xl mb-2 block">📝</span>
                  <span className="font-medium">Nouns <span className="text-sm text-gray-500">(Ουσιαστικά)</span></span>
                </div>
              </button>
              <button 
                onClick={() => setSelectedMode('adjective')}
                className={`p-4 rounded-lg border ${selectedMode === 'adjective' ? 'bg-blue-100 border-blue-500' : 'border-gray-200'}`}
              >
                <div className="text-center">
                  <span className="text-xl mb-2 block">🏷️</span>
                  <span className="font-medium">Adjectives <span className="text-sm text-gray-500">(Επίθετα)</span></span>
                </div>
              </button>
              <button 
                onClick={() => setSelectedMode('article')}
                className={`p-4 rounded-lg border ${selectedMode === 'article' ? 'bg-blue-100 border-blue-500' : 'border-gray-200'}`}
              >
                <div className="text-center">
                  <span className="text-xl mb-2 block">🔍</span>
                  <span className="font-medium">Articles <span className="text-sm text-gray-500">(Άρθρα)</span></span>
                </div>
              </button>
            </div>
            
            {/* Verb options */}
            {selectedMode === 'verb' && (
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Tense <span className="text-gray-500">(Χρόνος)</span></label>
                  <select 
                    value={verbSettings.tense} 
                    onChange={(e) => handleVerbSettingChange('tense', e.target.value)}
                    className="w-full p-2 border rounded"
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
                    className="w-full p-2 border rounded"
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
                    className="w-full p-2 border rounded"
                  >
                    <option value="all">All Groups (Όλες οι Ομάδες)</option>
                    <option value="A">Group A (Ομάδα Α)</option>
                    <option value="B">Group B (Ομάδα Β)</option>
                  </select>
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
                    className="w-full p-2 border rounded"
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
                    className="w-full p-2 border rounded"
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
                    className="w-full p-2 border rounded"
                  >
                    <option value="all">All Genders (Όλα τα Γένη)</option>
                    <option value="αρσενικό">Masculine (Αρσενικό)</option>
                    <option value="θηλυκό">Feminine (Θηλυκό)</option>
                    <option value="ουδέτερο">Neuter (Ουδέτερο)</option>
                  </select>
                </div>
              </div>
            )}
            
            {/* Adjective options (simplified) */}
            {selectedMode === 'adjective' && (
              <div className="p-4 bg-gray-50 rounded">
                <p>Practice adjectives - agreement with nouns in gender, number, and case. <span className="text-gray-500">(Εξάσκηση επιθέτων - συμφωνία με ουσιαστικά σε γένος, αριθμό και πτώση.)</span></p>
              </div>
            )}
            
            {/* Article options (simplified) */}
            {selectedMode === 'article' && (
              <div className="p-4 bg-gray-50 rounded">
                <p>Practice using articles - definite and indefinite articles. <span className="text-gray-500">(Εξάσκηση στη χρήση άρθρων - οριστικά και αόριστα άρθρα.)</span></p>
              </div>
            )}
          </div>
          
          <div className="bg-gray-50 border-t p-4">
            <button 
              onClick={startPractice}
              className="w-full bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700"
            >
              Start Practice <span className="text-gray-200">(Έναρξη Εξάσκησης)</span>
            </button>
          </div>
        </div>
        
        <div className="text-center text-sm text-gray-600">
          <p>Greek Grammar - Practice Application <span className="text-gray-500">(Ελληνική Γραμματική - Εφαρμογή Εξάσκησης)</span></p>
        </div>
      </div>
    </div>
  );
};

export default HomeScreen;