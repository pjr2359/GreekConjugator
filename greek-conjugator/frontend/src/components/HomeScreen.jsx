import React, { useState, useEffect } from 'react';
import { dashboardService } from '../services/api';

// ============================================================================
// SKILL RING COMPONENT - Apple Fitness style
// ============================================================================
const SkillRing = ({ name, progress, color, size = 60 }) => {
  const strokeWidth = size * 0.12;
  const radius = (size - strokeWidth) / 2;
  const circumference = 2 * Math.PI * radius;
  const offset = circumference - (progress / 100) * circumference;
  
  return (
    <div className="relative" style={{ width: size, height: size }}>
      <svg width={size} height={size} className="transform -rotate-90">
        {/* Background ring */}
        <circle
          cx={size / 2}
          cy={size / 2}
          r={radius}
          fill="none"
          stroke="rgba(255,255,255,0.1)"
          strokeWidth={strokeWidth}
        />
        {/* Progress ring */}
        <circle
          cx={size / 2}
          cy={size / 2}
          r={radius}
          fill="none"
          stroke={color}
          strokeWidth={strokeWidth}
          strokeLinecap="round"
          strokeDasharray={circumference}
          strokeDashoffset={offset}
          className="transition-all duration-1000 ease-out"
        />
      </svg>
      <div className="absolute inset-0 flex items-center justify-center">
        <span className="text-xs font-bold text-white">{Math.round(progress)}%</span>
      </div>
    </div>
  );
};

// ============================================================================
// QUEST ITEM COMPONENT
// ============================================================================
const QuestItem = ({ quest }) => {
  const progressPercent = (quest.progress / quest.target) * 100;
  
  return (
    <div className={`flex items-center gap-3 p-3 rounded-xl transition-all ${
      quest.completed 
        ? 'bg-emerald-500/10 border border-emerald-500/30' 
        : 'bg-slate-800/50 border border-slate-700/50'
    }`}>
      <div className={`w-8 h-8 rounded-lg flex items-center justify-center text-sm ${
        quest.completed ? 'bg-emerald-500 text-white' : 'bg-slate-700 text-slate-400'
      }`}>
        {quest.completed ? '✓' : quest.progress}
      </div>
      <div className="flex-1 min-w-0">
        <div className="flex items-center justify-between mb-1">
          <span className={`text-sm font-medium ${quest.completed ? 'text-emerald-400' : 'text-slate-300'}`}>
            {quest.name}
          </span>
          <span className="text-xs text-amber-400">+{quest.xp} XP</span>
        </div>
        <div className="h-1 bg-slate-700 rounded-full overflow-hidden">
          <div 
            className={`h-full transition-all duration-500 ${
              quest.completed ? 'bg-emerald-500' : 'bg-purple-500'
            }`}
            style={{ width: `${Math.min(progressPercent, 100)}%` }}
          />
        </div>
      </div>
    </div>
  );
};

