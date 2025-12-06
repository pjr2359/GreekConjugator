import React, { useState, useEffect } from 'react';
import { vocabularyService, skillsService } from '../services/api';

const HomeScreen = ({ onStartPractice, onStartVocabulary, onViewProgress, user }) => {
  const [vocabStats, setVocabStats] = useState(null);
  const [skillStats, setSkillStats] = useState(null);
  const [loading, setLoading] = useState(true);

  // Load all stats on component mount
  useEffect(() => {
    const loadAllStats = async () => {
      if (!user) return;
      
      setLoading(true);
      try {
        // Fetch all stats in parallel for speed
        const [vocabData, skillData] = await Promise.all([
          vocabularyService.getStats().catch(() => null),
          skillsService.getSkillTree().catch(() => null)
        ]);
        
        setVocabStats(vocabData);
        setSkillStats(skillData);
      } catch (error) {
        console.error('Failed to load stats:', error);
      } finally {
        setLoading(false);
      }
    };

    loadAllStats();
  }, [user]);

  // Start conjugation practice with backend
  const startConjugationPractice = () => {
    onStartPractice({
      mode: 'verb',
      useBackend: true
    });
  };

  // Calculate total due items
  const totalDue = (vocabStats?.due_for_review || 0);
  const vocabKnown = vocabStats?.words_practiced || 0;
  const vocabTotal = vocabStats?.unlocked_words || 100;
  const skillsMastered = skillStats?.skills?.filter(s => s.mastery_level >= 3).length || 0;
  const totalSkills = skillStats?.total_skills || 11;
  const overallAccuracy = vocabStats?.accuracy_rate || 0;

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-blue-900 to-slate-900 p-4">
      <div className="max-w-2xl mx-auto pt-4">
        {/* Header */}
        <header className="text-center mb-6">
          <div className="text-4xl mb-2">🏛️</div>
          <h1 className="text-2xl font-bold text-white">Ελληνικά</h1>
        </header>

        {/* Unified Progress Dashboard */}
        <div className="bg-slate-800/60 rounded-2xl border border-slate-700/50 p-4 mb-6">
          {/* Top row - Key metrics */}
          <div className="grid grid-cols-3 gap-4 mb-4">
            {/* Vocabulary Progress */}
            <div className="text-center">
              <div className="text-2xl font-bold text-cyan-400">{vocabKnown}</div>
              <div className="text-xs text-slate-400">Words Known</div>
              <div className="mt-1 h-1 bg-slate-700 rounded-full overflow-hidden">
                <div 
                  className="h-full bg-gradient-to-r from-cyan-500 to-blue-500 transition-all duration-500"
                  style={{ width: `${Math.min((vocabKnown / vocabTotal) * 100, 100)}%` }}
                />
              </div>
            </div>
            
            {/* Skills Progress */}
            <div className="text-center">
              <div className="text-2xl font-bold text-purple-400">{skillsMastered}/{totalSkills}</div>
              <div className="text-xs text-slate-400">Skills</div>
              <div className="mt-1 h-1 bg-slate-700 rounded-full overflow-hidden">
                <div 
                  className="h-full bg-gradient-to-r from-purple-500 to-pink-500 transition-all duration-500"
                  style={{ width: `${(skillsMastered / totalSkills) * 100}%` }}
                />
              </div>
            </div>
            
            {/* Accuracy */}
            <div className="text-center">
              <div className="text-2xl font-bold text-emerald-400">{overallAccuracy}%</div>
              <div className="text-xs text-slate-400">Accuracy</div>
              <div className="mt-1 h-1 bg-slate-700 rounded-full overflow-hidden">
                <div 
                  className="h-full bg-gradient-to-r from-emerald-500 to-green-500 transition-all duration-500"
                  style={{ width: `${overallAccuracy}%` }}
                />
              </div>
            </div>
          </div>

          {/* Due for review banner */}
          {totalDue > 0 && (
            <div className="bg-amber-500/10 border border-amber-500/30 rounded-xl p-3 flex items-center justify-between">
              <div className="flex items-center gap-2">
                <span className="text-amber-400">🔔</span>
                <span className="text-amber-200 text-sm">
                  <strong>{totalDue}</strong> {totalDue === 1 ? 'word' : 'words'} due for review
                </span>
              </div>
              <button 
                onClick={onStartVocabulary}
                className="text-xs bg-amber-500/20 hover:bg-amber-500/30 text-amber-300 px-3 py-1 rounded-lg transition-colors"
              >
                Review Now
              </button>
            </div>
          )}
        </div>

        {/* Practice Buttons */}
        <div className="space-y-3">
          {/* Vocabulary */}
          <button
            onClick={onStartVocabulary}
            className="w-full bg-slate-800/80 hover:bg-slate-700/80 border border-slate-700 rounded-xl p-4 
              flex items-center justify-between transition-all group"
          >
            <div className="flex items-center gap-3">
              <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-cyan-500 to-blue-600 flex items-center justify-center text-2xl">
                📚
              </div>
              <div className="text-left">
                <div className="text-white font-semibold">Vocabulary</div>
                <div className="text-slate-400 text-sm">{vocabStats?.new_available || 0} new available</div>
              </div>
            </div>
            <div className="text-slate-400 group-hover:text-white transition-colors">→</div>
          </button>

          {/* Conjugations */}
          <button
            onClick={startConjugationPractice}
            className="w-full bg-slate-800/80 hover:bg-slate-700/80 border border-slate-700 rounded-xl p-4 
              flex items-center justify-between transition-all group"
          >
            <div className="flex items-center gap-3">
              <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-purple-500 to-pink-600 flex items-center justify-center text-2xl">
                📝
              </div>
              <div className="text-left">
                <div className="text-white font-semibold">Conjugations</div>
                <div className="text-slate-400 text-sm">Practice verb forms</div>
              </div>
            </div>
            <div className="text-slate-400 group-hover:text-white transition-colors">→</div>
          </button>

          {/* Progress Map */}
          <button
            onClick={onViewProgress}
            className="w-full bg-slate-800/80 hover:bg-slate-700/80 border border-slate-700 rounded-xl p-4 
              flex items-center justify-between transition-all group"
          >
            <div className="flex items-center gap-3">
              <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-amber-500 to-orange-600 flex items-center justify-center text-2xl">
                🗺️
              </div>
              <div className="text-left">
                <div className="text-white font-semibold">Skill Tree</div>
                <div className="text-slate-400 text-sm">{skillsMastered} of {totalSkills} mastered</div>
              </div>
            </div>
            <div className="text-slate-400 group-hover:text-white transition-colors">→</div>
          </button>
        </div>

        {/* Mini skill icons row */}
        {skillStats?.skills && (
          <div className="mt-6 flex flex-wrap justify-center gap-2">
            {skillStats.skills.slice(0, 11).map((skill, i) => (
              <div 
                key={skill.category}
                className={`w-8 h-8 rounded-lg flex items-center justify-center text-xs font-bold transition-all
                  ${skill.mastery_level >= 5 ? 'bg-gradient-to-br from-yellow-400 to-amber-500 text-yellow-900' :
                    skill.mastery_level >= 3 ? 'bg-emerald-600 text-white' :
                    skill.mastery_level >= 1 ? 'bg-slate-600 text-slate-300' :
                    'bg-slate-800 text-slate-600'}`}
                title={`${skill.name}: Level ${skill.mastery_level}`}
              >
                {skill.mastery_level}
              </div>
            ))}
          </div>
        )}

      </div>
    </div>
  );
};

export default HomeScreen;