#!/usr/bin/env python3
"""
publish_instagram_reels.py — Публікація Instagram Reels через Graph API
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
from meta_publisher import post_first_comment_to_instagram  # noqa: E402

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
    """Формує підпис для Instagram Reels."""
    lines = [
        teaser,
        '',
        f"{config['emoji']} {config['cta']} → {config['bio_link']}",
        '',
    ]
    hashtags = ' '.join(f'#{h}' for h in config['ig_hashtags'])
    lines.append(hashtags)
    return '\n'.join(lines)


def publish_reels(config: dict, mage: str, date_str: str) -> str:
    """Публікує Reels в Instagram. Повертає media_id."""
    ig_user_id = os.environ[config['ig_user_id_secret']]
    access_token = os.environ[config['ig_access_token_secret']]

    # Читаємо публічний URL відео
    url_path = os.path.join(os.path.dirname(__file__), 'output', f'{mage}_video_url_{date_str}.txt')
    with open(url_path, 'r', encoding='utf-8') as f:
        video_url = f.read().strip()

    teaser = read_script(mage, date_str)
    caption = build_caption(config, teaser)

    # Крок 1: створити контейнер
    create_url = f'{GRAPH_API}/{ig_user_id}/media'
    params = {
        'media_type': 'REELS',
        'video_url': video_url,
        'caption': caption,
        'share_to_feed': True,
        'access_token': access_token,
    }
    r = requests.post(create_url, params=params, timeout=60)
    if not r.ok:
        raise RuntimeError(f'Instagram create container помилка: {r.status_code} {r.text[:500]}')
    container_id = r.json()['id']
    print(f'  ✅ Container створено: {container_id}')

    # Крок 2: polling статусу
    poll_url = f'{GRAPH_API}/{container_id}'
    poll_params = {'fields': 'status_code', 'access_token': access_token}
    start = time.time()
    while time.time() - start < 300:
        r = requests.get(poll_url, params=poll_params, timeout=30)
        r.raise_for_status()
        status = r.json().get('status_code')
        if status == 'FINISHED':
            break
        if status == 'ERROR':
            raise RuntimeError(f'Instagram container помилка обробки: {r.json()}')
        print(f'  ⏳ Instagram статус: {status}... чекаємо 10 сек')
        time.sleep(10)
    else:
        raise TimeoutError('Instagram timeout — контейнер не готовий за 5 хвилин')

    # Крок 3: публікація
    publish_url = f'{GRAPH_API}/{ig_user_id}/media_publish'
    publish_params = {'creation_id': container_id, 'access_token': access_token}
    r = requests.post(publish_url, params=publish_params, timeout=60)
    if not r.ok:
        raise RuntimeError(f'Instagram publish помилка: {r.status_code} {r.text[:500]}')
    media_id = r.json()['id']
    print(f'  ✅ Reels опубліковано: {media_id}')

    # Крок 4: перший коментар
    time.sleep(5)
    try:
        post_first_comment_to_instagram(media_id, access_token, mage)
    except Exception as e:
        print(f'  ⚠️ Помилка першого коментаря Instagram: {e}')

    return media_id


def main() -> None:
    parser = argparse.ArgumentParser(description='Публікація Instagram Reels')
    parser.add_argument('--mage', required=True, choices=['luna', 'arcas', 'numi', 'umbra'])
    args = parser.parse_args()

    date_str = datetime.now().strftime('%Y-%m-%d')
    config = load_config(args.mage)
    mage = config['mage']

    try:
        publish_reels(config, args.mage, date_str)
        print(f'[{mage}] ✅ Instagram Reels опубліковано + перший коментар')
    except Exception as e:
        error_msg = f'🔴 [{mage}] Помилка публікації Instagram Reels: {e}'
        print(error_msg)
        send_telegram_alert(error_msg)
        sys.exit(1)


if __name__ == '__main__':
    main()
