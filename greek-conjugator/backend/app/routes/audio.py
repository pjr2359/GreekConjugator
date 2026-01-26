import os
from flask import Blueprint, jsonify, send_from_directory, current_app
from ..models import Conjugation
from .auth import login_required
from ..services.audio import get_audio_service, RateLimitError

bp = Blueprint('audio', __name__, url_prefix='/api/audio')


@bp.route('/file/<path:filename>', methods=['GET'])
def serve_audio_file(filename):
    cache_dir = current_app.config.get("AUDIO_CACHE_DIR")
    return send_from_directory(cache_dir, filename)


@bp.route('/conjugation/<int:conjugation_id>', methods=['POST'])
@login_required
def generate_conjugation_audio(conjugation_id):
    try:
        conjugation = Conjugation.query.get_or_404(conjugation_id)
        service = get_audio_service(current_app)
        audio_url = service.ensure_conjugation_audio(conjugation)
        return jsonify({"audio_url": audio_url})
    except RateLimitError as e:
        return jsonify({"error": str(e)}), 429
    except Exception as e:
        return jsonify({"error": f"Failed to generate audio: {str(e)}"}), 500


@bp.route('/vocabulary/<int:word_id>', methods=['POST'])
@login_required
def generate_vocab_audio(word_id):
    try:
        service = get_audio_service(current_app)
        audio_url = service.ensure_vocab_audio(word_id)
        return jsonify({"audio_url": audio_url})
    except RateLimitError as e:
        return jsonify({"error": str(e)}), 429
    except Exception as e:
        return jsonify({"error": f"Failed to generate audio: {str(e)}"}), 500
