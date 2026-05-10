#!/usr/bin/env python3
"""
notify_tiktok.py — Telegram алерт для ручної публікації TikTok
Надсилає готовий caption, відео файлом і покрокову інструкцію
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


def build_caption(config: dict, teaser: str) -> str:
    """Формує готовий caption для TikTok."""
    emoji = config['emoji']
    cta = config['cta']
    bio_link = config['bio_link']
    hashtags = ' '.join(f'#{h}' for h in config['tiktok_hashtags'][:7])

    lines = [
        teaser,
        '',
        f'{emoji} {cta} → {bio_link}',
        '',
        hashtags,
    ]
    return '\n'.join(lines)


def send_instruction_message(token: str, chat_id: str, config: dict, caption: str, video_url: str) -> None:
    """Надсилає інструкцію з готовим caption у блоці для копіювання."""
    mage = config['mage']
    emoji = config['emoji']

    # Escape для HTML всередині <pre> блоку
    safe_caption = caption.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')

    text = (
        f'🎬 <b>{mage} відео готове для TikTok!</b>\n\n'
        f'📋 <b>Готовий caption</b> (натисни, щоб скопіювати):\n'
        f'<pre>{safe_caption}</pre>\n\n'
        f'📎 <b>Посилання на відео:</b>\n'
        f'<a href="{video_url}">Відкрити в браузері</a>\n\n'
        f'⏰ <b>Найкращий час:</b> 12:00–15:00 за Києвом\n\n'
        f'━━━ <b>Кроки публікації:</b> ━━━\n'
        f'1️⃣ Відкрий TikTok → "+" → "Upload"\n'
        f'2️⃣ Вибери відео (нижче в цьому чаті) або за посиланням\n'
        f'3️⃣ Натисни на caption → "Paste" (текст вище)👆\n'
        f'4️⃣ Додай обкладинку (Cover) → "Post"\n\n'
        f'{emoji} Готово! {mage} на TikTok 🚀'
    )

    url = f'https://api.telegram.org/bot{token}/sendMessage'
    payload = {
        'chat_id': chat_id,
        'text': text,
        'parse_mode': 'HTML',
        'disable_web_page_preview': True,
    }
    r = requests.post(url, json=payload, timeout=30)
    r.raise_for_status()


def send_video_file(token: str, chat_id: str, video_path: str, mage: str) -> None:
    """Надсилає відео файлом прямо в Telegram."""
    url = f'https://api.telegram.org/bot{token}/sendVideo'

    with open(video_path, 'rb') as f:
        files = {'video': f}
        data = {
            'chat_id': chat_id,
            'caption': f'🎥 Відео {mage} для TikTok',
            'parse_mode': 'HTML',
            'supports_streaming': True,
        }
        r = requests.post(url, files=files, data=data, timeout=120)
    r.raise_for_status()


def send_notification(config: dict, mage: str, date_str: str) -> None:
    """Надсилає повний TikTok алерт адміну."""
    token = os.environ['TELEGRAM_ALERT_BOT_TOKEN']
    admin_id = os.environ.get('ADMIN_TELEGRAM_ID', '6127139155')

    teaser = read_script_teaser(mage, date_str)
    video_url = read_video_url(mage, date_str)
    caption = build_caption(config, teaser)

    # 1. Інструкція з готовим caption
    send_instruction_message(token, admin_id, config, caption, video_url)

    # 2. Відео файлом
    video_path = os.path.join(os.path.dirname(__file__), 'output', f'{mage}_video_{date_str}.mp4')
    if os.path.exists(video_path):
        send_video_file(token, admin_id, video_path, config['mage'])
    else:
        print(f'⚠️ Локальний файл відео не знайдено: {video_path}')

    print(f'[{config["mage"]}] ✅ TikTok алерт надіслано адміну (caption + відео)')


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
