#!/usr/bin/env python3
"""
generate_audio.py — Генерація аудіо через ElevenLabs TTS
Читає output/{mage}_script_{DATE}.txt → зберігає output/{mage}_audio_{DATE}.mp3
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


def generate_audio(config: dict, script: str, mage: str, date_str: str) -> str:
    """Генерує аудіо через ElevenLabs API."""
    api_key = os.environ['ELEVENLABS_API_KEY']
    voice_id = os.environ[config['heygen_voice_id_secret']]

    url = f'https://api.elevenlabs.io/v1/text-to-speech/{voice_id}'
    headers = {
        'Accept': 'audio/mpeg',
        'Content-Type': 'application/json',
        'xi-api-key': api_key,
    }
    payload = {
        'text': script,
        'model_id': 'eleven_multilingual_v2',
        'voice_settings': {
            'stability': 0.75,
            'similarity_boost': 0.85,
            'style': 0.3,
            'use_speaker_boost': True,
        },
    }

    response = requests.post(url, json=payload, headers=headers, timeout=60)
    response.raise_for_status()

    output_dir = os.path.join(os.path.dirname(__file__), 'output')
    os.makedirs(output_dir, exist_ok=True)
    audio_path = os.path.join(output_dir, f'{mage}_audio_{date_str}.mp3')

    with open(audio_path, 'wb') as f:
        f.write(response.content)

    print(f'[{config["mage"]}] ✅ Аудіо згенеровано (ElevenLabs): {audio_path}')
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
