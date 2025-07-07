from flask import Blueprint, jsonify, request
from ..services.greek_text import GreekTextProcessor, validate_greek, compare_greek_texts, latin_to_greek, greek_to_latin
from .auth import login_required

bp = Blueprint('text_validation', __name__, url_prefix='/api/text')


@bp.route('/validate', methods=['POST'])
@login_required
def validate_text():
    """
    Validate Greek text input
    
    Request body:
    {
        "text": "Greek text to validate"
    }
    
    Response:
    {
        "valid": true/false,
        "normalized": "normalized text",
        "has_greek": true/false,
        "character_count": 10,
        "invalid_characters": [],
        "warnings": []
    }
    """
    try:
        data = request.get_json()
        text = data.get('text', '')
        
        if not isinstance(text, str):
            return jsonify({'error': 'Text must be a string'}), 400
        
        validation_result = validate_greek(text)
        
        return jsonify(validation_result)
        
    except Exception as e:
        return jsonify({'error': f'Validation failed: {str(e)}'}), 500


@bp.route('/compare', methods=['POST'])
@login_required
def compare_texts():
    """
    Compare two Greek texts with accent-insensitive comparison
    
    Request body:
    {
        "text1": "first text",
        "text2": "second text",
        "strict": false  // optional, default false
    }
    
    Response:
    {
        "match": true/false,
        "similarity_score": 0.95,
        "suggestions": ["suggestion1", "suggestion2"]
    }
    """
    try:
        data = request.get_json()
        text1 = data.get('text1', '')
        text2 = data.get('text2', '')
        strict = data.get('strict', False)
        
        if not isinstance(text1, str) or not isinstance(text2, str):
            return jsonify({'error': 'Both texts must be strings'}), 400
        
        # Perform comparison
        if strict:
            # Strict comparison (exact match including accents)
            match = GreekTextProcessor.normalize_unicode(text1.strip()) == GreekTextProcessor.normalize_unicode(text2.strip())
        else:
            # Accent-insensitive comparison
            match = compare_greek_texts(text1, text2)
        
        # Calculate similarity score
        similarity_score = GreekTextProcessor.get_similarity_score(text1, text2)
        
        # Get suggestions if not a perfect match
        suggestions = []
        if not match and text2:
            suggestions = GreekTextProcessor.suggest_corrections(text1, text2)
        
        return jsonify({
            'match': match,
            'similarity_score': similarity_score,
            'suggestions': suggestions
        })
        
    except Exception as e:
        return jsonify({'error': f'Comparison failed: {str(e)}'}), 500


@bp.route('/transliterate', methods=['POST'])
@login_required
def transliterate_text():
    """
    Transliterate text between Latin and Greek
    
    Request body:
    {
        "text": "text to transliterate",
        "direction": "to_greek" or "to_latin"
    }
    
    Response:
    {
        "original": "original text",
        "transliterated": "transliterated text",
        "direction": "to_greek"
    }
    """
    try:
        data = request.get_json()
        text = data.get('text', '')
        direction = data.get('direction', 'to_greek')
        
        if not isinstance(text, str):
            return jsonify({'error': 'Text must be a string'}), 400
        
        if direction not in ['to_greek', 'to_latin']:
            return jsonify({'error': 'Direction must be "to_greek" or "to_latin"'}), 400
        
        if direction == 'to_greek':
            transliterated = latin_to_greek(text)
        else:
            transliterated = greek_to_latin(text)
        
        return jsonify({
            'original': text,
            'transliterated': transliterated,
            'direction': direction
        })
        
    except Exception as e:
        return jsonify({'error': f'Transliteration failed: {str(e)}'}), 500


@bp.route('/normalize', methods=['POST'])
@login_required
def normalize_text():
    """
    Normalize Greek text to standard Unicode form
    
    Request body:
    {
        "text": "Greek text to normalize"
    }
    
    Response:
    {
        "original": "original text",
        "normalized": "normalized text",
        "without_accents": "text without accents"
    }
    """
    try:
        data = request.get_json()
        text = data.get('text', '')
        
        if not isinstance(text, str):
            return jsonify({'error': 'Text must be a string'}), 400
        
        normalized = GreekTextProcessor.normalize_unicode(text)
        without_accents = GreekTextProcessor.remove_accents(text)
        
        return jsonify({
            'original': text,
            'normalized': normalized,
            'without_accents': without_accents
        })
        
    except Exception as e:
        return jsonify({'error': f'Normalization failed: {str(e)}'}), 500


