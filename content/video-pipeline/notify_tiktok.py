#!/usr/bin/env python3
"""
notify_tiktok.py — Telegram алерт для ручної публікації TikTok
Надсилає caption і посилання на відео власнику проекту
"""

import argparse
import json
import os
from datetime import datetime

import requests


def load_config(mage: str) -> dict:
    """Завантажує конфіг мага з JSON файлу."""
    config_path = os.path.join(os.path.dirname(__file__), 'configs', f'{mage}.json')
    with open(config_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def read_script_teaser(mage: str, date_str: str) -> str:
    """Читає перші 2 речення скрипту як тизер."""
    script_path = os.path.join(os.path.dirname(__file__), 'output', f'{mage}_script_{date_str}.txt')
    with open(script_path, 'r', encoding='utf-8') as f:
        text = f.read().strip()
    sentences = [s.strip() for s in text.split('.') if s.strip()]
    teaser = '. '.join(sentences[:2]) + '.' if len(sentences) >= 2 else text
    return teaser


def read_video_url(mage: str, date_str: str) -> str:
    """Читає публічний URL відео."""
    url_path = os.path.join(os.path.dirname(__file__), 'output', f'{mage}_video_url_{date_str}.txt')
    with open(url_path, 'r', encoding='utf-8') as f:
        return f.read().strip()


def build_message(config: dict, teaser: str, video_url: str) -> str:
    """Формує повідомлення для власника про TikTok."""
    mage = config['mage']
    emoji = config['emoji']
    cta = config['cta']
    bio_link = config['bio_link']
    hashtags = ' '.join(f'#{h}' for h in config['tiktok_hashtags'][:5])

    lines = [
        f'🎬 {mage} відео готове для TikTok!',
        '',
        '📱 Caption (скопіюй):',
        teaser,
        '',
        f'{emoji} {cta} → {bio_link}',
        '',
        hashtags,
        '',
        f'📎 Відео: {video_url}',
        '',
        '⏰ Найкращий час публікації: 12:00-15:00 за Києвом',
    ]
    return '\n'.join(lines)


def send_notification(config: dict, mage: str, date_str: str) -> None:
    """Надсилає особисте повідомлення в Telegram."""
    token = os.environ['TELEGRAM_ALERT_BOT_TOKEN']
    admin_id = os.environ.get('ADMIN_TELEGRAM_ID', '6127139155')
    teaser = read_script_teaser(mage, date_str)
    video_url = read_video_url(mage, date_str)
    message = build_message(config, teaser, video_url)

    url = f'https://api.telegram.org/bot{token}/sendMessage'
    payload = {
        'chat_id': admin_id,
        'text': message,
        'parse_mode': 'HTML',
        'disable_web_page_preview': False,
    }
    r = requests.post(url, json=payload, timeout=30)
    r.raise_for_status()
    print(f'[{config["mage"]}] ✅ TikTok алерт надіслано адміну')


def main() -> None:
    parser = argparse.ArgumentParser(description='Telegram алерт для ручної публікації TikTok')
    parser.add_argument('--mage', required=True, choices=['luna', 'arcas', 'numi', 'umbra'])
    args = parser.parse_args()

    date_str = datetime.now().strftime('%Y-%m-%d')
    config = load_config(args.mage)
    mage = config['mage']

    try:
        send_notification(config, args.mage, date_str)
    except Exception as e:
        print(f'⚠️ [{mage}] Помилка TikTok алерту: {e}')


if __name__ == '__main__':
    main()
