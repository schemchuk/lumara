#!/usr/bin/env python3
"""
generate_script.py — Генерація скрипту відео для мага через Claude API
Зберігає результат в output/{mage}_script_{DATE}.txt
"""

import argparse
import json
import os
import sys
from datetime import datetime

import anthropic


def load_config(mage: str) -> dict:
    """Завантажує конфіг мага з JSON файлу."""
    config_path = os.path.join(os.path.dirname(__file__), 'configs', f'{mage}.json')
    if not os.path.exists(config_path):
        raise FileNotFoundError(f'Конфіг не знайдено: {config_path}')
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
        import requests
        requests.post(
            f'https://api.telegram.org/bot{token}/sendMessage',
            json={'chat_id': chat_id, 'text': message, 'parse_mode': 'HTML'},
            timeout=10,
        )
    except Exception as e:
        print(f'[ALERT FAIL] {e}')


def generate_script(config: dict, date_str: str) -> str:
    """Генерує скрипт через Claude API."""
    client = anthropic.Anthropic(api_key=os.environ['ANTHROPIC_API_KEY'])

    mage = config['mage']
    style = config['style']
    topic = config['topic']
    cta = config['cta']
    bio_link = config['bio_link']

    system_prompt = (
        f'Ти {mage} — {style}. Говориш від першої особи українською. '
        f'Ти НЕ розкриваєш що ти AI. Ти реальний персонаж.'
    )

    user_prompt = (
        f'Створи скрипт для короткого відео (30 секунд, 60-80 слів).\n'
        f'Тема: {topic}\n'
        f'Структура:\n'
        f'1. Інтригуючий початок (одне речення-гачок)\n'
        f'2. Корисний інсайт (2-3 речення по темі)\n'
        f'3. CTA в кінці: "{cta} → {bio_link}"\n'
        f'Стиль: {style}\n'
        f'Мова: українська\n'
        f'БЕЗ сценічних ремарок, тільки текст для озвучки.'
    )

    response = client.messages.create(
        model='claude-sonnet-4-6',
        max_tokens=500,
        system=system_prompt,
        messages=[{'role': 'user', 'content': user_prompt}],
    )

    script = response.content[0].text.strip()

    # Підрахунок слів
    word_count = len(script.split())
    print(f'[{mage}] ✅ Скрипт згенеровано ({word_count} слів)')

    return script


def save_script(script: str, mage: str, date_str: str) -> str:
    """Зберігає скрипт у файл."""
    output_dir = os.path.join(os.path.dirname(__file__), 'output')
    os.makedirs(output_dir, exist_ok=True)
    path = os.path.join(output_dir, f'{mage}_script_{date_str}.txt')
    with open(path, 'w', encoding='utf-8') as f:
        f.write(script)
    return path


def main() -> None:
    parser = argparse.ArgumentParser(description='Генерація скрипту відео для мага')
    parser.add_argument('--mage', required=True, choices=['luna', 'arcas', 'numi', 'umbra'])
    args = parser.parse_args()

    date_str = datetime.now().strftime('%Y-%m-%d')
    config = load_config(args.mage)
    mage = config['mage']

    try:
        script = generate_script(config, date_str)
        save_script(script, args.mage, date_str)
    except Exception as e:
        error_msg = f'🔴 [{mage}] Помилка генерації скрипту: {e}'
        print(error_msg)
        send_telegram_alert(error_msg)
        sys.exit(1)


if __name__ == '__main__':
    main()
