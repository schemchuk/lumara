#!/usr/bin/env python3
"""
generate_audio.py — Генерація аудіо через Microsoft Edge TTS (безкоштовно)
Читає output/{mage}_script_{DATE}.txt → зберігає output/{mage}_audio_{DATE}.mp3
"""

import argparse
import asyncio
import json
import os
import sys
from datetime import datetime

import edge_tts


# Налаштування голосів для кожного мага
VOICE_CONFIG = {
    'luna': {
        'voice': 'uk-UA-PolinaNeural',
        'rate': '+0%',
        'pitch': '+0Hz',
        'desc': 'жіночий, м\'який, містичний',
    },
    'arcas': {
        'voice': 'uk-UA-OstapNeural',
        'rate': '+0%',
        'pitch': '+0Hz',
        'desc': 'чоловічий, глибокий, таролог',
    },
    'numi': {
        'voice': 'uk-UA-PolinaNeural',
        'rate': '+15%',
        'pitch': '+20Hz',
        'desc': 'жіночий, енергійний, молодий (рижа лисиця)',
    },
    'umbra': {
        'voice': 'uk-UA-PolinaNeural',
        'rate': '-10%',
        'pitch': '-30Hz',
        'desc': 'жіночий, спокійний, зрілий 45-50 (біла миш)',
    },
}


def load_config(mage: str) -> dict:
    """Завантажує конфіг мага з JSON файлу."""
    config_path = os.path.join(os.path.dirname(__file__), 'configs', f'{mage}.json')
    with open(config_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def send_telegram_alert(message: str) -> None:
    """Надсилає Telegram алерт через загального бота."""
    import requests
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


async def generate_audio_async(mage_lower: str, script: str, output_path: str) -> None:
    """Асинхронна генерація аудіо через Edge TTS."""
    cfg = VOICE_CONFIG[mage_lower]
    communicate = edge_tts.Communicate(
        script,
        cfg['voice'],
        rate=cfg['rate'],
        pitch=cfg['pitch'],
    )
    await communicate.save(output_path)


def generate_audio(config: dict, script: str, mage: str, date_str: str) -> str:
    """Генерує аудіо через Edge TTS."""
    mage_lower = config['mage_lower']
    cfg = VOICE_CONFIG[mage_lower]

    output_dir = os.path.join(os.path.dirname(__file__), 'output')
    os.makedirs(output_dir, exist_ok=True)
    audio_path = os.path.join(output_dir, f'{mage}_audio_{date_str}.mp3')

    asyncio.run(generate_audio_async(mage_lower, script, audio_path))

    print(f'[{config["mage"]}] ✅ Аудіо згенеровано (Edge TTS — {cfg["desc"]}): {audio_path}')
    return audio_path


def main() -> None:
    parser = argparse.ArgumentParser(description='Генерація аудіо для відео мага')
    parser.add_argument('--mage', required=True, choices=['luna', 'arcas', 'numi', 'umbra'])
    args = parser.parse_args()

    date_str = datetime.now().strftime('%Y-%m-%d')
    config = load_config(args.mage)
    mage = config['mage']

    script_path = os.path.join(os.path.dirname(__file__), 'output', f'{args.mage}_script_{date_str}.txt')
    if not os.path.exists(script_path):
        error_msg = f'🔴 [{mage}] Скрипт не знайдено: {script_path}'
        print(error_msg)
        send_telegram_alert(error_msg)
        sys.exit(1)

    with open(script_path, 'r', encoding='utf-8') as f:
        script = f.read().strip()

    try:
        generate_audio(config, script, args.mage, date_str)
    except Exception as e:
        error_msg = f'🔴 [{mage}] Помилка генерації аудіо: {e}'
        print(error_msg)
        send_telegram_alert(error_msg)
        sys.exit(1)


if __name__ == '__main__':
    main()
