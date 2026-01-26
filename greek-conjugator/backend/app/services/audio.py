import os
import time
from collections import deque
from datetime import datetime

from google.cloud import texttospeech

from ..models import db, AudioUsage, Conjugation


class RateLimitError(Exception):
    pass


class AudioService:
    def __init__(self, cache_dir, rpm_limit=60, daily_char_limit=50000):
        self.cache_dir = cache_dir
        self.rpm_limit = rpm_limit
        self.daily_char_limit = daily_char_limit
        self._request_times = deque()
        os.makedirs(self.cache_dir, exist_ok=True)

    def _check_rpm_limit(self):
        now = time.time()
        while self._request_times and (now - self._request_times[0]) > 60:
            self._request_times.popleft()
        if len(self._request_times) >= self.rpm_limit:
            raise RateLimitError("TTS rate limit reached")
        self._request_times.append(now)

    def _get_or_create_usage(self):
        today = datetime.utcnow().strftime("%Y-%m-%d")
        usage = AudioUsage.query.filter_by(usage_date=today).first()
        if not usage:
            usage = AudioUsage(usage_date=today, chars_used=0, requests_count=0)
            db.session.add(usage)
            db.session.commit()
        return usage

    def _check_daily_limit(self, chars):
        usage = self._get_or_create_usage()
        if usage.chars_used + chars > self.daily_char_limit:
            raise RateLimitError("TTS daily character limit reached")
        usage.chars_used += chars
        usage.requests_count += 1
        usage.updated_at = datetime.utcnow()
        db.session.commit()

    def _synthesize(self, text, language_code="el-GR", voice_name=None):
        if not text:
            raise ValueError("Cannot synthesize empty text")

        self._check_rpm_limit()
        self._check_daily_limit(len(text))

        client = texttospeech.TextToSpeechClient()
        voice = texttospeech.VoiceSelectionParams(
            language_code=language_code,
            name=voice_name or "el-GR-Wavenet-A",
        )
        audio_config = texttospeech.AudioConfig(
            audio_encoding=texttospeech.AudioEncoding.MP3
        )
        response = client.synthesize_speech(
            input=texttospeech.SynthesisInput(text=text),
            voice=voice,
            audio_config=audio_config,
        )
        return response.audio_content

    def ensure_conjugation_audio(self, conjugation):
        if conjugation.audio_url:
            return conjugation.audio_url

        filename = f"conjugation_{conjugation.id}.mp3"
        file_path = os.path.join(self.cache_dir, filename)
        audio_bytes = self._synthesize(conjugation.form)
        with open(file_path, "wb") as f:
            f.write(audio_bytes)

        conjugation.audio_url = f"/api/audio/file/{filename}"
        db.session.commit()
        return conjugation.audio_url

    def ensure_vocab_audio(self, word_id):
        result = db.session.execute(
            db.text("SELECT id, word, audio_url FROM common_words WHERE id = :id"),
            {"id": word_id},
        ).fetchone()
        if not result:
            raise ValueError("Vocabulary word not found")

        row = dict(result._mapping)
        if row.get("audio_url"):
            return row["audio_url"]

        filename = f"vocab_{row['id']}.mp3"
        file_path = os.path.join(self.cache_dir, filename)
        audio_bytes = self._synthesize(row["word"])
        with open(file_path, "wb") as f:
            f.write(audio_bytes)

        audio_url = f"/api/audio/file/{filename}"
        db.session.execute(
            db.text("UPDATE common_words SET audio_url = :url WHERE id = :id"),
            {"url": audio_url, "id": row["id"]},
        )
        db.session.commit()
        return audio_url


def get_audio_service(app):
    cache_dir = app.config.get("AUDIO_CACHE_DIR")
    rpm_limit = app.config.get("TTS_RPM_LIMIT")
    daily_limit = app.config.get("TTS_DAILY_CHAR_LIMIT")
    return AudioService(cache_dir, rpm_limit=rpm_limit, daily_char_limit=daily_limit)
