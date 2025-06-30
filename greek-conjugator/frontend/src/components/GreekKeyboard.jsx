import React, { useState } from 'react';

const GreekKeyboard = ({ onTextChange, value = '', placeholder = "Type in Greek or Latin..." }) => {
  const [showVirtualKeyboard, setShowVirtualKeyboard] = useState(false);

  // Greek to Latin transliteration mapping
  const greekToLatin = {
    'α': 'a', 'β': 'b', 'γ': 'g', 'δ': 'd', 'ε': 'e', 'ζ': 'z', 'η': 'h', 'θ': 'th',
    'ι': 'i', 'κ': 'k', 'λ': 'l', 'μ': 'm', 'ν': 'n', 'ξ': 'x', 'ο': 'o', 'π': 'p',
    'ρ': 'r', 'σ': 's', 'ς': 's', 'τ': 't', 'υ': 'u', 'φ': 'f', 'χ': 'ch', 'ψ': 'ps', 'ω': 'w'
  };

  // Latin to Greek transliteration mapping
  const latinToGreek = {
    'a': 'α', 'b': 'β', 'g': 'γ', 'd': 'δ', 'e': 'ε', 'z': 'ζ', 'h': 'η', 'th': 'θ',
    'i': 'ι', 'k': 'κ', 'l': 'λ', 'm': 'μ', 'n': 'ν', 'x': 'ξ', 'o': 'ο', 'p': 'π',
    'r': 'ρ', 's': 'σ', 't': 'τ', 'u': 'υ', 'f': 'φ', 'ch': 'χ', 'ps': 'ψ', 'w': 'ω'
  };

  // Greek keyboard layout
  const greekKeys = [
    ['α', 'β', 'γ', 'δ', 'ε', 'ζ', 'η', 'θ', 'ι', 'κ'],
    ['λ', 'μ', 'ν', 'ξ', 'ο', 'π', 'ρ', 'σ', 'τ', 'υ'],
    ['φ', 'χ', 'ψ', 'ω', 'ς', 'ά', 'έ', 'ή', 'ί', 'ό'],
    ['ύ', 'ώ', 'ΐ', 'ΰ']
  ];

  const transliterateToGreek = (text) => {
    let result = text;

    // Handle special combinations first
    result = result.replace(/th/gi, 'θ');
    result = result.replace(/ch/gi, 'χ');
    result = result.replace(/ps/gi, 'ψ');

    // Then handle single characters
    result = result.split('').map(char => {
      const lower = char.toLowerCase();
      if (latinToGreek[lower]) {
        return char === char.toUpperCase() ? latinToGreek[lower].toUpperCase() : latinToGreek[lower];
      }
      return char;
    }).join('');

    return result;
  };

  const handleInputChange = (e) => {
    const inputText = e.target.value;
    const transliterated = transliterateToGreek(inputText);
    onTextChange(transliterated);
  };

  const handleVirtualKeyPress = (key) => {
    const newValue = value + key;
    onTextChange(newValue);
  };

  const handleBackspace = () => {
    const newValue = value.slice(0, -1);
    onTextChange(newValue);
  };

  const acceptVariations = (userInput, correctAnswer) => {
    // Remove accents for comparison
    const removeAccents = (text) => {
      return text.replace(/[άἀἁἂἃἄἅἆἇᾀᾁᾂᾃᾄᾅᾆᾇᾲᾳᾴᾶᾷ]/g, 'α')
        .replace(/[έἐἑἒἓἔἕ]/g, 'ε')
        .replace(/[ήἠἡἢἣἤἥἦἧᾐᾑᾒᾓᾔᾕᾖᾗῂῃῄῆῇ]/g, 'η')
        .replace(/[ίἰἱἲἳἴἵἶἷῐῑῒΐῖῗ]/g, 'ι')
        .replace(/[όὀὁὂὃὄὅ]/g, 'ο')
        .replace(/[ύὐὑὒὓὔὕὖὗῠῡῢΰῦῧ]/g, 'υ')
        .replace(/[ώὠὡὢὣὤὥὦὧᾠᾡᾢᾣᾤᾥᾦᾧῲῳῴῶῷ]/g, 'ω');
    };

    const normalizedInput = removeAccents(userInput.toLowerCase().trim());
    const normalizedCorrect = removeAccents(correctAnswer.toLowerCase().trim());

    return normalizedInput === normalizedCorrect;
  };

  return (
    <div className="w-full">
      <div className="relative">
        <input
          type="text"
          value={value}
          onChange={handleInputChange}
          placeholder={placeholder}
          className="w-full px-4 py-3 text-lg border-2 border-blue-300 rounded-lg focus:border-blue-500 focus:outline-none font-greek"
          style={{ fontFamily: 'Georgia, "Times New Roman", serif' }}
        />

        <button
          onClick={() => setShowVirtualKeyboard(!showVirtualKeyboard)}
          className="absolute right-3 top-1/2 transform -translate-y-1/2 text-blue-600 hover:text-blue-800"
          type="button"
        >
          ⌨️
        </button>
      </div>

      {showVirtualKeyboard && (
        <div className="mt-3 p-4 bg-gray-100 rounded-lg border">
          <div className="text-sm text-gray-600 mb-2">Greek Virtual Keyboard</div>
          {greekKeys.map((row, rowIndex) => (
            <div key={rowIndex} className="flex justify-center gap-1 mb-2">
              {row.map((key) => (
                <button
                  key={key}
                  onClick={() => handleVirtualKeyPress(key)}
                  className="px-3 py-2 bg-white border border-gray-300 rounded hover:bg-blue-50 text-lg font-greek"
                  style={{ fontFamily: 'Georgia, "Times New Roman", serif' }}
                  type="button"
                >
                  {key}
                </button>
              ))}
            </div>
          ))}

          <div className="flex justify-center gap-2 mt-3">
            <button
              onClick={() => handleVirtualKeyPress(' ')}
              className="px-8 py-2 bg-white border border-gray-300 rounded hover:bg-blue-50"
              type="button"
            >
              Space
            </button>
            <button
              onClick={handleBackspace}
              className="px-4 py-2 bg-red-100 border border-red-300 rounded hover:bg-red-200"
              type="button"
            >
              ⌫
            </button>
            <button
              onClick={() => setShowVirtualKeyboard(false)}
              className="px-4 py-2 bg-gray-200 border border-gray-300 rounded hover:bg-gray-300"
              type="button"
            >
              Hide
            </button>
          </div>
        </div>
      )}

      <div className="mt-2 text-sm text-gray-600">
        💡 Tip: Type "grapho" to get "γραφω", or use the virtual keyboard above
      </div>
    </div>
  );
};

