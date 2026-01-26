#!/usr/bin/env python3
import argparse
from app import create_app
from app.models import db, Verb, Conjugation
from app.services.audio import get_audio_service, RateLimitError


def get_top_verbs(limit):
    return (Verb.query
            .order_by(Verb.frequency.is_(None), Verb.frequency)
            .limit(limit)
            .all())


def get_top_vocab_ids(limit):
    result = db.session.execute(
        db.text("""
            SELECT id FROM common_words
            ORDER BY (frequency_rank IS NULL), frequency_rank
            LIMIT :limit
        """),
        {"limit": limit}
    ).fetchall()
    return [row[0] for row in result]


def prefill_audio(verb_limit, vocab_limit):
    app = create_app()
    with app.app_context():
        service = get_audio_service(app)

        # Prefill conjugations for top verbs
        verbs = get_top_verbs(verb_limit)
        verb_ids = [v.id for v in verbs]
        conjugations = (Conjugation.query
                        .filter(Conjugation.verb_id.in_(verb_ids))
                        .all())
        print(f"Found {len(conjugations)} conjugations for top {verb_limit} verbs")
        for conj in conjugations:
            if conj.audio_url:
                continue
            try:
                service.ensure_conjugation_audio(conj)
            except RateLimitError as e:
                print(f"Rate limit hit while generating conjugation audio: {e}")
                return

        # Prefill vocabulary audio for top words
        vocab_ids = get_top_vocab_ids(vocab_limit)
        print(f"Found {len(vocab_ids)} vocab items to generate")
        for word_id in vocab_ids:
            try:
                service.ensure_vocab_audio(word_id)
            except RateLimitError as e:
                print(f"Rate limit hit while generating vocab audio: {e}")
                return

        print("Audio prefill complete.")


def main():
    parser = argparse.ArgumentParser(description="Prefill audio for top verbs and vocabulary.")
    parser.add_argument("--verbs", type=int, default=200, help="Number of top verbs to prefill")
    parser.add_argument("--vocab", type=int, default=1000, help="Number of top vocab words to prefill")
    args = parser.parse_args()
    prefill_audio(args.verbs, args.vocab)


if __name__ == "__main__":
    main()
