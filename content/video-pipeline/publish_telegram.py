#!/usr/bin/env python3
"""
publish_telegram.py — Анонс відео в Telegram канал мага
"""

import argparse
import json
import os
import sys
from datetime import datetime

import requests


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


def read_script_teaser(mage: str, date_str: str) -> str:
    """Читає перші 2 речення скрипту як тизер."""
    script_path = os.path.join(os.path.dirname(__file__), 'output', f'{mage}_script_{date_str}.txt')
    with open(script_path, 'r', encoding='utf-8') as f:
        text = f.read().strip()
    sentences = [s.strip() for s in text.split('.') if s.strip()]
    teaser = '. '.join(sentences[:2]) + '.' if len(sentences) >= 2 else text
    return teaser


def build_message(config: dict, teaser: str) -> str:
    """Формує повідомлення для Telegram каналу."""
    mage = config['mage']
    emoji = config['emoji']
    bio_link = config['bio_link']
    # Беремо перші 2 теми для хештегів
    topics = [t.strip() for t in config['topic'].split(',') if t.strip()]
    topic_tags = ' '.join(f'#{t.replace(" ", "")}' for t in topics[:2])

    lines = [
        f'{emoji} Нове відео від {mage}',
        '',
        teaser,
        '',
        '▶️ Дивись в Instagram та TikTok',
        f'🔗 {bio_link}',
        '',
        f'#{config["mage_lower"]} #lumara {topic_tags}',
    ]
    return '\n'.join(lines)


def publish_to_telegram(config: dict, mage: str, date_str: str) -> None:
    """Надсилає анонс в Telegram канал мага."""
    bot_token = os.environ[config['telegram_bot_token_secret']]
    channel_id = config['telegram_channel_id']
    teaser = read_script_teaser(mage, date_str)
    message = build_message(config, teaser)

    url = f'https://api.telegram.org/bot{bot_token}/sendMessage'
    payload = {
        'chat_id': channel_id,
        'text': message,
        'parse_mode': 'HTML',
        'disable_web_page_preview': False,
    }
    r = requests.post(url, json=payload, timeout=30)
    r.raise_for_status()
    print(f'[{config["mage"]}] ✅ Telegram анонс надіслано')


def main() -> None:
    parser = argparse.ArgumentParser(description='Анонс відео в Telegram канал мага')
    parser.add_argument('--mage', required=True, choices=['luna', 'arcas', 'numi', 'umbra'])
    args = parser.parse_args()

    date_str = datetime.now().strftime('%Y-%m-%d')
    config = load_config(args.mage)
    mage = config['mage']

    try:
        publish_to_telegram(config, args.mage, date_str)
        print(f'[{mage}] ✅ Telegram анонс надіслано в канал')
    except Exception as e:
        error_msg = f'⚠️ [{mage}] Помилка Telegram анонсу: {e}'
        print(error_msg)
        send_telegram_alert(error_msg)
        sys.exit(0)


if __name__ == '__main__':
    main()
