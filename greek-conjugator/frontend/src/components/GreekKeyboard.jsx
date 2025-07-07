import React, { useState, useEffect, useRef } from 'react';
import { textValidationService } from '../services/api';

const GreekKeyboard = ({ 
  onTextChange, 
  value = '', 
  placeholder = "Type in Greek or Latin...", 
  autoTransliterate = true,
  showValidation = false,
  correctAnswer = null,
  disabled = false
}) => {
  const [showVirtualKeyboard, setShowVirtualKeyboard] = useState(false);
  const [transliterationMode, setTransliterationMode] = useState(true);
  const [showAccents, setShowAccents] = useState(false);
  const [isMobile, setIsMobile] = useState(false);
  const [validationResult, setValidationResult] = useState(null);
  const [keyboardLayout, setKeyboardLayout] = useState('basic');
  const inputRef = useRef(null);
  const debounceTimeoutRef = useRef(null);

  // Detect mobile device
  useEffect(() => {
    const checkMobile = () => {
      setIsMobile(window.innerWidth <= 768 || 'ontouchstart' in window);
    };
    checkMobile();
    window.addEventListener('resize', checkMobile);
    return () => window.removeEventListener('resize', checkMobile);
  }, []);

  // Enhanced Greek keyboard layouts
  const keyboardLayouts = {
    basic: [
      ['α', 'β', 'γ', 'δ', 'ε', 'ζ', 'η', 'θ', 'ι', 'κ'],
      ['λ', 'μ', 'ν', 'ξ', 'ο', 'π', 'ρ', 'σ', 'τ', 'υ'],
      ['φ', 'χ', 'ψ', 'ω', 'ς']
    ],
    accented: [
      ['ά', 'έ', 'ή', 'ί', 'ό', 'ύ', 'ώ'],
      ['ΐ', 'ΰ', 'ϊ', 'ϋ'],
      ['ἀ', 'ἁ', 'ἐ', 'ἑ', 'ἠ', 'ἡ', 'ἰ', 'ἱ', 'ὀ', 'ὁ'],
      ['ὐ', 'ὑ', 'ὠ', 'ὡ']
    ],
    uppercase: [
      ['Α', 'Β', 'Γ', 'Δ', 'Ε', 'Ζ', 'Η', 'Θ', 'Ι', 'Κ'],
      ['Λ', 'Μ', 'Ν', 'Ξ', 'Ο', 'Π', 'Ρ', 'Σ', 'Τ', 'Υ'],
      ['Φ', 'Χ', 'Ψ', 'Ω']
    ]
  };

  // Common Greek diacritics
  const diacritics = [
    { name: 'acute', symbol: '́', description: 'Acute accent' },
    { name: 'grave', symbol: '̀', description: 'Grave accent' },
    { name: 'circumflex', symbol: '͂', description: 'Circumflex' },
    { name: 'diaeresis', symbol: '̈', description: 'Diaeresis' },
    { name: 'rough', symbol: '̔', description: 'Rough breathing' },
    { name: 'smooth', symbol: '̓', description: 'Smooth breathing' },
    { name: 'iota_subscript', symbol: 'ͅ', description: 'Iota subscript' }
  ];

  // Debounced validation
  useEffect(() => {
    if (showValidation && value && correctAnswer) {
      if (debounceTimeoutRef.current) {
        clearTimeout(debounceTimeoutRef.current);
      }
      
      debounceTimeoutRef.current = setTimeout(async () => {
        try {
          const result = await textValidationService.checkAnswer(value, correctAnswer, 'lenient');
          setValidationResult(result);
        } catch (error) {
          console.error('Validation error:', error);
        }
      }, 500);
    }

    return () => {
      if (debounceTimeoutRef.current) {
        clearTimeout(debounceTimeoutRef.current);
      }
    };
  }, [value, correctAnswer, showValidation]);

  // Handle input changes with real-time transliteration
  const handleInputChange = async (e) => {
    const inputText = e.target.value;
    
    if (autoTransliterate && transliterationMode) {
      try {
        const result = await textValidationService.transliterate(inputText, 'to_greek');
        onTextChange(result.transliterated);
      } catch (error) {
        // Fallback to client-side transliteration
        const transliterated = clientSideTransliterate(inputText);
        onTextChange(transliterated);
      }
    } else {
      onTextChange(inputText);
    }
  };

  // Client-side transliteration fallback
  const clientSideTransliterate = (text) => {
    const mapping = {
      'th': 'θ', 'ch': 'χ', 'ps': 'ψ', 'au': 'αυ', 'eu': 'ευ', 'ou': 'ου',
      'ai': 'αι', 'ei': 'ει', 'oi': 'οι', 'ui': 'υι',
      'a': 'α', 'b': 'β', 'g': 'γ', 'd': 'δ', 'e': 'ε', 'z': 'ζ', 'h': 'η',
      'i': 'ι', 'k': 'κ', 'l': 'λ', 'm': 'μ', 'n': 'ν', 'x': 'ξ', 'o': 'ο',
      'p': 'π', 'r': 'ρ', 's': 'σ', 't': 'τ', 'u': 'υ', 'f': 'φ', 'w': 'ω',
      'y': 'υ', 'v': 'β', 'c': 'κ', 'j': 'ι'
    };

    let result = text;
    
    // Sort by length (longer first) to handle digraphs correctly
    const sortedMappings = Object.entries(mapping).sort((a, b) => b[0].length - a[0].length);
    
    for (const [latin, greek] of sortedMappings) {
      const regex = new RegExp(latin, 'gi');
      result = result.replace(regex, (match) => 
        match === match.toUpperCase() ? greek.toUpperCase() : greek
      );
    }
    
    return result;
  };

  // Handle virtual keyboard key press
  const handleVirtualKeyPress = (key) => {
    const cursorPosition = inputRef.current?.selectionStart || value.length;
    const newValue = value.slice(0, cursorPosition) + key + value.slice(cursorPosition);
    onTextChange(newValue);
    
    // Move cursor to after the inserted character
    setTimeout(() => {
      if (inputRef.current) {
        inputRef.current.focus();
        inputRef.current.setSelectionRange(cursorPosition + key.length, cursorPosition + key.length);
      }
    }, 0);
  };

  // Handle backspace
  const handleBackspace = () => {
    const cursorPosition = inputRef.current?.selectionStart || value.length;
    if (cursorPosition > 0) {
      const newValue = value.slice(0, cursorPosition - 1) + value.slice(cursorPosition);
      onTextChange(newValue);
      
      setTimeout(() => {
        if (inputRef.current) {
          inputRef.current.focus();
          inputRef.current.setSelectionRange(cursorPosition - 1, cursorPosition - 1);
        }
      }, 0);
    }
  };

  // Handle clear
  const handleClear = () => {
    onTextChange('');
    if (inputRef.current) {
      inputRef.current.focus();
    }
  };

  // Add diacritic to last character
  const addDiacritic = (diacritic) => {
    if (value.length > 0) {
      const lastChar = value[value.length - 1];
      const newValue = value.slice(0, -1) + lastChar + diacritic;
      onTextChange(newValue);
    }
  };

  // Get input styling based on validation
  const getInputStyling = () => {
    let baseClasses = "w-full px-4 py-3 text-lg border-2 rounded-lg focus:outline-none font-greek transition-colors";
    
    if (disabled) {
      baseClasses += " bg-gray-100 cursor-not-allowed";
    }
    
    if (showValidation && validationResult) {
      if (validationResult.correct) {
        baseClasses += " border-green-500 bg-green-50";
      } else if (validationResult.similarity_score > 0.7) {
        baseClasses += " border-yellow-500 bg-yellow-50";
      } else {
        baseClasses += " border-red-500 bg-red-50";
      }
    } else {
      baseClasses += " border-blue-300 focus:border-blue-500";
    }
    
    return baseClasses;
  };

  return (
    <div className="w-full">
      {/* Input field */}
      <div className="relative">
        <input
          ref={inputRef}
          type="text"
          value={value}
          onChange={handleInputChange}
          placeholder={placeholder}
          disabled={disabled}
          className={getInputStyling()}
          style={{ fontFamily: 'Georgia, "Times New Roman", serif' }}
          onFocus={() => isMobile && setShowVirtualKeyboard(true)}
        />

        {/* Input controls */}
        <div className="absolute right-2 top-1/2 transform -translate-y-1/2 flex gap-1">
          {/* Transliteration toggle */}
          <button
            onClick={() => setTransliterationMode(!transliterationMode)}
            className={`p-1 rounded text-sm ${transliterationMode ? 'text-blue-600' : 'text-gray-400'}`}
            type="button"
            title="Toggle transliteration"
          >
            Aa→Αα
          </button>

          {/* Virtual keyboard toggle */}
          <button
            onClick={() => setShowVirtualKeyboard(!showVirtualKeyboard)}
            className="p-1 text-blue-600 hover:text-blue-800"
            type="button"
            title="Toggle virtual keyboard"
          >
            ⌨️
          </button>

          {/* Clear button */}
          {value && (
            <button
              onClick={handleClear}
              className="p-1 text-red-600 hover:text-red-800"
              type="button"
              title="Clear input"
            >
              ✕
            </button>
          )}
        </div>
      </div>

      {/* Validation feedback */}
      {showValidation && validationResult && (
        <div className={`mt-2 p-2 rounded text-sm ${
          validationResult.correct 
            ? 'bg-green-100 text-green-800' 
            : validationResult.similarity_score > 0.7
            ? 'bg-yellow-100 text-yellow-800'
            : 'bg-red-100 text-red-800'
        }`}>
          {validationResult.feedback}
          {validationResult.suggestions.length > 0 && (
            <div className="mt-1 text-xs">
              <strong>Suggestions:</strong> {validationResult.suggestions.join(', ')}
            </div>
          )}
        </div>
      )}

      {/* Virtual keyboard */}
      {showVirtualKeyboard && (
        <div className="mt-3 p-4 bg-gray-50 rounded-lg border shadow-lg">
          {/* Keyboard header */}
          <div className="flex justify-between items-center mb-3">
            <div className="text-sm font-medium text-gray-700">Greek Virtual Keyboard</div>
            <div className="flex gap-2">
              {/* Layout selector */}
              <select
                value={keyboardLayout}
                onChange={(e) => setKeyboardLayout(e.target.value)}
                className="text-xs px-2 py-1 border rounded"
              >
                <option value="basic">Basic</option>
                <option value="accented">Accented</option>
                <option value="uppercase">Uppercase</option>
              </select>
              
              {/* Close button */}
              <button
                onClick={() => setShowVirtualKeyboard(false)}
                className="text-gray-500 hover:text-gray-700"
                type="button"
              >
                ✕
              </button>
            </div>
          </div>

          {/* Keyboard layout */}
          <div className="space-y-2">
            {keyboardLayouts[keyboardLayout].map((row, rowIndex) => (
              <div key={rowIndex} className="flex justify-center gap-1 flex-wrap">
                {row.map((key) => (
                  <button
                    key={key}
                    onClick={() => handleVirtualKeyPress(key)}
                    className="px-3 py-2 bg-white border border-gray-300 rounded hover:bg-blue-50 text-lg font-greek transition-colors min-w-[40px]"
                    style={{ fontFamily: 'Georgia, "Times New Roman", serif' }}
                    type="button"
                  >
                    {key}
                  </button>
                ))}
              </div>
            ))}
          </div>

          {/* Diacritics panel */}
          {keyboardLayout === 'basic' && (
            <div className="mt-3 pt-3 border-t">
              <div className="text-xs text-gray-600 mb-2">Diacritics (add to last character):</div>
              <div className="flex flex-wrap gap-1">
                {diacritics.map((diacritic) => (
                  <button
                    key={diacritic.name}
                    onClick={() => addDiacritic(diacritic.symbol)}
                    className="px-2 py-1 bg-white border border-gray-300 rounded hover:bg-blue-50 text-sm"
                    type="button"
                    title={diacritic.description}
                  >
                    {diacritic.symbol}
                  </button>
                ))}
              </div>
            </div>
          )}

          {/* Control buttons */}
          <div className="flex justify-center gap-2 mt-4 pt-3 border-t">
            <button
              onClick={() => handleVirtualKeyPress(' ')}
              className="px-6 py-2 bg-white border border-gray-300 rounded hover:bg-blue-50"
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
              onClick={handleClear}
              className="px-4 py-2 bg-yellow-100 border border-yellow-300 rounded hover:bg-yellow-200"
              type="button"
            >
              Clear
            </button>
          </div>
        </div>
      )}

      {/* Help text */}
      <div className="mt-2 text-sm text-gray-600">
        💡 {transliterationMode 
          ? "Type Latin characters (e.g., 'grapho' → 'γραφω')" 
          : "Type Greek characters directly"}
        {isMobile && " • Tap ⌨️ for virtual keyboard"}
      </div>
    </div>
  );
};

