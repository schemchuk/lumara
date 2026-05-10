#!/usr/bin/env python3
"""
generate_video.py — Генерація відео з аватаром через HeyGen API v2
Завантажує mp3 → HeyGen asset → генерує відео → зберігає output/{mage}_video_{DATE}.mp4
→ завантажує в Supabase Storage
"""

import argparse
import json
import os
import sys
import time
from datetime import datetime

import httpx
import requests
from supabase import create_client


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


def get_next_photo_id(config: dict, mage: str) -> str:
    """
    Отримує наступний photo_id зі списку PHOTO_IDS у round-robin режимі.
    Індекс зберігається в Supabase таблиці video_queue, поле last_photo_index.
    """
    photo_ids_str = os.environ.get(config['heygen_photo_ids_secret'], '')
    photo_ids = [p.strip() for p in photo_ids_str.split(',') if p.strip()]
    if not photo_ids:
        raise ValueError(f'HEYGEN_PHOTO_IDS для {mage} не налаштовано')

    supabase_url = os.environ['SUPABASE_URL']
    supabase_key = os.environ['SUPABASE_SERVICE_ROLE_KEY']
    sb = create_client(supabase_url, supabase_key)

    # Отримуємо поточний індекс
    result = sb.table('video_queue').select('*').eq('mage', mage).execute()
    if result.data:
        last_index = result.data[0].get('last_photo_index', 0)
        next_index = (last_index + 1) % len(photo_ids)
        # Оновлюємо індекс
        sb.table('video_queue').update({'last_photo_index': next_index}).eq('mage', mage).execute()
    else:
        # Створюємо запис якщо немає
        next_index = 0
        sb.table('video_queue').insert({'mage': mage, 'last_photo_index': 0}).execute()

    return photo_ids[next_index]


def upload_audio_to_heygen(audio_path: str, api_key: str) -> str:
    """Крок 1: Завантажує аудіо в HeyGen як asset. Повертає asset_id."""
    file_name = os.path.basename(audio_path)
    file_size = os.path.getsize(audio_path)

    url = 'https://upload.heygen.com/v1/asset'
    headers = {
        'X-File-Name': file_name,
        'Content-Type': 'audio/mpeg',
        'Authorization': f'Bearer {api_key}',
    }

    with open(audio_path, 'rb') as f:
        response = requests.post(url, headers=headers, data=f, timeout=120)
    response.raise_for_status()

    data = response.json()
    asset_id = data.get('data', {}).get('id') or data.get('id')
    if not asset_id:
        raise ValueError(f'HeyGen не повернув asset_id: {data}')
    return asset_id


def generate_heygen_video(photo_id: str, audio_asset_id: str, api_key: str) -> str:
    """Крок 2: Створює відео в HeyGen. Повертає video_id."""
    url = 'https://api.heygen.com/v2/video/generate'
    headers = {
        'Authorization': f'Bearer {api_key}',
        'Content-Type': 'application/json',
    }
    payload = {
        'video_inputs': [{
            'character': {
                'type': 'avatar',
                'avatar_id': photo_id,
                'avatar_style': 'normal',
            },
            'voice': {
                'type': 'audio',
                'audio_asset_id': audio_asset_id,
            },
            'background': {
                'type': 'color',
                'value': '#0a0a1a',
            },
        }],
        'dimension': {'width': 1080, 'height': 1920},
        'aspect_ratio': None,
        'caption': False,
    }

    response = requests.post(url, headers=headers, json=payload, timeout=60)
    response.raise_for_status()

    data = response.json()
    video_id = data.get('data', {}).get('video_id') or data.get('video_id')
    if not video_id:
        raise ValueError(f'HeyGen не повернув video_id: {data}')
    return video_id


def poll_heygen_video(video_id: str, api_key: str, timeout_sec: int = 600) -> str:
    """Крок 3: Polling статусу відео. Повертає video_url."""
    url = f'https://api.heygen.com/v1/video_status.get'
    headers = {'Authorization': f'Bearer {api_key}'}

    start = time.time()
    while time.time() - start < timeout_sec:
        response = requests.get(url, headers=headers, params={'video_id': video_id}, timeout=30)
        response.raise_for_status()
        data = response.json()
        status = data.get('data', {}).get('status') or data.get('status')

        if status == 'completed':
            video_url = data.get('data', {}).get('video_url') or data.get('video_url')
            return video_url
        elif status == 'failed':
            raise RuntimeError(f'HeyGen генерація відео провалилась: {data}')

        print(f'  ⏳ HeyGen статус: {status}... чекаємо 15 сек')
        time.sleep(15)

    raise TimeoutError('HeyGen timeout — відео не згенеровано за 10 хвилин')


