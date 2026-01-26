let audioContext;

const getAudioContext = () => {
  if (!audioContext) {
    audioContext = new (window.AudioContext || window.webkitAudioContext)();
  }
  return audioContext;
};

const playTone = (frequency, durationMs, type = 'sine', gain = 0.12) => {
  const ctx = getAudioContext();
  const oscillator = ctx.createOscillator();
  const gainNode = ctx.createGain();

  oscillator.type = type;
  oscillator.frequency.value = frequency;
  gainNode.gain.value = gain;

  oscillator.connect(gainNode);
  gainNode.connect(ctx.destination);

  const now = ctx.currentTime;
  const duration = durationMs / 1000;
  gainNode.gain.setValueAtTime(gain, now);
  gainNode.gain.exponentialRampToValueAtTime(0.0001, now + duration);

  oscillator.start(now);
  oscillator.stop(now + duration);
};

export const playClick = () => {
  playTone(800, 60, 'square', 0.07);
};

export const playChime = () => {
  playTone(660, 120, 'sine', 0.12);
  setTimeout(() => playTone(990, 140, 'sine', 0.12), 90);
};

export const playBloop = () => {
  playTone(260, 140, 'sine', 0.12);
  setTimeout(() => playTone(200, 140, 'sine', 0.1), 120);
};