// ============================================================================
// OLIVE TREE WIDGET - Compact animated scene in a frame
// ============================================================================
const OliveTreeWidget = ({ wordsKnown, todayActivity }) => {
  const getGrowthStage = () => {
    if (wordsKnown >= 2000) return { stage: 6, name: 'Ancient', icon: '🏆' };
    if (wordsKnown >= 1000) return { stage: 5, name: 'Mature', icon: '🫒' };
    if (wordsKnown >= 500) return { stage: 4, name: 'Flourishing', icon: '🌳' };
    if (wordsKnown >= 250) return { stage: 3, name: 'Branching', icon: '🌿' };
    if (wordsKnown >= 100) return { stage: 2, name: 'Sapling', icon: '🌱' };
    if (wordsKnown >= 25) return { stage: 1, name: 'Sprout', icon: '🌱' };
    return { stage: 0, name: 'Seed', icon: '🫘' };
  };
  
  const growth = getGrowthStage();
  const isHealthy = todayActivity > 0;
  const nextThreshold = [25, 100, 250, 500, 1000, 2000, 2000][growth.stage];
  const progressToNext = growth.stage < 6 
    ? Math.min(((wordsKnown - [0, 25, 100, 250, 500, 1000, 2000][growth.stage]) / (nextThreshold - [0, 25, 100, 250, 500, 1000, 2000][growth.stage])) * 100, 100)
    : 100;
  
  return (
    <div className="bg-gradient-to-b from-slate-800/80 to-slate-900/80 rounded-2xl border border-slate-700/50 overflow-hidden">
      {/* Scene container */}
      <div className="relative h-40 overflow-hidden">
        <svg viewBox="0 0 200 120" className="w-full h-full" preserveAspectRatio="xMidYMax slice">
          <defs>
            <linearGradient id="sky" x1="0%" y1="0%" x2="0%" y2="100%">
              <stop offset="0%" stopColor="#7dd3fc" />
              <stop offset="100%" stopColor="#bae6fd" />
            </linearGradient>
            <linearGradient id="sea" x1="0%" y1="0%" x2="0%" y2="100%">
              <stop offset="0%" stopColor="#0ea5e9" />
              <stop offset="100%" stopColor="#0369a1" />
            </linearGradient>
            <linearGradient id="hill" x1="0%" y1="0%" x2="0%" y2="100%">
              <stop offset="0%" stopColor="#84cc16" />
              <stop offset="100%" stopColor="#4d7c0f" />
            </linearGradient>
          </defs>
          
          {/* Sky */}
          <rect x="0" y="0" width="200" height="70" fill="url(#sky)" />
          
          {/* Sun */}
          <circle cx="170" cy="25" r="15" fill="#fcd34d" className="animate-pulse" style={{animationDuration: '4s'}} />
          
          {/* Clouds */}
          <g className="animate-cloud">
            <ellipse cx="40" cy="30" rx="15" ry="6" fill="white" opacity="0.9" />
            <ellipse cx="52" cy="28" rx="10" ry="4" fill="white" opacity="0.9" />
          </g>
          <g className="animate-cloud-slow">
            <ellipse cx="130" cy="40" rx="12" ry="5" fill="white" opacity="0.7" />
          </g>
          
          {/* Sea */}
          <rect x="0" y="55" width="200" height="25" fill="url(#sea)" />
          
          {/* Waves */}
          <path d="M0 60 Q20 57 40 60 T80 60 T120 60 T160 60 T200 60 V65 H0 Z" fill="#38bdf8" opacity="0.5" className="animate-wave" />
          
          {/* Sailboat */}
          <g className="animate-boat" style={{transformOrigin: '160px 58px'}}>
            <path d="M155 58 L160 48 L160 60 Z" fill="white" />
            <rect x="153" y="60" width="10" height="3" fill="#78350f" rx="1" />
          </g>
          
          {/* Hill */}
          <path d="M-10 80 Q50 60 100 70 Q150 60 210 80 L210 120 L-10 120 Z" fill="url(#hill)" />
          
          {/* Grass tufts */}
          <g stroke="#4d7c0f" strokeWidth="1.5" fill="none" opacity="0.5">
            <path d="M30 90 Q32 85 34 90" />
            <path d="M70 82 Q72 77 74 82" />
            <path d="M150 88 Q152 83 154 88" />
          </g>
          
          {/* Flowers */}
          <circle cx="45" cy="95" r="2" fill="#fbbf24" />
          <circle cx="140" cy="92" r="2" fill="#f472b6" />
          
          {/* THE TREE */}
          <g transform="translate(100, 95)">
            {/* Shadow */}
            <ellipse cx="0" cy="20" rx={8 + growth.stage * 3} ry="4" fill="#000" opacity="0.1" />
            
            {/* Trunk */}
            {growth.stage >= 1 ? (
              <path 
                d={`M-2 20 Q-3 ${10 - growth.stage * 2} 0 ${-growth.stage * 3} Q3 ${10 - growth.stage * 2} 2 20 Z`}
                fill={isHealthy ? '#78350f' : '#6b7280'}
              />
            ) : (
              /* Seed */
              <ellipse cx="0" cy="18" rx="3" ry="2" fill="#78350f" />
            )}
            
            {/* Foliage */}
            {growth.stage >= 1 && (
              <g className={isHealthy ? 'animate-sway' : ''} style={{transformOrigin: '0 20px'}}>
                <ellipse 
                  cx="0" 
                  cy={-growth.stage * 4} 
                  rx={6 + growth.stage * 4} 
                  ry={4 + growth.stage * 2.5} 
                  fill={isHealthy ? '#4ade80' : '#6b7280'} 
                  opacity="0.9"
                />
                {growth.stage >= 2 && (
                  <>
                    <ellipse cx={-growth.stage * 2.5} cy={-growth.stage * 2} rx={4 + growth.stage * 2} ry={3 + growth.stage * 1.5} fill={isHealthy ? '#22c55e' : '#78716c'} opacity="0.8" />
                    <ellipse cx={growth.stage * 2.5} cy={-growth.stage * 2.5} rx={4 + growth.stage * 2} ry={3 + growth.stage * 1.5} fill={isHealthy ? '#22c55e' : '#78716c'} opacity="0.8" />
                  </>
                )}
                {growth.stage >= 4 && (
                  <ellipse cx="0" cy={-growth.stage * 5.5} rx={4 + growth.stage} ry={3 + growth.stage * 0.5} fill={isHealthy ? '#86efac' : '#9ca3af'} opacity="0.7" />
                )}
                {/* Olives */}
                {growth.stage >= 5 && (
                  <>
                    <circle cx="-8" cy="-8" r="2" fill="#365314" />
                    <circle cx="6" cy="-12" r="2" fill="#365314" />
                    <circle cx="10" cy="-5" r="2" fill="#365314" />
                  </>
                )}
              </g>
            )}
            
            {/* Sprout for stage 0 */}
            {growth.stage === 0 && (
              <path d="M0 16 Q-1.5 10 0 5 Q1.5 10 0 16" fill="#4ade80" />
            )}
          </g>
          
          {/* Sparkles when healthy */}
          {isHealthy && growth.stage >= 2 && (
            <g className="animate-sparkle">
              <circle cx="90" cy="78" r="1.5" fill="#fef08a" />
              <circle cx="112" cy="75" r="1" fill="#fef08a" />
            </g>
          )}
        </svg>
        
        {/* Health indicator */}
        <div className={`absolute top-2 right-2 px-2 py-1 rounded-full text-xs font-medium ${
          isHealthy 
            ? 'bg-emerald-500/20 text-emerald-400 border border-emerald-500/30' 
            : 'bg-amber-500/20 text-amber-400 border border-amber-500/30'
        }`}>
          {isHealthy ? '✨ Thriving' : '💧 Water me'}
        </div>
      </div>
      
      {/* Info bar */}
      <div className="px-4 py-3 bg-slate-900/50">
        <div className="flex items-center justify-between mb-2">
          <div className="flex items-center gap-2">
            <span className="text-lg">{growth.icon}</span>
            <div>
              <div className="text-sm font-medium text-white">{growth.name} Tree</div>
              <div className="text-xs text-slate-400">{wordsKnown} words learned</div>
            </div>
          </div>
          {growth.stage < 6 && (
            <div className="text-right">
              <div className="text-xs text-slate-400">Next: {nextThreshold}</div>
            </div>
          )}
        </div>
        
        {/* Growth progress */}
        <div className="flex gap-1">
          {[0, 1, 2, 3, 4, 5, 6].map((stage) => (
            <div 
              key={stage}
              className={`h-1.5 flex-1 rounded-full transition-all ${
                stage < growth.stage ? 'bg-emerald-500' :
                stage === growth.stage ? 'bg-emerald-500/50' :
                'bg-slate-700'
              }`}
            >
              {stage === growth.stage && (
                <div 
                  className="h-full bg-emerald-500 rounded-full transition-all"
                  style={{ width: `${progressToNext}%` }}
                />
              )}
            </div>
          ))}
        </div>
      </div>
      
      {/* CSS */}
      <style>{`
        @keyframes cloud-move { 0% { transform: translateX(0); } 100% { transform: translateX(30px); } }
        @keyframes cloud-move-slow { 0% { transform: translateX(0); } 100% { transform: translateX(20px); } }
        @keyframes wave-move { 0%, 100% { transform: translateX(0); } 50% { transform: translateX(-5px); } }
        @keyframes boat-bob { 0%, 100% { transform: translateY(0) rotate(0deg); } 50% { transform: translateY(-2px) rotate(2deg); } }
        @keyframes tree-sway { 0%, 100% { transform: rotate(-1.5deg); } 50% { transform: rotate(1.5deg); } }
        @keyframes sparkle-anim { 0%, 100% { opacity: 0.3; } 50% { opacity: 1; } }
        .animate-cloud { animation: cloud-move 20s ease-in-out infinite alternate; }
        .animate-cloud-slow { animation: cloud-move-slow 25s ease-in-out infinite alternate; }
        .animate-wave { animation: wave-move 3s ease-in-out infinite; }
        .animate-boat { animation: boat-bob 3s ease-in-out infinite; }
        .animate-sway { animation: tree-sway 4s ease-in-out infinite; }
        .animate-sparkle circle { animation: sparkle-anim 2s ease-in-out infinite; }
        .animate-sparkle circle:nth-child(2) { animation-delay: 0.7s; }
      `}</style>
    </div>
  );
};

