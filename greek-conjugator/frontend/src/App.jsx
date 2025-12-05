import React, { useState, useEffect } from 'react';
import './App.css';
import AuthComponent from './components/AuthComponent';
import HomeScreen from './components/HomeScreen';
import PracticeSession from './components/PracticeSession';
import GreekConjugationApp from './components/GreekConjugationApp';
import NounDeclinationApp from './components/NounDeclinationApp';
import AdjectiveApp from './components/AdjectiveApp';
import ArticleApp from './components/ArticleApp';
import VocabularyPractice from './components/VocabularyPractice';
import { authService } from './services/api';

const App = () => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [currentScreen, setCurrentScreen] = useState('home');
  const [practiceSettings, setPracticeSettings] = useState({});

  // Check authentication on app load
  useEffect(() => {
    const checkAuth = async () => {
      try {
        const authData = await authService.checkAuth();
        if (authData.authenticated) {
          setUser(authData.user);
        }
      } catch (error) {
        console.error('Auth check failed:', error);
      } finally {
        setLoading(false);
      }
    };

    checkAuth();
  }, []);

  // Start practice with selected settings
  const handleStartPractice = (settings) => {
    setPracticeSettings(settings);

    // Use new backend-powered practice for verb conjugations
    if (settings.mode === 'verb' && settings.useBackend) {
      setCurrentScreen('new-practice');
    } else {
      setCurrentScreen('practice');
    }
  };

  // Return to home screen
  const handleBackToHome = () => {
    setCurrentScreen('home');
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-900 via-blue-900 to-slate-900 flex items-center justify-center">
        <div className="text-center">
          <div className="text-6xl mb-4">🏛️</div>
          <div className="animate-spin rounded-full h-10 w-10 border-b-2 border-blue-400 mx-auto"></div>
        </div>
      </div>
    );
  }

  // Show authentication screen if not logged in
  if (!user) {
    return <AuthComponent user={user} setUser={setUser} />;
  }

  // Navigate to vocabulary practice
  const handleStartVocabulary = () => {
    setCurrentScreen('vocabulary');
  };

  // Render current screen for authenticated users
  const renderScreen = () => {
    switch (currentScreen) {
      case 'home':
        return <HomeScreen onStartPractice={handleStartPractice} onStartVocabulary={handleStartVocabulary} user={user} />;
      case 'new-practice':
        return <PracticeSession user={user} onBackToHome={handleBackToHome} />;
      case 'vocabulary':
        return <VocabularyPractice user={user} onBackToHome={handleBackToHome} />;
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
              onBackToHome={handleBackToHome}
            />;
          case 'article':
            return <ArticleApp
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
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-blue-900 to-slate-900">
      <AuthComponent user={user} setUser={setUser} />
      {renderScreen()}
    </div>
  );
};

export default App;