@bp.route('/check-answer', methods=['POST'])
@login_required
def check_answer():
    """
    Check if a user's answer matches the correct answer with Greek text processing
    
    Request body:
    {
        "user_answer": "user's input",
        "correct_answer": "correct answer",
        "tolerance": "strict" or "lenient"  // optional, default "lenient"
    }
    
    Response:
    {
        "correct": true/false,
        "similarity_score": 0.95,
        "normalized_user_answer": "normalized user input",
        "normalized_correct_answer": "normalized correct answer",
        "suggestions": ["suggestion1", "suggestion2"],
        "feedback": "Detailed feedback message"
    }
    """
    try:
        data = request.get_json()
        user_answer = data.get('user_answer', '')
        correct_answer = data.get('correct_answer', '')
        tolerance = data.get('tolerance', 'lenient')
        
        if not isinstance(user_answer, str) or not isinstance(correct_answer, str):
            return jsonify({'error': 'Both answers must be strings'}), 400
        
        if tolerance not in ['strict', 'lenient']:
            return jsonify({'error': 'Tolerance must be "strict" or "lenient"'}), 400
        
        # Normalize both answers
        norm_user = GreekTextProcessor.normalize_unicode(user_answer.strip())
        norm_correct = GreekTextProcessor.normalize_unicode(correct_answer.strip())
        
        # Check correctness based on tolerance
        if tolerance == 'strict':
            # Exact match including accents
            correct = norm_user == norm_correct
        else:
            # Accent-insensitive comparison
            correct = compare_greek_texts(norm_user, norm_correct)
        
        # Calculate similarity score
        similarity_score = GreekTextProcessor.get_similarity_score(norm_user, norm_correct)
        
        # Get suggestions if not correct
        suggestions = []
        if not correct and norm_correct:
            suggestions = GreekTextProcessor.suggest_corrections(norm_user, norm_correct)
        
        # Generate feedback
        feedback = _generate_feedback(correct, similarity_score, suggestions, tolerance)
        
        return jsonify({
            'correct': correct,
            'similarity_score': similarity_score,
            'normalized_user_answer': norm_user,
            'normalized_correct_answer': norm_correct,
            'suggestions': suggestions,
            'feedback': feedback
        })
        
    except Exception as e:
        return jsonify({'error': f'Answer checking failed: {str(e)}'}), 500


@bp.route('/keyboard-mapping', methods=['GET'])
@login_required
def get_keyboard_mapping():
    """
    Get the transliteration mapping for the Greek keyboard
    
    Response:
    {
        "latin_to_greek": {...},
        "greek_to_latin": {...},
        "diacritics": {...}
    }
    """
    try:
        return jsonify({
            'latin_to_greek': GreekTextProcessor.TRANSLITERATION_MAP,
            'greek_to_latin': GreekTextProcessor.REVERSE_TRANSLITERATION,
            'diacritics': GreekTextProcessor.DIACRITICS
        })
        
    except Exception as e:
        return jsonify({'error': f'Failed to get keyboard mapping: {str(e)}'}), 500


def _generate_feedback(correct: bool, similarity_score: float, suggestions: list, tolerance: str) -> str:
    """Generate helpful feedback based on the answer checking results"""
    if correct:
        return "Correct! Well done!"
    
    if similarity_score >= 0.9:
        if suggestions:
            return f"Very close! {suggestions[0]}"
        else:
            return "Very close! Check your spelling carefully."
    elif similarity_score >= 0.7:
        return "Good attempt! Review the correct form and try again."
    elif similarity_score >= 0.5:
        return "Partially correct. Make sure you have the right word form."
    else:
        if suggestions:
            return f"Not quite right. {suggestions[0]}"
        else:
            return "Please try again. Make sure you're using the correct Greek form."


@bp.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint for the text validation service"""
    return jsonify({
        'status': 'healthy',
        'service': 'Greek Text Validation API',
        'version': '1.0.0'
    })