// ============================================================================
// MAIN HOME SCREEN COMPONENT
// ============================================================================
const HomeScreen = ({ onStartPractice, onStartVocabulary, onViewProgress, user }) => {
  const [dashboard, setDashboard] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const loadDashboard = async () => {
      if (!user) return;
      
      setLoading(true);
      try {
        const data = await dashboardService.getComprehensiveStats();
        setDashboard(data);
      } catch (error) {
        console.error('Failed to load dashboard:', error);
      } finally {
        setLoading(false);
      }
    };

    loadDashboard();
  }, [user]);

  const startConjugationPractice = () => {
    onStartPractice({ mode: 'verb', useBackend: true });
  };

  // Extract data with defaults
  const vocab = dashboard?.vocabulary || {};
  const coverage = dashboard?.coverage || {};
  const grammar = dashboard?.grammar || {};
  const quests = dashboard?.quests || [];
  const nextStep = dashboard?.next_step || {};
  const tier = coverage?.tier?.current || { name: 'Beginner', greek: 'Αρχάριος' };
  const nextTier = coverage?.tier?.next;

  // Loading state
  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-900 via-blue-900 to-slate-900 flex items-center justify-center">
        <div className="text-center">
          <div className="text-4xl mb-4 animate-pulse">🫒</div>
          <div className="text-slate-400">Loading your garden...</div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-blue-900 to-slate-900 p-4 pb-8">
      <div className="max-w-lg mx-auto">
        
        {/* Header */}
        <header className="flex items-center justify-between mb-4 pt-2">
          <div>
            <h1 className="text-xl font-bold text-white">Ελληνικά</h1>
            <div className="text-sm text-slate-400">{tier.greek} • {tier.name}</div>
          </div>
          <div className="text-right">
            <div className="text-2xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-amber-400 to-orange-500">
              {dashboard?.competency_score || 0}
            </div>
            <div className="text-xs text-slate-500">Competency</div>
          </div>
        </header>

        {/* Olive Tree Widget */}
        <div className="mb-4">
          <OliveTreeWidget 
            wordsKnown={vocab?.total_known || 0} 
            todayActivity={(dashboard?.today?.reviews_completed || 0) + (dashboard?.today?.words_learned || 0)}
          />
        </div>

        {/* Next Best Step */}
        {nextStep && nextStep.title && (
          <div className={`mb-4 p-3 rounded-xl border ${
            nextStep.type === 'urgent' ? 'bg-red-500/10 border-red-500/30' :
            nextStep.type === 'important' ? 'bg-amber-500/10 border-amber-500/30' :
            nextStep.type === 'improve' ? 'bg-purple-500/10 border-purple-500/30' :
            nextStep.type === 'grow' ? 'bg-cyan-500/10 border-cyan-500/30' :
            'bg-slate-800/50 border-slate-700/50'
          }`}>
            <div className="flex items-center justify-between">
              <div>
                <div className="text-xs text-slate-400 uppercase tracking-wider mb-0.5">Next Step</div>
                <div className={`font-medium text-sm ${
                  nextStep.type === 'urgent' ? 'text-red-400' :
                  nextStep.type === 'important' ? 'text-amber-400' :
                  nextStep.type === 'improve' ? 'text-purple-400' :
                  'text-cyan-400'
                }`}>
                  {nextStep.title}
                </div>
              </div>
              <button 
                onClick={() => {
                  if (nextStep.route === 'vocabulary') onStartVocabulary();
                  else if (nextStep.route === 'conjugation') startConjugationPractice();
                  else if (nextStep.route === 'progress') onViewProgress();
                }}
                className="px-3 py-1.5 rounded-lg text-xs font-medium bg-white/10 hover:bg-white/20 text-white transition-all"
              >
                Go →
              </button>
            </div>
          </div>
        )}

        {/* Greek Coverage */}
        <div className="bg-slate-800/60 rounded-xl border border-slate-700/50 p-3 mb-3">
          <div className="flex items-center justify-between mb-2">
            <div>
              <span className="text-2xl font-bold text-white">{coverage?.percent || 0}%</span>
              <span className="text-sm text-slate-400 ml-2">of everyday Greek</span>
            </div>
            <span className="text-cyan-400 font-semibold">{vocab?.total_known || 0} words</span>
          </div>
          <div className="h-2 bg-slate-700 rounded-full overflow-hidden">
            <div 
              className="h-full bg-gradient-to-r from-cyan-500 to-purple-500 transition-all duration-1000"
              style={{ width: `${coverage?.tier?.progress_percent || 0}%` }}
            />
          </div>
          {nextTier && (
            <div className="text-xs text-slate-500 mt-2 text-center">
              {coverage?.tier?.words_to_next || 0} words to <span className="text-cyan-400">{nextTier.name}</span>
              {nextTier.unlock && <span className="text-amber-400"> • 🔓 {nextTier.unlock}</span>}
            </div>
          )}
        </div>

        {/* Vocab Stats */}
        <div className="grid grid-cols-4 gap-2 mb-3">
          <div className="bg-slate-800/50 rounded-lg p-2.5 text-center border border-slate-700/30">
            <div className="text-lg font-bold text-emerald-400">{vocab?.active || 0}</div>
            <div className="text-xs text-slate-500">Active</div>
          </div>
          <div className="bg-slate-800/50 rounded-lg p-2.5 text-center border border-slate-700/30">
            <div className="text-lg font-bold text-blue-400">{vocab?.learning || 0}</div>
            <div className="text-xs text-slate-500">Learning</div>
          </div>
          <div className="bg-slate-800/50 rounded-lg p-2.5 text-center border border-slate-700/30">
            <div className="text-lg font-bold text-amber-400">{vocab?.due || 0}</div>
            <div className="text-xs text-slate-500">Due</div>
          </div>
          <div className="bg-slate-800/50 rounded-lg p-2.5 text-center border border-slate-700/30">
            <div className="text-lg font-bold text-red-400">{vocab?.at_risk || 0}</div>
            <div className="text-xs text-slate-500">At Risk</div>
          </div>
        </div>

        {/* Skills + Quests Row */}
        <div className="grid grid-cols-2 gap-3 mb-4">
          {/* Skills */}
          <div className="bg-slate-800/60 rounded-xl border border-slate-700/50 p-3">
            <div className="flex items-center justify-between mb-2">
              <span className="text-xs font-medium text-slate-400">Skills</span>
              <span className="text-xs text-purple-400">{grammar?.skills_proficient || 0}/{grammar?.total_skills || 11}</span>
            </div>
            <div className="flex justify-center gap-1">
              {grammar?.domains && Object.entries(grammar.domains).slice(0, 4).map(([key, domain]) => (
                <SkillRing 
                  key={key}
                  name={domain.name}
                  progress={domain.progress}
                  color={domain.progress >= 80 ? '#10b981' : domain.progress >= 50 ? '#8b5cf6' : '#3b82f6'}
                  size={32}
                />
              ))}
            </div>
          </div>

          {/* Daily Quests */}
          <div className="bg-slate-800/60 rounded-xl border border-slate-700/50 p-3">
            <div className="flex items-center justify-between mb-2">
              <span className="text-xs font-medium text-slate-400">Quests</span>
              <span className="text-xs text-emerald-400">{quests.filter(q => q.completed).length}/{quests.length}</span>
            </div>
            <div className="space-y-1">
              {quests.slice(0, 2).map(quest => (
                <div key={quest.id} className="flex items-center gap-1.5">
                  <div className={`w-4 h-4 rounded text-xs flex items-center justify-center ${quest.completed ? 'bg-emerald-500 text-white' : 'bg-slate-600 text-slate-400'}`}>
                    {quest.completed ? '✓' : quest.progress}
                  </div>
                  <span className={`text-xs truncate ${quest.completed ? 'text-emerald-400' : 'text-slate-400'}`}>{quest.name}</span>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Practice Buttons */}
        <div className="space-y-2">
          <button
            onClick={onStartVocabulary}
            className="w-full bg-gradient-to-r from-cyan-600 to-blue-700 hover:from-cyan-500 hover:to-blue-600 
              text-white font-semibold py-3.5 px-4 rounded-xl transition-all flex items-center justify-between shadow-lg shadow-cyan-900/30"
          >
            <div className="flex items-center gap-3">
              <span className="text-xl">📚</span>
              <span>Study Vocabulary</span>
            </div>
            {vocab?.due > 0 && <span className="text-xs bg-white/20 px-2 py-0.5 rounded-full">{vocab.due} due</span>}
          </button>
          
          <button
            onClick={startConjugationPractice}
            className="w-full bg-gradient-to-r from-purple-600 to-pink-700 hover:from-purple-500 hover:to-pink-600 
              text-white font-semibold py-3.5 px-4 rounded-xl transition-all flex items-center justify-between shadow-lg shadow-purple-900/30"
          >
            <div className="flex items-center gap-3">
              <span className="text-xl">📝</span>
              <span>Practice Conjugations</span>
            </div>
            <span className="text-xs bg-white/20 px-2 py-0.5 rounded-full">{grammar?.skills_proficient || 0} skills</span>
          </button>

          <button
            onClick={onViewProgress}
            className="w-full bg-slate-800/80 hover:bg-slate-700/80 border border-slate-700 
              text-slate-300 font-medium py-3 px-4 rounded-xl transition-all flex items-center justify-center gap-2"
          >
            <span>🗺️</span>
            <span>View Skill Tree</span>
          </button>
        </div>

      </div>
    </div>
  );
};

export default HomeScreen;
