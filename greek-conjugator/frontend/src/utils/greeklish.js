const ACCENT_MAP = {
  'ά': 'α',
  'έ': 'ε',
  'ή': 'η',
  'ί': 'ι',
  'ό': 'ο',
  'ύ': 'υ',
  'ώ': 'ω',
  'ϊ': 'ι',
  'ΐ': 'ι',
  'ϋ': 'υ',
  'ΰ': 'υ',
  'Ά': 'Α',
  'Έ': 'Ε',
  'Ή': 'Η',
  'Ί': 'Ι',
  'Ό': 'Ο',
  'Ύ': 'Υ',
  'Ώ': 'Ω',
  'Ϊ': 'Ι',
  'Ϋ': 'Υ',
};

const DIGRAPHS = [
  ['γγ', 'ng'],
  ['γκ', 'g'],
  ['μπ', 'b'],
  ['ντ', 'd'],
  ['τσ', 'ts'],
  ['τζ', 'tz'],
  ['αι', 'e'],
  ['ει', 'i'],
  ['οι', 'i'],
  ['υι', 'i'],
  ['ου', 'ou'],
  ['αυ', 'av'],
  ['ευ', 'ev'],
];

const LETTER_MAP = {
  'α': 'a',
  'β': 'v',
  'γ': 'g',
  'δ': 'd',
  'ε': 'e',
  'ζ': 'z',
  'η': 'i',
  'θ': 'th',
  'ι': 'i',
  'κ': 'k',
  'λ': 'l',
  'μ': 'm',
  'ν': 'n',
  'ξ': 'x',
  'ο': 'o',
  'π': 'p',
  'ρ': 'r',
  'σ': 's',
  'ς': 's',
  'τ': 't',
  'υ': 'i',
  'φ': 'f',
  'χ': 'h',
  'ψ': 'ps',
  'ω': 'o',
};

const normalizeAccents = (text) =>
  text
    .split('')
    .map((char) => ACCENT_MAP[char] || char)
    .join('');

export const toGreeklish = (text) => {
  if (!text) return '';
  let output = normalizeAccents(text).toLowerCase();

  DIGRAPHS.forEach(([pattern, replacement]) => {
    output = output.replaceAll(pattern, replacement);
  });

  return output
    .split('')
    .map((char) => LETTER_MAP[char] || char)
    .join('');
};
