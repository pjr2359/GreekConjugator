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
          <h1 className="text-2xl font-bold text-blue-600">Ελληνική Γραμματική</h1>
          <p className="text-gray-600">Επιλέξτε τις ασκήσεις σας</p>
        </header>
        
        <div className="bg-white shadow-lg rounded-lg overflow-hidden border mb-6">
          <div className="bg-blue-50 border-b p-4">
            <h2 className="text-xl font-bold text-blue-700">Τι θέλετε να εξασκήσετε;</h2>
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
                  <span className="font-medium">Ρήματα</span>
                </div>
              </button>
              <button 
                onClick={() => setSelectedMode('noun')}
                className={`p-4 rounded-lg border ${selectedMode === 'noun' ? 'bg-blue-100 border-blue-500' : 'border-gray-200'}`}
              >
                <div className="text-center">
                  <span className="text-xl mb-2 block">📝</span>
                  <span className="font-medium">Ουσιαστικά</span>
                </div>
              </button>
              <button 
                onClick={() => setSelectedMode('adjective')}
                className={`p-4 rounded-lg border ${selectedMode === 'adjective' ? 'bg-blue-100 border-blue-500' : 'border-gray-200'}`}
              >
                <div className="text-center">
                  <span className="text-xl mb-2 block">🏷️</span>
                  <span className="font-medium">Επίθετα</span>
                </div>
              </button>
              <button 
                onClick={() => setSelectedMode('article')}
                className={`p-4 rounded-lg border ${selectedMode === 'article' ? 'bg-blue-100 border-blue-500' : 'border-gray-200'}`}
              >
                <div className="text-center">
                  <span className="text-xl mb-2 block">🔍</span>
                  <span className="font-medium">Άρθρα</span>
                </div>
              </button>
            </div>
            
            {/* Verb options */}
            {selectedMode === 'verb' && (
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Χρόνος</label>
                  <select 
                    value={verbSettings.tense} 
                    onChange={(e) => handleVerbSettingChange('tense', e.target.value)}
                    className="w-full p-2 border rounded"
                  >
                    <option value="all">Όλοι οι χρόνοι</option>
                    <option value="ενεστώτας">Ενεστώτας</option>
                    <option value="αόριστος">Αόριστος</option>
                    <option value="παρατατικός">Παρατατικός</option>
                    <option value="μέλλοντας">Μέλλοντας</option>
                    <option value="παρακείμενος">Παρακείμενος</option>
                    <option value="υπερσυντέλικος">Υπερσυντέλικος</option>
                  </select>
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Τύπος</label>
                  <select 
                    value={verbSettings.type} 
                    onChange={(e) => handleVerbSettingChange('type', e.target.value)}
                    className="w-full p-2 border rounded"
                  >
                    <option value="all">Όλοι οι τύποι</option>
                    <option value="ενεργητική φωνή">Ενεργητική φωνή</option>
                    <option value="παθητική φωνή">Παθητική φωνή</option>
                    <option value="μέση φωνή">Μέση φωνή</option>
                  </select>
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Ομάδα</label>
                  <select 
                    value={verbSettings.group} 
                    onChange={(e) => handleVerbSettingChange('group', e.target.value)}
                    className="w-full p-2 border rounded"
                  >
                    <option value="all">Όλες οι ομάδες</option>
                    <option value="A">Ομάδα Α</option>
                    <option value="B">Ομάδα Β</option>
                  </select>
                </div>
              </div>
            )}
            
            {/* Noun options */}
            {selectedMode === 'noun' && (
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Πτώση</label>
                  <select 
                    value={nounSettings.case} 
                    onChange={(e) => handleNounSettingChange('case', e.target.value)}
                    className="w-full p-2 border rounded"
                  >
                    <option value="all">Όλες οι πτώσεις</option>
                    <option value="ονομαστική">Ονομαστική</option>
                    <option value="γενική">Γενική</option>
                    <option value="αιτιατική">Αιτιατική</option>
                    <option value="κλητική">Κλητική</option>
                  </select>
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Αριθμός</label>
                  <select 
                    value={nounSettings.number} 
                    onChange={(e) => handleNounSettingChange('number', e.target.value)}
                    className="w-full p-2 border rounded"
                  >
                    <option value="all">Όλοι οι αριθμοί</option>
                    <option value="ενικός">Ενικός</option>
                    <option value="πληθυντικός">Πληθυντικός</option>
                  </select>
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Γένος</label>
                  <select 
                    value={nounSettings.gender} 
                    onChange={(e) => handleNounSettingChange('gender', e.target.value)}
                    className="w-full p-2 border rounded"
                  >
                    <option value="all">Όλα τα γένη</option>
                    <option value="αρσενικό">Αρσενικό</option>
                    <option value="θηλυκό">Θηλυκό</option>
                    <option value="ουδέτερο">Ουδέτερο</option>
                  </select>
                </div>
              </div>
            )}
            
            {/* Adjective options (simplified) */}
            {selectedMode === 'adjective' && (
              <div className="p-4 bg-gray-50 rounded">
                <p>Εξάσκηση στα επίθετα - συμφωνία με τα ουσιαστικά σε γένος, αριθμό και πτώση.</p>
              </div>
            )}
            
            {/* Article options (simplified) */}
            {selectedMode === 'article' && (
              <div className="p-4 bg-gray-50 rounded">
                <p>Εξάσκηση στη χρήση των άρθρων - οριστικά και αόριστα άρθρα.</p>
              </div>
            )}
          </div>
          
          <div className="bg-gray-50 border-t p-4">
            <button 
              onClick={startPractice}
              className="w-full bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700"
            >
              Έναρξη εξάσκησης
            </button>
          </div>
        </div>
        
        <div className="text-center text-sm text-gray-600">
          <p>Ελληνική Γραμματική - Εφαρμογή Εξάσκησης</p>
        </div>
      </div>
    </div>
  );
};

export default HomeScreen;