def download_video(video_url: str, output_path: str) -> None:
    """Завантажує відео з URL і зберігає локально."""
    response = requests.get(video_url, timeout=120)
    response.raise_for_status()
    with open(output_path, 'wb') as f:
        f.write(response.content)


def upload_to_supabase(video_path: str, mage: str, date_str: str) -> str:
    """Крок 4: Завантажує відео в Supabase Storage bucket 'videos'. Повертає публічний URL."""
    supabase_url = os.environ['SUPABASE_URL']
    supabase_key = os.environ['SUPABASE_SERVICE_ROLE_KEY']
    sb = create_client(supabase_url, supabase_key)

    bucket_name = 'videos'
    file_name = f'{mage}_{date_str}.mp4'

    with open(video_path, 'rb') as f:
        sb.storage.from_(bucket_name).upload(file_name, f, file_options={'content-type': 'video/mp4'})

    public_url = sb.storage.from_(bucket_name).get_public_url(file_name)
    return public_url


def save_video_url(public_url: str, mage: str, date_str: str) -> str:
    """Зберігає публічний URL відео у файл."""
    output_dir = os.path.join(os.path.dirname(__file__), 'output')
    os.makedirs(output_dir, exist_ok=True)
    path = os.path.join(output_dir, f'{mage}_video_url_{date_str}.txt')
    with open(path, 'w', encoding='utf-8') as f:
        f.write(public_url)
    return path


def main() -> None:
    parser = argparse.ArgumentParser(description='Генерація відео для мага')
    parser.add_argument('--mage', required=True, choices=['luna', 'arcas', 'numi', 'umbra'])
    args = parser.parse_args()

    date_str = datetime.now().strftime('%Y-%m-%d')
    config = load_config(args.mage)
    mage = config['mage']

    audio_path = os.path.join(os.path.dirname(__file__), 'output', f'{args.mage}_audio_{date_str}.mp3')
    if not os.path.exists(audio_path):
        error_msg = f'🔴 [{mage}] Аудіо не знайдено: {audio_path}'
        print(error_msg)
        send_telegram_alert(error_msg)
        sys.exit(1)

    # Визначаємо API ключ: UMBRA використовує окремий акаунт
    if args.mage == 'umbra':
        api_key = os.environ['HEYGEN_API_KEY_UMBRA']
    else:
        api_key = os.environ['HEYGEN_API_KEY']

    try:
        print(f'[{mage}] 📤 Завантаження аудіо в HeyGen...')
        audio_asset_id = upload_audio_to_heygen(audio_path, api_key)
        print(f'[{mage}]   ✅ Audio asset: {audio_asset_id}')

        print(f'[{mage}] 🎭 Вибір наступного photo ID (round-robin)...')
        photo_id = get_next_photo_id(config, args.mage)
        print(f'[{mage}]   ✅ Photo ID: {photo_id}')

        print(f'[{mage}] 🎬 Генерація відео в HeyGen...')
        video_id = generate_heygen_video(photo_id, audio_asset_id, api_key)
        print(f'[{mage}]   ✅ Video ID: {video_id}')

        print(f'[{mage}] ⏳ Очікування завершення генерації...')
        video_url = poll_heygen_video(video_id, api_key)
        print(f'[{mage}]   ✅ Відео готове')

        output_dir = os.path.join(os.path.dirname(__file__), 'output')
        video_path = os.path.join(output_dir, f'{args.mage}_video_{date_str}.mp4')
        download_video(video_url, video_path)
        print(f'[{mage}]   ✅ Відео завантажено локально: {video_path}')

        print(f'[{mage}] ☁️ Завантаження в Supabase Storage...')
        public_url = upload_to_supabase(video_path, args.mage, date_str)
        save_video_url(public_url, args.mage, date_str)

        print(f'[{mage}] ✅ Відео згенеровано і завантажено: {public_url}')

    except Exception as e:
        error_msg = f'🔴 [{mage}] Помилка генерації відео: {e}'
        print(error_msg)
        send_telegram_alert(error_msg)
        sys.exit(1)


if __name__ == '__main__':
    main()
