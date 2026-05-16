#!/usr/bin/env python3
"""
publish_twitter.py — Публікація твіту від Academy через Twitter API v2
Використовує tweepy, публікує від ACADEMY акаунту
"""

import argparse
import json
import os
import sys
from datetime import datetime

import requests
import tweepy


def load_config(mage: str) -> dict:
    """Завантажує конфіг мага з JSON файлу."""
    config_path = os.path.join(os.path.dirname(__file__), 'configs', f'{mage}.json')
    with open(config_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def send_telegram_alert(message: str) -> None:
    """Надсилає Telegram алерт через загального бота."""
    token = os.environ.get('TELEGRAM_ALERT_BOT_TOKEN')
    chat_id = os.environ.get('LUMARA_TELEGRAM_CHANNEL_ID')
    if not token or not chat_id:
        print(f'[ALERT] {message}')
        return
    try:
        requests.post(
            f'https://api.telegram.org/bot{token}/sendMessage',
            json={'chat_id': chat_id, 'text': message, 'parse_mode': 'HTML'},
            timeout=10,
        )
    except Exception as e:
        print(f'[ALERT FAIL] {e}')


def read_script(mage: str, date_str: str) -> str:
    """Читає повний скрипт."""
    script_path = os.path.join(os.path.dirname(__file__), 'output', f'{mage}_script_{date_str}.txt')
    with open(script_path, 'r', encoding='utf-8') as f:
        return f.read().strip()


def generate_twitter_text(script: str, config: dict) -> str:
    """Генерує твіт через Claude API на основі скрипту."""
    import anthropic

    client = anthropic.Anthropic(api_key=os.environ['ANTHROPIC_API_KEY'])
    mage = config['mage']
    emoji = config['emoji']

    user_prompt = (
        f'На основі цього скрипту створи твіт до 220 символів.\n'
        f'Від імені LUMARA Academy. Гострий інсайт від {mage}.\n'
        f'Без посилань в тексті (посилання в біо). 2-3 хештеги.\n'
        f'Формат: "{{інсайт}}" — {emoji} {mage}, LUMARA\n#{{tag1}} #{{tag2}}\n\n'
        f'Скрипт:\n{script}'
    )

    response = client.messages.create(
        model='claude-sonnet-4-6',
        max_tokens=200,
        messages=[{'role': 'user', 'content': user_prompt}],
    )
    tweet = response.content[0].text.strip()
    return tweet[:280]


def post_tweet(text: str) -> None:
    """Публікує твіт через Twitter API v2."""
    client = tweepy.Client(
        consumer_key=os.environ['ACADEMY_TWITTER_API_KEY'],
        consumer_secret=os.environ['ACADEMY_TWITTER_API_SECRET'],
        access_token=os.environ['ACADEMY_TWITTER_ACCESS_TOKEN'],
        access_token_secret=os.environ['ACADEMY_TWITTER_ACCESS_SECRET'],
    )
    client.create_tweet(text=text)


def main() -> None:
    parser = argparse.ArgumentParser(description='Публікація Twitter твіту від Academy')
    parser.add_argument('--mage', required=True, choices=['luna', 'arcas', 'numi', 'umbra'])
    args = parser.parse_args()

    date_str = datetime.now().strftime('%Y-%m-%d')
    config = load_config(args.mage)
    mage = config['mage']

    try:
        script = read_script(args.mage, date_str)
        twitter_text = generate_twitter_text(script, config)
        print(f'[{mage}→ACADEMY] 📝 Твіт: {twitter_text[:80]}...')
        post_tweet(twitter_text)
        print(f'[{mage}→ACADEMY] ✅ Twitter твіт опубліковано')
    except Exception as e:
        error_msg = f'⚠️ [{mage}→ACADEMY] Помилка Twitter: {e}'
        print(error_msg)
        send_telegram_alert(error_msg)
        sys.exit(0)


if __name__ == '__main__':
    main()
