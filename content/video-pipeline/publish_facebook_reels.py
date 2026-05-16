#!/usr/bin/env python3
"""
publish_facebook_reels.py — Публікація Facebook Reels через Graph API
Після публікації — перший коментар з редіректами (з meta_publisher.py)
"""

import argparse
import json
import os
import sys
import time
from datetime import datetime

import requests

# Додаємо шлях до meta_publisher.py в репо
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'packages', 'agents', 'shared'))
from meta_publisher import post_first_comment_to_facebook  # noqa: E402

GRAPH_API = 'https://graph.facebook.com/v19.0'


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
    """Читає скрипт і повертає перші 2 речення як тизер."""
    script_path = os.path.join(os.path.dirname(__file__), 'output', f'{mage}_script_{date_str}.txt')
    with open(script_path, 'r', encoding='utf-8') as f:
        text = f.read().strip()
    sentences = [s.strip() for s in text.split('.') if s.strip()]
    teaser = '. '.join(sentences[:2]) + '.' if len(sentences) >= 2 else text
    return teaser


def build_caption(config: dict, teaser: str) -> str:
    """Формує підпис для Facebook Reels (без хештегів)."""
    lines = [
        teaser,
        '',
        f"{config['emoji']} {config['cta']} → {config['bio_link']}",
    ]
    return '\n'.join(lines)


def publish_reels(config: dict, mage: str, date_str: str) -> str:
    """Публікує Reels в Facebook. Повертає post_id."""
    fb_page_id = os.environ[config['fb_page_id_secret']]
    page_token = os.environ[config['fb_access_token_secret']]

    # Шлях до локального відео файлу
    video_path = os.path.join(os.path.dirname(__file__), 'output', f'{mage}_video_{date_str}.mp4')
    file_size = os.path.getsize(video_path)

    teaser = read_script(mage, date_str)
    caption = build_caption(config, teaser)

    # Крок 1: старт resumable upload
    start_url = f'{GRAPH_API}/{fb_page_id}/video_reels'
    start_params = {'upload_phase': 'start', 'access_token': page_token}
    r = requests.post(start_url, params=start_params, timeout=60)
    if not r.ok:
        raise RuntimeError(f'Facebook start upload помилка: {r.status_code} {r.text[:500]}')
    data = r.json()
    video_id = data['video_id']
    upload_url = data['upload_url']
    print(f'  ✅ Upload session: video_id={video_id}')

    # Крок 2: завантаження відео
    with open(video_path, 'rb') as f:
        upload_headers = {
            'Authorization': f'OAuth {page_token}',
            'file_offset': '0',
            'Content-Length': str(file_size),
        }
        r = requests.post(upload_url, headers=upload_headers, data=f, timeout=120)
    if not r.ok:
        raise RuntimeError(f'Facebook upload помилка: {r.status_code} {r.text[:500]}')
    print(f'  ✅ Відео завантажено на Facebook')

    # Крок 3: фініш і публікація
    finish_url = f'{GRAPH_API}/{fb_page_id}/video_reels'
    finish_params = {
        'upload_phase': 'finish',
        'video_id': video_id,
        'video_state': 'PUBLISHED',
        'description': caption,
        'access_token': page_token,
    }
    r = requests.post(finish_url, params=finish_params, timeout=60)
    if not r.ok:
        raise RuntimeError(f'Facebook finish publish помилка: {r.status_code} {r.text[:500]}')
    post_id = r.json().get('post_id') or r.json().get('id')
    print(f'  ✅ Reels опубліковано: {post_id}')

    # Крок 4: перший коментар
    time.sleep(5)
    try:
        post_first_comment_to_facebook(post_id, page_token, mage)
    except Exception as e:
        print(f'  ⚠️ Помилка першого коментаря Facebook: {e}')

    return post_id


def main() -> None:
    parser = argparse.ArgumentParser(description='Публікація Facebook Reels')
    parser.add_argument('--mage', required=True, choices=['luna', 'arcas', 'numi', 'umbra'])
    args = parser.parse_args()

    date_str = datetime.now().strftime('%Y-%m-%d')
    config = load_config(args.mage)
    mage = config['mage']

    try:
        publish_reels(config, args.mage, date_str)
        print(f'[{mage}] ✅ Facebook Reels опубліковано + перший коментар')
    except Exception as e:
        error_msg = f'🔴 [{mage}] Помилка публікації Facebook Reels: {e}'
        print(error_msg)
        send_telegram_alert(error_msg)
        sys.exit(1)


if __name__ == '__main__':
    main()
