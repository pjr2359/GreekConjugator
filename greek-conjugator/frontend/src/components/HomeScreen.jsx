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
// PIXEL ART GIAGIA (Greek Grandmother) - CSS-based animated character
// ============================================================================
const PixelGiagia = ({ isWatering, position }) => {
  return (
    <div 
      className={`absolute transition-all duration-1000 ${isWatering ? 'animate-giagia-water' : 'animate-giagia-walk'}`}
      style={{ 
        bottom: '72px',
        left: position,
        transform: 'translateX(-50%)',
        imageRendering: 'pixelated'
      }}
    >
      {/* Giagia pixel art using CSS */}
      <svg width="24" height="32" viewBox="0 0 24 32" className="pixelated drop-shadow-md">
        {/* Head */}
        <rect x="8" y="2" width="8" height="8" fill="#F5DEB3" /> {/* Face */}
        <rect x="7" y="0" width="10" height="4" fill="#9CA3AF" /> {/* Gray hair bun */}
        <rect x="6" y="3" width="2" height="3" fill="#9CA3AF" /> {/* Side hair */}
        <rect x="16" y="3" width="2" height="3" fill="#9CA3AF" /> {/* Side hair */}
        <rect x="9" y="5" width="2" height="1" fill="#1F2937" /> {/* Left eye */}
        <rect x="13" y="5" width="2" height="1" fill="#1F2937" /> {/* Right eye */}
        <rect x="11" y="7" width="2" height="1" fill="#D97706" /> {/* Smile */}
        
        {/* Body - black dress */}
        <rect x="6" y="10" width="12" height="14" fill="#1F2937" /> {/* Dress */}
        <rect x="7" y="11" width="10" height="3" fill="#374151" /> {/* Apron top */}
        <rect x="8" y="14" width="8" height="8" fill="#E5E7EB" /> {/* White apron */}
        
        {/* Arms */}
        <rect x="4" y="11" width="2" height="6" fill="#F5DEB3" /> {/* Left arm */}
        <rect x="18" y="11" width="2" height="6" fill="#F5DEB3" /> {/* Right arm */}
        
        {/* Legs */}
        <rect x="8" y="24" width="3" height="6" fill="#1F2937" /> {/* Left leg */}
        <rect x="13" y="24" width="3" height="6" fill="#1F2937" /> {/* Right leg */}
        <rect x="7" y="29" width="4" height="2" fill="#4B5563" /> {/* Left shoe */}
        <rect x="13" y="29" width="4" height="2" fill="#4B5563" /> {/* Right shoe */}
        
        {/* Watering can (when watering) */}
        {isWatering && (
          <>
            <rect x="19" y="14" width="6" height="4" fill="#3B82F6" /> {/* Can body */}
            <rect x="24" y="12" width="2" height="3" fill="#3B82F6" /> {/* Spout */}
            <rect x="20" y="12" width="1" height="2" fill="#3B82F6" /> {/* Handle */}
            {/* Water drops */}
            <rect x="25" y="15" width="1" height="2" fill="#60A5FA" className="animate-water-drop" />
            <rect x="26" y="17" width="1" height="2" fill="#93C5FD" className="animate-water-drop" style={{animationDelay: '0.2s'}} />
          </>
        )}
      </svg>
    </div>
  );
};

