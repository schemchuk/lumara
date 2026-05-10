#!/usr/bin/env python3
"""
pipeline.py — Головний оркестратор відео пайплайну LUMARA
Запускає всі кроки по черзі, надсилає підсумковий звіт в Telegram
"""

import argparse
import json
import os
import subprocess
import sys
from datetime import datetime

import requests


def load_config(mage: str) -> dict:
    """Завантажує конфіг мага з JSON файлу."""
    config_path = os.path.join(os.path.dirname(__file__), 'configs', f'{mage}.json')
    with open(config_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def send_telegram_alert(message: str, chat_id: str = None) -> None:
    """Надсилає алерт в LUMARA_TELEGRAM_CHANNEL_ID або вказаний chat_id."""
    token = os.environ.get('TELEGRAM_ALERT_BOT_TOKEN')
    cid = chat_id or os.environ.get('LUMARA_TELEGRAM_CHANNEL_ID')
    if not token or not cid:
        print(f'[ALERT] {message}')
        return
    try:
        requests.post(
            f'https://api.telegram.org/bot{token}/sendMessage',
            json={'chat_id': cid, 'text': message, 'parse_mode': 'HTML'},
            timeout=10,
        )
    except Exception as e:
        print(f'[ALERT FAIL] {e}')


def run_step(name: str, script: str, mage: str, critical: bool) -> tuple[bool, str]:
    """Запускає один крок пайплайну через subprocess."""
    print(f'\n{"─" * 50}')
    print(f'{name}')
    print('─' * 50)

    script_path = os.path.join(os.path.dirname(__file__), script)
    cmd = [sys.executable, script_path, '--mage', mage]

    try:
        result = subprocess.run(cmd, capture_output=False, text=True, timeout=900)
        if result.returncode == 0:
            print(f'✅ {name} — успішно')
            return True, 'OK'
        else:
            print(f'❌ {name} — провал (код {result.returncode})')
            if critical:
                raise RuntimeError(f'Критичний крок провалено: {name}')
            return False, f'FAILED (code {result.returncode})'
    except subprocess.TimeoutExpired:
        print(f'⏱️ {name} — timeout')
        if critical:
            raise RuntimeError(f'Критичний крок timeout: {name}')
        return False, 'TIMEOUT'
    except Exception as e:
        print(f'❌ {name} — помилка: {e}')
        if critical:
            raise
        return False, f'ERROR: {e}'


def main() -> None:
    parser = argparse.ArgumentParser(description='Відео пайплайн LUMARA')
    parser.add_argument('--mage', required=True, choices=['luna', 'arcas', 'numi', 'umbra'])
    args = parser.parse_args()

    date_str = datetime.now().strftime('%Y-%m-%d')
    config = load_config(args.mage)
    mage = config['mage']
    emoji = config['emoji']

    print(f'\n🎬 [{mage}] Запуск відео пайплайну — {date_str}')
    print(f'   Тема: {config["topic"]}')
    print(f'   Стиль: {config["style"]}')

    steps = [
        ('📝 Генерація скрипту', 'generate_script.py', True),
        ('🎙️ Генерація аудіо', 'generate_audio.py', True),
        ('🎬 Генерація відео', 'generate_video.py', True),
        ('📸 Instagram Reels', 'publish_instagram_reels.py', False),
        ('📘 Facebook Reels', 'publish_facebook_reels.py', False),
        ('✈️ Telegram анонс', 'publish_telegram.py', False),
        ('🐦 Twitter', 'publish_twitter.py', False),
        ('📲 TikTok алерт', 'notify_tiktok.py', False),
    ]

    results = {}
    try:
        for name, script, critical in steps:
            ok, status = run_step(name, script, args.mage, critical)
            results[name] = '✅' if ok else '❌'
            if not ok and critical:
                raise RuntimeError(f'Критичний крок провалено: {name}')
    except Exception as e:
        error_msg = f'🔴 [{mage}] Пайплайн зупинено: {e}'
        print(f'\n{error_msg}')
        send_telegram_alert(error_msg)
        sys.exit(1)

    # Підсумковий звіт
    report_lines = [
        f'📊 {mage} пайплайн завершено — {date_str}',
        '',
        f'{results.get("📝 Генерація скрипту", "⏭️")} Скрипт згенеровано',
        f'{results.get("🎙️ Генерація аудіо", "⏭️")} Аудіо (ElevenLabs)',
        f'{results.get("🎬 Генерація відео", "⏭️")} Відео (HeyGen)',
        f'{results.get("📸 Instagram Reels", "⏭️")} Instagram Reels + коментар',
        f'{results.get("📘 Facebook Reels", "⏭️")} Facebook Reels + коментар',
        f'{results.get("✈️ Telegram анонс", "⏭️")} Telegram анонс (@{config["mage_lower"]}_lumara)',
        f'{results.get("🐦 Twitter", "⏭️")} Twitter (Academy)',
        f'{results.get("📲 TikTok алерт", "⏭️")} TikTok — очікує ручної публікації',
        '',
        '💰 Витрати: HeyGen ~$2, ElevenLabs ~$0',
    ]
    report = '\n'.join(report_lines)

    print(f'\n{report}')
    send_telegram_alert(report)


if __name__ == '__main__':
    main()
