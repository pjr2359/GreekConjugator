import React, { useState } from 'react';
import HomeScreen from './components/HomeScreen';
import GreekConjugationApp from './components/GreekConjugationApp';
import NounDeclinationApp from './components/NounDeclinationApp';
import AdjectiveApp from './components/AdjectiveApp';
import ArticleApp from './components/ArticleApp';

const App = () => {
  const [currentScreen, setCurrentScreen] = useState('home');
  const [practiceSettings, setPracticeSettings] = useState({});

  // Start practice with selected settings
  const handleStartPractice = (settings) => {
    setPracticeSettings(settings);
    setCurrentScreen('practice');
  };

  // Return to home screen
  const handleBackToHome = () => {
    setCurrentScreen('home');
  };

  // Render current screen
  const renderScreen = () => {
    switch (currentScreen) {
      case 'home':
        return <HomeScreen onStartPractice={handleStartPractice} />;
      case 'practice':
        // Select the appropriate practice component based on mode
        switch (practiceSettings.mode) {
          case 'verb':
            return <GreekConjugationApp 
              settings={practiceSettings}
              onBackToHome={handleBackToHome}
            />;
          case 'noun':
            return <NounDeclinationApp 
              settings={practiceSettings}
              onBackToHome={handleBackToHome}
            />;
          case 'adjective':
            return <AdjectiveApp 
              settings={practiceSettings}
              onBackToHome={handleBackToHome}
            />;
          case 'article':
            return <ArticleApp 
              settings={practiceSettings}
              onBackToHome={handleBackToHome}
            />;
          default:
            return <div>Invalid practice mode</div>;
        }
      default:
        return <div>Screen not found</div>;
    }
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {renderScreen()}
    </div>
  );
};

export default App;