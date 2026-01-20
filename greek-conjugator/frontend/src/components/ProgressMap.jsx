import React, { useState, useEffect } from 'react';
import { skillsService } from '../services/api';

const ProgressMap = ({ user, onBackToHome, onStartPractice }) => {
  const [skillTree, setSkillTree] = useState(null);
  const [selectedSkill, setSelectedSkill] = useState(null);
  const [loading, setLoading] = useState(true);
  const [stats, setStats] = useState(null);

  useEffect(() => {
    loadSkillTree();
    loadStats();
  }, []);

  const loadSkillTree = async () => {
    try {
      const data = await skillsService.getSkillTree();
      setSkillTree(data);
    } catch (error) {
      console.error('Failed to load skill tree:', error);
    } finally {
      setLoading(false);
    }
  };

  const loadStats = async () => {
    try {
      const data = await skillsService.getStats();
      setStats(data);
    } catch (error) {
      console.error('Failed to load stats:', error);
    }
  };

  const getMasteryColor = (level) => {
    const colors = {
      0: 'bg-slate-700 border-slate-600',
      1: 'bg-slate-600 border-slate-500',
      2: 'bg-blue-600 border-blue-500',
      3: 'bg-emerald-600 border-emerald-500',
      4: 'bg-amber-500 border-amber-400',
      5: 'bg-gradient-to-br from-yellow-400 to-amber-500 border-yellow-300'
    };
    return colors[level] || colors[0];
  };

  const getMasteryLabel = (level) => {
    const labels = {
      0: 'Locked',
      1: 'Beginner',
      2: 'Developing',
      3: 'Proficient',
      4: 'Expert',
      5: 'Master'
    };
    return labels[level] || 'Unknown';
  };

  const getTierName = (tier) => {
    const names = {
      1: 'Beginner',
      2: 'Elementary',
      3: 'Intermediate',
      4: 'Advanced',
      5: 'Expert'
    };
    return names[tier] || `Tier ${tier}`;
  };

  const handleSkillClick = async (skill) => {
    if (!skill.unlocked) return;
    
    try {
      const detail = await skillsService.getSkillDetail(skill.category);
      setSelectedSkill(detail);
    } catch (error) {
      console.error('Failed to load skill detail:', error);
    }
  };

  const startSkillPractice = (skill) => {
    if (onStartPractice) {
      onStartPractice({
        mode: 'conjugation',
        useBackend: true,
        skillCategory: skill.category,
        tense: skill.category.split('_')[0],
        mood: skill.category.split('_')[1],
        voice: skill.category.split('_')[2] || 'active'
      });
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-900 via-blue-900 to-slate-900 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-16 w-16 border-b-2 border-purple-500 mx-auto mb-4"></div>
          <p className="text-slate-400">Loading your progress...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-blue-900 to-slate-900 p-4">
      <div className="max-w-4xl mx-auto">
        {/* Header */}
        <div className="flex items-center justify-between mb-6">
          <button
            onClick={onBackToHome}
            className="flex items-center text-slate-400 hover:text-white transition-colors"
          >
            <svg className="w-5 h-5 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
            </svg>
            Back
          </button>
        </div>

        {/* Title & Overall Progress */}
        <div className="text-center mb-8">
          <div className="text-5xl mb-3">🗺️</div>
          <h1 className="text-3xl font-bold text-white mb-1">Χάρτης Προόδου</h1>
          <p className="text-blue-300">Conjugation Progress Map</p>
          
          {/* Overall Progress Bar */}
          {skillTree && (
            <div className="mt-6 max-w-md mx-auto">
              <div className="flex justify-between text-sm text-slate-400 mb-2">
                <span>Overall Mastery</span>
                <span>{skillTree.mastery_percentage}%</span>
              </div>
              <div className="w-full bg-slate-700 rounded-full h-4">
                <div 
                  className="bg-gradient-to-r from-purple-500 to-pink-500 h-4 rounded-full transition-all duration-500"
                  style={{ width: `${skillTree.mastery_percentage}%` }}
                />
              </div>
              <div className="flex justify-between text-xs text-slate-500 mt-1">
                <span>{skillTree.unlocked_skills}/{skillTree.total_skills} skills unlocked</span>
                <span>{stats?.mastered_skills || 0} mastered</span>
              </div>
            </div>
          )}
        </div>

        {/* Quick Stats */}
        {stats && (
          <div className="grid grid-cols-4 gap-3 mb-8">
            <div className="bg-slate-800/50 rounded-xl p-4 text-center border border-slate-700">
              <div className="text-2xl font-bold text-blue-400">{stats.unlocked_skills}</div>
              <div className="text-xs text-slate-400">Unlocked</div>
            </div>
            <div className="bg-slate-800/50 rounded-xl p-4 text-center border border-slate-700">
              <div className="text-2xl font-bold text-emerald-400">{stats.proficient_skills}</div>
              <div className="text-xs text-slate-400">Proficient</div>
            </div>
            <div className="bg-slate-800/50 rounded-xl p-4 text-center border border-slate-700">
              <div className="text-2xl font-bold text-amber-400">{stats.mastered_skills}</div>
              <div className="text-xs text-slate-400">Mastered</div>
            </div>
            <div className="bg-slate-800/50 rounded-xl p-4 text-center border border-slate-700">
              <div className="text-2xl font-bold text-purple-400">{stats.overall_accuracy}%</div>
              <div className="text-xs text-slate-400">Accuracy</div>
            </div>
          </div>
        )}

        {/* Skill Tree */}
        {skillTree && Object.entries(skillTree.tiers).map(([tier, skills]) => (
          <div key={tier} className="mb-8">
            {/* Tier Header */}
            <div className="flex items-center gap-3 mb-4">
              <div className={`w-10 h-10 rounded-full flex items-center justify-center text-white font-bold
                ${tier <= 2 ? 'bg-emerald-600' : tier <= 3 ? 'bg-blue-600' : tier <= 4 ? 'bg-purple-600' : 'bg-amber-500'}`}>
                {tier}
              </div>
              <div>
                <h2 className="text-xl font-bold text-white">{getTierName(parseInt(tier))}</h2>
                <p className="text-sm text-slate-400">
                  {skills.filter(s => s.unlocked).length}/{skills.length} unlocked
                </p>
              </div>
            </div>

            {/* Skills Grid */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {skills.map((skill) => (
                <button
                  key={skill.category}
                  onClick={() => handleSkillClick(skill)}
                  disabled={!skill.unlocked}
                  className={`relative p-4 rounded-xl border-2 transition-all text-left
                    ${skill.unlocked 
                      ? `${getMasteryColor(skill.mastery_level)} hover:scale-105 cursor-pointer` 
                      : 'bg-slate-800/50 border-slate-700 opacity-50 cursor-not-allowed'
                    }`}
                >
                  {/* Lock icon for locked skills */}
                  {!skill.unlocked && (
                    <div className="absolute top-2 right-2 text-2xl">🔒</div>
                  )}
                  
                  {/* Mastery crown for mastered skills */}
                  {skill.mastery_level >= 5 && (
                    <div className="absolute top-2 right-2 text-2xl">👑</div>
                  )}

                  <div className="flex items-start gap-3">
                    <div className="text-3xl">{skill.icon}</div>
                    <div className="flex-1">
                      <h3 className="font-bold text-white">{skill.display_name}</h3>
                      <p className="text-sm text-white/70">{skill.display_name_greek}</p>
                      
                      {/* Progress bar */}
                      {skill.unlocked && (
                        <div className="mt-2">
                          <div className="flex justify-between text-xs text-white/60 mb-1">
                            <span>{getMasteryLabel(skill.mastery_level)}</span>
                            <span>{skill.accuracy}%</span>
                          </div>
                          <div className="w-full bg-black/20 rounded-full h-2">
                            <div 
                              className="bg-white/80 h-2 rounded-full transition-all"
                              style={{ width: `${(skill.mastery_level / 5) * 100}%` }}
                            />
                          </div>
                        </div>
                      )}
                      
                      {/* Stats */}
                      {skill.unlocked && skill.attempts > 0 && (
                        <p className="text-xs text-white/50 mt-1">
                          {skill.correct}/{skill.attempts} correct
                        </p>
                      )}
                    </div>
                  </div>
                </button>
              ))}
            </div>

            {/* Connection line to next tier */}
            {parseInt(tier) < 5 && (
              <div className="flex justify-center my-4">
                <div className="w-0.5 h-8 bg-slate-600"></div>
              </div>
            )}
          </div>
        ))}

        {/* Skill Detail Modal */}
        {selectedSkill && (
          <div className="fixed inset-0 bg-black/70 flex items-center justify-center p-4 z-50">
            <div className="bg-slate-800 rounded-2xl border border-slate-700 max-w-lg w-full max-h-[90vh] overflow-y-auto">
              {/* Modal Header */}
              <div className={`p-6 ${getMasteryColor(selectedSkill.mastery_level)} rounded-t-2xl`}>
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-3">
                    <div className="text-4xl">{selectedSkill.icon}</div>
                    <div>
                      <h2 className="text-2xl font-bold text-white">{selectedSkill.display_name}</h2>
                      <p className="text-white/80">{selectedSkill.display_name_greek}</p>
                    </div>
                  </div>
                  <button
                    onClick={() => setSelectedSkill(null)}
                    className="text-white/60 hover:text-white text-2xl"
                  >
                    ×
                  </button>
                </div>
              </div>

              {/* Modal Content */}
              <div className="p-6">
                {/* Description */}
                <p className="text-slate-300 mb-4">{selectedSkill.description}</p>

                {/* Stats */}
                <div className="grid grid-cols-3 gap-4 mb-6">
                  <div className="text-center p-3 bg-slate-700/50 rounded-lg">
                    <div className="text-xl font-bold text-white">{selectedSkill.attempts}</div>
                    <div className="text-xs text-slate-400">Attempts</div>
                  </div>
                  <div className="text-center p-3 bg-slate-700/50 rounded-lg">
                    <div className="text-xl font-bold text-emerald-400">{selectedSkill.correct}</div>
                    <div className="text-xs text-slate-400">Correct</div>
                  </div>
                  <div className="text-center p-3 bg-slate-700/50 rounded-lg">
                    <div className="text-xl font-bold text-amber-400">
                      {selectedSkill.attempts > 0 ? Math.round((selectedSkill.correct / selectedSkill.attempts) * 100) : 0}%
                    </div>
                    <div className="text-xs text-slate-400">Accuracy</div>
                  </div>
                </div>

                {/* Mastery Progress */}
                <div className="mb-6">
                  <div className="flex justify-between text-sm mb-2">
                    <span className="text-slate-400">Mastery Level</span>
                    <span className="text-white font-bold">{getMasteryLabel(selectedSkill.mastery_level)}</span>
                  </div>
                  <div className="flex gap-1">
                    {[1, 2, 3, 4, 5].map(level => (
                      <div
                        key={level}
                        className={`flex-1 h-3 rounded ${
                          level <= selectedSkill.mastery_level
                            ? level === 5 ? 'bg-amber-400' : 'bg-purple-500'
                            : 'bg-slate-600'
                        }`}
                      />
                    ))}
                  </div>
                  <p className="text-xs text-slate-500 mt-2">
                    {selectedSkill.mastery_level < 3 
                      ? `Reach Proficient to unlock the next skill`
                      : selectedSkill.mastery_level < 5
                        ? `Keep practicing to reach Master level`
                        : `🎉 You've mastered this skill!`
                    }
                  </p>
                </div>

                {/* Sample Forms */}
                {selectedSkill.samples && selectedSkill.samples.length > 0 && (
                  <div className="mb-6">
                    <h3 className="text-sm font-bold text-slate-400 mb-2">Sample Forms</h3>
                    <div className="space-y-2">
                      {selectedSkill.samples.map((sample, i) => (
                        <div key={i} className="flex justify-between bg-slate-700/30 rounded-lg p-2 text-sm">
                          <span className="text-purple-300 font-medium">{sample.form}</span>
                          <span className="text-slate-400">{sample.verb} - {sample.english}</span>
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {/* Practice Button */}
                <button
                  onClick={() => {
                    setSelectedSkill(null);
                    startSkillPractice(selectedSkill);
                  }}
                  className="w-full py-4 bg-gradient-to-r from-purple-500 to-pink-500 text-white font-bold rounded-xl 
                    hover:from-purple-600 hover:to-pink-600 transition-all text-lg"
                >
                  ▶️ Practice {selectedSkill.display_name}
                </button>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default ProgressMap;




