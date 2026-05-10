# 🎬 LUMARA Video Pipeline — Інструкції

Повністю автоматичний відео-пайплайн для 4 магів LUMARA Academy.

---

## 📊 Діаграма пайплайну

```
┌─────────────────┐
│  GitHub Actions │  cron: пн-чт 08:00 UTC
│  або manual run │
└────────┬────────┘
         │
         ▼
┌─────────────────┐     ┌──────────────┐     ┌─────────────┐
│ generate_script │────▶│ generate_audio│────▶│generate_video│
│  (Claude API)   │     │ (ElevenLabs)  │     │  (HeyGen)   │
└─────────────────┘     └──────────────┘     └──────┬──────┘
                                                    │
              ┌─────────────────────────────────────┼──────┐
              │                                     │      │
              ▼                                     ▼      ▼
    ┌─────────────────┐                 ┌─────────────────┐
    │ publish_instagram │               │ publish_facebook │
    │    Reels + CTA    │               │   Reels + CTA    │
    └─────────────────┘                 └─────────────────┘
              │                                     │
              ▼                                     ▼
    ┌─────────────────┐                 ┌─────────────────┐
    │ publish_telegram│                 │ publish_twitter │
    │   (@mage_lumara)│                 │  (Academy acc)  │
    └─────────────────┘                 └─────────────────┘
              │
              ▼
    ┌─────────────────┐
    │   notify_tiktok │───▶ Telegram → Admin (ручна публікація)
    └─────────────────┘
```

---

## 📅 Графік публікацій

| День | Маг | Cron | Час UTC | Час Київ |
|------|-----|------|---------|----------|
| Понеділок | 🌙 LUNA | `0 8 * * 1` | 08:00 | 10:00 (зима) / 11:00 (літо) |
| Вівторок | 🃏 ARCAS | `0 8 * * 2` | 08:00 | 10:00 / 11:00 |
| Середа | 🔢 NUMI | `0 8 * * 3` | 08:00 | 10:00 / 11:00 |
| Четвер | 🧠 UMBRA | `0 8 * * 4` | 08:00 | 10:00 / 11:00 |

---

## ⚙️ Налаштування

### 1. HeyGen Avatar (Photo IDs) і Voice ID

**Photo IDs** — це ID фотографій, завантажених в HeyGen для створення відео з talking photo.