// Enhanced text comparison function using the new backend API
export const compareGreekTexts = async (userInput, correctAnswer, tolerance = 'lenient') => {
  try {
    const response = await textValidationService.checkAnswer(userInput, correctAnswer, tolerance);
    return response.correct;
  } catch (error) {
    console.error('API comparison failed, falling back to client-side:', error);
    // Fallback to client-side comparison
    return clientSideCompare(userInput, correctAnswer);
  }
};

// Client-side comparison fallback
const clientSideCompare = (userInput, correctAnswer) => {
  const removeAccents = (text) => {
    return text.replace(/[άἀἁἂἃἄἅἆἇᾀᾁᾂᾃᾄᾅᾆᾇᾲᾳᾴᾶᾷ]/g, 'α')
      .replace(/[έἐἑἒἓἔἕ]/g, 'ε')
      .replace(/[ήἠἡἢἣἤἥἦἧᾐᾑᾒᾓᾔᾕᾖᾗῂῃῄῆῇ]/g, 'η')
      .replace(/[ίἰἱἲἳἴἵἶἷῐῑῒΐῖῗ]/g, 'ι')
      .replace(/[όὀὁὂὃὄὅ]/g, 'ο')
      .replace(/[ύὐὑὒὓὔὕὖὗῠῡῢΰῦῧ]/g, 'υ')
      .replace(/[ώὠὡὢὣὤὥὦὧᾠᾡᾢᾣᾤᾥᾦᾧῲῳῴῶῷ]/g, 'ω')
      .replace(/ς/g, 'σ'); // Convert final sigma
  };

  const normalizedInput = removeAccents(userInput.toLowerCase().trim());
  const normalizedCorrect = removeAccents(correctAnswer.toLowerCase().trim());

  return normalizedInput === normalizedCorrect;
};

// Export the comparison function for backwards compatibility
export const acceptVariations = clientSideCompare;

export default GreekKeyboard;