// ============================================================================
// OLIVE TREE WIDGET - Pixel art tree that grows with your progress
// ============================================================================
const OliveTreeWidget = ({ wordsKnown, todayActivity }) => {
  const [giagiaPosition, setGiagiaPosition] = useState('30%');
  const [isWatering, setIsWatering] = useState(false);
  
  const getGrowthStage = () => {
    if (wordsKnown >= 1000) return { stage: 4, name: 'Ancient', icon: '🏆', image: '/assets/olive-tree/ancient.png', size: 120 };
    if (wordsKnown >= 500) return { stage: 3, name: 'Mature', icon: '🫒', image: '/assets/olive-tree/mature.png', size: 100 };
    if (wordsKnown >= 100) return { stage: 2, name: 'Sapling', icon: '🌿', image: '/assets/olive-tree/sapling.png', size: 80 };
    if (wordsKnown >= 25) return { stage: 1, name: 'Sprout', icon: '🌱', image: '/assets/olive-tree/sprout.png', size: 70 };
    return { stage: 0, name: 'Seed', icon: '🫘', image: '/assets/olive-tree/sprout.png', size: 50 };
  };
  
  const growth = getGrowthStage();
  const isHealthy = todayActivity > 0;
  const thresholds = [25, 100, 500, 1000, 1000];
  const nextThreshold = thresholds[growth.stage];
  const prevThreshold = growth.stage > 0 ? thresholds[growth.stage - 1] : 0;
  const progressToNext = growth.stage < 4 
    ? Math.min(((wordsKnown - prevThreshold) / (nextThreshold - prevThreshold)) * 100, 100)
    : 100;
  
  // Animate giagia walking and watering
  useEffect(() => {
    if (isHealthy) {
      // When healthy, giagia waters the tree
      const wateringCycle = () => {
        // Walk to tree
        setGiagiaPosition('45%');
        setIsWatering(false);
        
        // Start watering after reaching tree
        setTimeout(() => {
          setIsWatering(true);
        }, 1500);
        
        // Stop watering and walk away
        setTimeout(() => {
          setIsWatering(false);
          setGiagiaPosition('70%');
        }, 4000);
        
        // Walk back
        setTimeout(() => {
          setGiagiaPosition('30%');
        }, 6000);
      };
      
      wateringCycle();
      const interval = setInterval(wateringCycle, 10000);
      return () => clearInterval(interval);
    } else {
      // When not healthy, giagia stands sadly
      setGiagiaPosition('25%');
      setIsWatering(false);
    }
  }, [isHealthy]);
  
  return (
    <div className="bg-gradient-to-b from-slate-800/80 to-slate-900/80 rounded-2xl border border-slate-700/50 overflow-hidden">
      {/* Scene container with pixel art background */}
      <div className="relative h-48 overflow-hidden">
        {/* Pixel art landscape background */}
        <img 
          src="/assets/olive-tree/background-hilltop.png" 
          alt="Greek island hilltop"
          className="absolute inset-0 w-full h-full object-cover pixelated"
          style={{ imageRendering: 'pixelated' }}
        />
        
        {/* Subtle animated overlay for depth */}
        <div className="absolute inset-0 bg-gradient-to-t from-black/20 via-transparent to-transparent" />
        
        {/* Pixel Art Tree - positioned on the hilltop */}
        <div className={`absolute bottom-20 left-1/2 -translate-x-1/2 transition-all duration-500 ${isHealthy ? 'animate-sway' : 'opacity-70 grayscale-[30%]'}`}>
          <img 
            src={growth.image} 
            alt={`${growth.name} olive tree`}
            className="pixelated drop-shadow-[0_4px_8px_rgba(0,0,0,0.4)]"
            style={{ 
              width: growth.size, 
              height: 'auto',
              imageRendering: 'pixelated'
            }}
          />
        </div>
        
        {/* Animated Giagia */}
        <PixelGiagia isWatering={isWatering} position={giagiaPosition} />
        
        {/* Sparkles when healthy */}
        {isHealthy && growth.stage >= 1 && (
          <div className="absolute bottom-36 left-1/2 -translate-x-1/2 pointer-events-none">
            <div className="animate-sparkle">
              <div className="absolute -left-10 -top-6 w-2 h-2 bg-yellow-300 rounded-full shadow-lg shadow-yellow-300/50" />
              <div className="absolute left-8 -top-10 w-1.5 h-1.5 bg-yellow-200 rounded-full shadow-lg shadow-yellow-200/50" style={{animationDelay: '0.5s'}} />
              <div className="absolute -left-5 top-2 w-1 h-1 bg-yellow-300 rounded-full shadow-lg shadow-yellow-300/50" style={{animationDelay: '1s'}} />
            </div>
          </div>
        )}
        
        {/* Health indicator */}
        <div className={`absolute top-3 right-3 px-2 py-1 rounded-lg text-xs font-medium shadow-lg ${
          isHealthy 
            ? 'bg-emerald-600/90 text-white border border-emerald-400/50' 
            : 'bg-amber-600/90 text-white border border-amber-400/50'
        }`} style={{fontFamily: 'inherit'}}>
          {isHealthy ? '✨ Thriving' : '💧 Water me'}
        </div>
      </div>
      
      {/* Info bar */}
      <div className="px-4 py-3 bg-slate-900/80">
        <div className="flex items-center justify-between mb-2">
          <div className="flex items-center gap-2">
            <span className="text-lg">{growth.icon}</span>
            <div>
              <div className="text-sm font-medium text-white">{growth.name} Tree</div>
              <div className="text-xs text-slate-400">{wordsKnown} words learned</div>
            </div>
          </div>
          {growth.stage < 4 && (
            <div className="text-right">
              <div className="text-xs text-cyan-400">{nextThreshold - wordsKnown} to next</div>
            </div>
          )}
          {growth.stage >= 4 && (
            <div className="text-xs text-amber-400">🏆 Max Growth!</div>
          )}
        </div>
        
        {/* Growth progress */}
        <div className="flex gap-1">
          {[0, 1, 2, 3, 4].map((stage) => (
            <div 
              key={stage}
              className={`h-1.5 flex-1 rounded-full transition-all overflow-hidden ${
                stage < growth.stage ? 'bg-emerald-500' :
                stage === growth.stage ? 'bg-slate-700' :
                'bg-slate-700'
              }`}
            >
              {stage === growth.stage && (
                <div 
                  className="h-full bg-emerald-500 rounded-full transition-all duration-500"
                  style={{ width: `${progressToNext}%` }}
                />
              )}
            </div>
          ))}
        </div>
        <div className="flex justify-between mt-1 text-xs text-slate-500">
          <span>Seed</span>
          <span>Sprout</span>
          <span>Sapling</span>
          <span>Mature</span>
          <span>Ancient</span>
        </div>
      </div>
      
      {/* CSS */}
      <style>{`
        @keyframes cloud-move { 0%, 100% { transform: translateX(0); } 50% { transform: translateX(20px); } }
        @keyframes cloud-move-slow { 0%, 100% { transform: translateX(0); } 50% { transform: translateX(15px); } }
        @keyframes wave-move { 0%, 100% { transform: translateX(0) scaleY(1); } 50% { transform: translateX(-10px) scaleY(0.8); } }
        @keyframes tree-sway { 0%, 100% { transform: translateX(-50%) rotate(-1deg); } 50% { transform: translateX(-50%) rotate(1deg); } }
        @keyframes sparkle-anim { 0%, 100% { opacity: 0; transform: scale(0.5); } 50% { opacity: 1; transform: scale(1); } }
        @keyframes water-drop { 
          0% { opacity: 1; transform: translateY(0); } 
          100% { opacity: 0; transform: translateY(8px); } 
        }
        @keyframes giagia-bob { 
          0%, 100% { transform: translateX(-50%) translateY(0); } 
          50% { transform: translateX(-50%) translateY(-2px); } 
        }
        .animate-cloud { animation: cloud-move 15s ease-in-out infinite; }
        .animate-cloud-slow { animation: cloud-move-slow 20s ease-in-out infinite; }
        .animate-wave { animation: wave-move 3s ease-in-out infinite; }
        .animate-sway { animation: tree-sway 4s ease-in-out infinite; }
        .animate-sparkle div { animation: sparkle-anim 2s ease-in-out infinite; }
        .animate-water-drop { animation: water-drop 0.5s ease-in infinite; }
        .animate-giagia-walk { animation: giagia-bob 0.4s ease-in-out infinite; }
        .animate-giagia-water { animation: none; }
        .pixelated { image-rendering: pixelated; image-rendering: crisp-edges; }
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

        {/* Olive Tree Widget - temporarily disabled for development
        <div className="mb-4">
          <OliveTreeWidget 
            wordsKnown={vocab?.total_known || 0} 
            todayActivity={(dashboard?.today?.reviews_completed || 0) + (dashboard?.today?.words_learned || 0)}
          />
        </div>
        */}

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
              <span className="text-2xl font-bold text-white">{Math.round(coverage?.percent || 0)}%</span>
              <span className="text-sm text-slate-400 ml-2">of everyday Greek</span>
            </div>
            <span className="text-cyan-400 font-semibold">{vocab?.for_coverage || 0} words</span>
          </div>
          <div className="h-2 bg-slate-700 rounded-full overflow-hidden">
            <div 
              className="h-full bg-gradient-to-r from-cyan-500 to-purple-500 transition-all duration-1000"
              style={{ width: `${Math.round(coverage?.percent || 0)}%` }}
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
            <div className="text-lg font-bold text-emerald-400">{vocab?.mastered || 0}</div>
            <div className="text-xs text-slate-500">Mastered</div>
          </div>
          <div className="bg-slate-800/50 rounded-lg p-2.5 text-center border border-slate-700/30">
            <div className="text-lg font-bold text-cyan-400">{vocab?.known || 0}</div>
            <div className="text-xs text-slate-500">Known</div>
          </div>
          <div className="bg-slate-800/50 rounded-lg p-2.5 text-center border border-slate-700/30">
            <div className="text-lg font-bold text-blue-400">{vocab?.new || 0}</div>
            <div className="text-xs text-slate-500">New</div>
          </div>
          <div className="bg-slate-800/50 rounded-lg p-2.5 text-center border border-slate-700/30">
            <div className="text-lg font-bold text-amber-400">{vocab?.due || 0}</div>
            <div className="text-xs text-slate-500">Due</div>
          </div>
        </div>

        {/* Skills Row */}
        <div className="mb-4">
          <div className="bg-slate-800/60 rounded-xl border border-slate-700/50 p-3">
            <div className="flex items-center justify-between mb-2">
              <span className="text-xs font-medium text-slate-400">Skills</span>
              <span className="text-xs text-purple-400">{grammar?.skills_proficient || 0}/{grammar?.total_skills || 11}</span>
            </div>
            <div className="flex justify-center gap-2">
              {grammar?.domains && Object.entries(grammar.domains).slice(0, 6).map(([key, domain]) => (
                <SkillRing 
                  key={key}
                  name={domain.name}
                  progress={domain.progress}
                  color={domain.progress >= 80 ? '#10b981' : domain.progress >= 50 ? '#8b5cf6' : '#3b82f6'}
                  size={36}
                />
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