// Export the acceptVariations function for use in other components
export const acceptVariations = (userInput, correctAnswer) => {
  const removeAccents = (text) => {
    return text.replace(/[άἀἁἂἃἄἅἆἇᾀᾁᾂᾃᾄᾅᾆᾇᾲᾳᾴᾶᾷ]/g, 'α')
      .replace(/[έἐἑἒἓἔἕ]/g, 'ε')
      .replace(/[ήἠἡἢἣἤἥἦἧᾐᾑᾒᾓᾔᾕᾖᾗῂῃῄῆῇ]/g, 'η')
      .replace(/[ίἰἱἲἳἴἵἶἷῐῑῒΐῖῗ]/g, 'ι')
      .replace(/[όὀὁὂὃὄὅ]/g, 'ο')
      .replace(/[ύὐὑὒὓὔὕὖὗῠῡῢΰῦῧ]/g, 'υ')
      .replace(/[ώὠὡὢὣὤὥὦὧᾠᾡᾢᾣᾤᾥᾦᾧῲῳῴῶῷ]/g, 'ω');
  };

  const normalizedInput = removeAccents(userInput.toLowerCase().trim());
  const normalizedCorrect = removeAccents(correctAnswer.toLowerCase().trim());

  return normalizedInput === normalizedCorrect;
};

export default GreekKeyboard;