1. Зайдіть в [HeyGen Dashboard](https://app.heygen.com/)
2. Перейдіть в **Avatar → TalkingPhoto**
3. Завантажте фото мага (мінімум 6 фото для round-robin)
4. Відкрийте фото → скопіюйте `photo_id` з URL або API
5. Додайте всі ID через кому в GitHub Secret: `LUNA_HEYGEN_PHOTO_IDS`

**Voice ID** — голос ElevenLabs, який використовується через HeyGen:
1. В HeyGen Dashboard перейдіть в **Voice → My Voice**
2. Скопіюйте Voice ID
3. Збережіть в GitHub Secret: `LUNA_HEYGEN_VOICE_ID`

> ⚠️ **Важливо:** в конфігах використовується `heygen_photo_ids_secret`, а не `avatar_id`. При кожній генерації обирається наступний photo_id зі списку (round-robin). Індекс зберігається в Supabase таблиці `video_queue`.

### 2. ElevenLabs API ключ і Voice ID

1. Зареєструйтесь на [elevenlabs.io](https://elevenlabs.io/)
2. Скопіюйте API ключ → GitHub Secret: `ELEVENLABS_API_KEY`
3. Voice ID береться з `LUNA_HEYGEN_VOICE_ID` (той самий, що й для HeyGen)

### 3. Twitter API ключі для Academy

1. [developer.twitter.com](https://developer.twitter.com) → створіть App для Academy
2. Згенеруйте **Consumer Keys** та **Access Token**
3. Збережіть в GitHub Secrets:
   - `ACADEMY_TWITTER_API_KEY`
   - `ACADEMY_TWITTER_API_SECRET`
   - `ACADEMY_TWITTER_ACCESS_TOKEN`
   - `ACADEMY_TWITTER_ACCESS_SECRET`

### 4. Supabase Storage — bucket `videos`

1. В Supabase Dashboard перейдіть в **Storage**
2. Створіть bucket з ім'ям `videos`
3. Включіть **Public access** для цього bucket
4. Переконайтесь, що `SUPABASE_SERVICE_ROLE_KEY` має права на запис

### 5. Telegram канали магів

Для кожного мага потрібно:
- Бот токен (BotFather → `@BotFather`)
- Channel ID (додайте бота адміном в канал, отримайте ID через `@userinfobot` або API)

---

## ➕ Як додати нового мага

1. Скопіюйте `configs/luna.json` → `configs/newmage.json`
2. Змініть:
   - `mage`, `mage_lower`, `emoji`
   - `post_day`, `cron`
   - `telegram_channel_id`, `telegram_bot_token_secret`
   - `ig_user_id_secret`, `fb_page_id_secret`, `fb_access_token_secret`
   - `heygen_photo_ids_secret`, `heygen_voice_id_secret`
   - `topic`, `style`, `cta`, `bio_link`
   - `tiktok_hashtags`, `ig_hashtags`
3. Додайте всі нові secrets в GitHub
4. Додайте новий `cron` в `.github/workflows/video-pipeline.yml`
5. Оновіть `case` в `workflow` для визначення мага по дню
6. Оновіть `pipeline.py` choices, якщо потрібно

---

## 🐞 Типові помилки

### HeyGen timeout
- **Причина:** відео генерується довше 10 хвилин або credits закінчились
- **Рішення:** перевірте баланс credits в HeyGen Dashboard

### Instagram 400 / 403
- **Причина:** `IG_ACCESS_TOKEN` протух (діє 60 днів)
- **Рішення:** оновіть токен через [Meta Graph API Explorer](https://developers.facebook.com/tools/explorer/) → `instagram_content_publish`

### Facebook Reels помилка
- **Причина:** `PAGE_ACCESS_TOKEN` неправильний або page не опублікована
- **Рішення:** перевірте `LUNA_PAGE_ACCESS_TOKEN` і `LUNA_FB_PAGE_ID`

### Supabase Storage помилка
- **Причина:** bucket `videos` не існує або не public
- **Рішення:** створіть bucket в Supabase Dashboard і ввімкніть Public

---

## 🔄 Воронка конверсії

```
TikTok / IG Reels / FB Reels
         │
         ▼
  lumara.fyi/links/{mage}
         │
    ┌────┴────┐
    ▼         ▼
  Чат      Telegram
  мага      канал
    │         │
    └────┬────┘
         ▼
    Реєстрація
    (LUMARA Academy)
         │
         ▼
    Підписка / Платіж
```

---

## 💰 Витрати

| Сервіс | Вартість за відео | Примітка |
|--------|-------------------|----------|
| HeyGen | ~$2 | talking photo 30 сек |
| ElevenLabs | ~$0 | 60-80 слів, multilingual v2 |
| Claude API | ~$0.01 | 1 запит на скрипт |
| Twitter API | безкоштовно | basic tier |

---

## 📁 Структура

```
content/video-pipeline/
├── INSTRUCTIONS.md
├── requirements.txt
├── generate_script.py
├── generate_audio.py
├── generate_video.py
├── publish_instagram_reels.py
├── publish_facebook_reels.py
├── publish_telegram.py
├── publish_twitter.py
├── notify_tiktok.py
├── pipeline.py
└── configs/
    ├── luna.json
    ├── arcas.json
    ├── numi.json
    └── umbra.json
```

---

*Останнє оновлення: 9 травня 2026*
*Проект: LUMARA Academy · lumara.fyi*
