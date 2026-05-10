Онови файл LUMARA_SESSION_HANDOFF_V3.md до версії V4. Додай всі зміни які були зроблені з 23 квітня по сьогодні:

Реструктуризація репо магів
Telethon UserBot для LUNA (warmup режим)
Живі промпти магів з анонсом артефактів
Фікс Instagram діалогів (гілки коментарів)
Facebook моніторинг
Webhook для Telegram
Спільна пам'ять магів (user_context)
Акаунти магів в Telegram (номери телефонів)
GitHub secrets для всіх магів
Оновлений статус всіх блоків
Поточне завдання і що далі

Збережи як LUMARA_SESSION_HANDOFF_V4.md# LUMARA — Документ передачі сесії V4
*Оновлено: 9 Травня 2026*

## 🚀 Як підняти контекст в новій вкладці
Відкрий нову вкладку Claude, завантаж цей файл і напиши:
> "Прочитай цей документ і продовж роботу над проектом LUMARA з того місця де зупинились"

---

## ✅ Статус проекту

### Фаза 0 — Стратегія (ЗАВЕРШЕНО ✅)
- Назва: **LUMARA** (не змінюється)
- Домен: **lumara.fyi**
- Слоган: "Illuminate your path"
- Кольори: темно-зелений + смарагд + золото

### Фаза 1 — Соціальні мережі (В ПРОЦЕСІ 🔄)

#### LUMARA Academy
| Платформа | Нікнейм | Статус |
|-----------|---------|--------|
| Instagram | @lumara_fyi | ✅ |
| TikTok | @lumara48 | ✅ |
| YouTube | @lumara_fyi | ✅ |
| Telegram | @lumara_academy | ✅ |
| Twitter/X | @lumara | ⚠️ заблоковано, подано апеляцію |

#### Telegram канали магів
| Маг | Telegram | GitHub репо |
|-----|---------|-------------|
| LUNA | @luna_lumara | lunalumarafyi-lab/lumara |
| ARCAS | @arcas_lumara | arcaslumara-max/lumara |
| NUMI | @numi_lumara | numilumara-design/lumara |
| UMBRA | @umbra_lumara | umbralumara-oss/lumara |
| Academy | @lumara_academy | starWoshe/lumara |

#### Instagram акаунти магів
| Маг | Instagram | Посилання в біо |
|-----|---------|--------|
| LUNA | @luna.lumara | lumara.fyi/chat/luna |
| ARCAS | @arcaslumara | lumara.fyi/chat/arcas |
| NUMI | @numi.lumara | lumara.fyi/chat/numi |
| UMBRA | @umbra.lumara | lumara.fyi/chat/umbra |

#### Telegram UserBot акаунти (Telethon)
| Маг | Номер телефону | Статус |
|-----|----------------|--------|
| LUNA | у Supabase (сесія збережена) | ✅ warmup активний |
| ACADEMY | у Supabase (сесія збережена) | ✅ активний |

---

## 🔄 Виконані блоки

### БЛОК 1 — Сайт і воронка ✅
- Лендінг без AI/BETA
- Magic Link додано
- Redirect після входу до конкретного мага
- Публічні сторінки /mages/ для всіх магів
- UTM трекінг активний
- Адмін панель з воронкою і розбивкою по магах
- Моніторинг токенів і алерти
- Гостьовий чат з UTM та онбордингом через діалог ✅
- Lead Generation System (рівні розкриття, коди знання) ✅
- Крос-промо між магами ✅
- Кешування промптів Anthropic (зниження витрат) ✅
- UNLIMITED_EMAILS — безліміт для конкретних email без адмін-панелі ✅

### БЛОК 2 — Контент і воронка магів ✅
- Промпти Python скриптів оновлено
- Інтрига в кожному пості
- CTA до Telegram і сайту
- Окремий формат для Telegram (глибший, без хештегів)
- Посилання малими буквами скрізь
- Мультимовність в промптах

### БЛОК Links ✅
- Сторінки /links/[mage] створено
- Bio-link сторінка /links з усіма магами

### БЛОК 3.1 ✅ — Автопублікація постів
- Telegram канали магів (кожен через свій бот і канал)
- Повний пост + картинка + UTM посилання
- Кожен маг публікує через своє репо GitHub Actions

### БЛОК 3.2 ✅ — Академія @lumara_academy
- Контент план: Пн/Ср/Пт/Нд автопублікація
- academy-weekend.yml для вихідних
- Академія у системі sync-mages (starWoshe/lumara)

### БЛОК 3.3 ✅ — Реактивація мовчазних юзерів
- Cron job кожен день о 12:00 UTC
- Email від мага через Resend
- Трекінг reactivationSentAt в БД

### БЛОК 4 — Активний пошук ✅ (повністю реалізовано)
- **telegram_monitor.py** — моніторинг тематичних груп, тригери, відповіді
- **instagram_comment_monitor.py** — Instagram та Facebook коментарі
- **Режим likes_only** — бот ставить реакції (🌙/👍) без відповідей
- **MONITOR_MODE / ACTIVE_MONITOR** env vars для контролю поведінки
- GitHub Actions workflows (cron кожні 2 год)
- Адмінка з блоком "Активний пошук"

### БЛОК 4a — Реструктуризація репо магів ✅ (НОВЕ)
**Архітектура:**
- Головне репо `schemchuk/lumara` → sync-mages.yml синхронізує в 5 репо магів
- Кожне репо мага має свої workflows (instagram-monitor, facebook-monitor, daily-post)
- `temp-mage-repos/{mage}/.github/workflows/` — шаблони, які синхронізуються
- Academy (`starWoshe/lumara`) не отримує `sync-mages.yml` (автовидалення)
- Academy не отримує `daily-post.yml` — натомість `academy-weekend.yml`
- Workflows магів не копіюються в репо академії і навпаки
- Orphaned workflow файли автоматично видаляються при синку

**Секрети синхронізуються з головного репо в репо магів:**
```
ANTHROPIC_API_KEY, IG_ACCESS_TOKEN, SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY
INSTAGRAM_MAX_PER_DAY, FACEBOOK_MAX_PER_DAY, TELEGRAM_ALERT_BOT_TOKEN
{MAGE}_IG_USER_ID, {MAGE}_FB_PAGE_ID, {MAGE}_PAGE_ACCESS_TOKEN
{MAGE}_PAGE_ID, {MAGE}_TELEGRAM_CHANNEL_ID, {MAGE}_TELEGRAM_BOT_TOKEN
TELEGRAM_BOT_TOKEN, OPENAI_API_KEY, DATABASE_URL, DIRECT_URL
LUMARA_TELEGRAM_CHANNEL_ID, TELEGRAM_CHANNEL_ID
```

### БЛОК 4b — Telethon UserBot ✅ (НОВЕ)
- **userbot_luna.py** — Telethon UserBot для LUNA (warmup режим)
- Режими: `warmup` (реакції на пости в групах), `active` (AI відповіді)
- Конфігурація: emojis, паузи, ліміти, теми — унікальні для кожного мага
- **Виправлено**: `asyncio.sleep(pause_sec)` замінено на `_interruptible_sleep(pause_sec)` — перевіряє timeout щохвилини
- MAX_RUNTIME_MIN = 40 хв (вкладається в GitHub Actions)
- Сесія Telethon зберігається в Supabase (таблиця `userbot_sessions`)
- Логи дій у Supabase (таблиця `userbot_actions`)
- **sync_mage_groups.py** — автосинхрон груп з Telegram діалогів

**Проблеми та рішення:**
- `SendReactionRequest` замість `msg.react` (Telethon 1.x сумісність)
- Fallback реакція 👍 для груп з обмеженими реакціями
- Фільтр `assigned_mage` case-sensitive (luna → LUNA)
- `count_actions_today`: fallback 999→0, формат дати без timezone

### БЛОК 4c — Живі промпти магів з анонсом артефактів ✅ (НОВЕ)
- Маги поступово розкривають існування Академії через 3 шари
- **AnnouncementState** у Supabase — трекінг шарів анонсів per user per agent
- Шар 1: натяк на спільноту (після 5 обмінів)
- Шар 2: згадка про артефакти (після +3 обмінів)
- Шар 3: пряме запрошення (після +3 обмінів)
- Кодові слова знання: `LUNA:wolf_vision`, `ARCAS:shaman_card`, `NUMI:cycle_nine`, `UMBRA:beekeeper_shadow`
- Плітки Академії (AcademyGossip) — маги органічно вплітають в розмови
- Рівні розкриття: 0 (гість) → 1 (авторизований) → 2 (8+ повідомлень) → 3 (2+ маги)

### БЛОК 4d — Instagram діалоги в гілках коментарів ✅ (НОВЕ)
- Відповіді в гілках (`reply_to_comment_id`)
- Контекст посту в промпті відповіді
- Редірект після 5 обмінів (CTA з посиланням на сайт)
- Гостьовий route: трекінг кодів знання в localStorage → перенесення в БД після реєстрації
- Автоекстракція імені/дати народження/місця з діалогу мага в профіль

### БЛОК 4e — Facebook моніторинг ✅ (НОВЕ)
- **instagram_comment_monitor.py** обробляє і Facebook і Instagram (MONITOR_PLATFORM)
- Facebook коментарі: перший коментар під постом → відповідь
- Токени: `ACADEMY_PAGE_ACCESS_TOKEN`, `ACADEMY_FB_PAGE_ID`
- Page Access Token (довгострокові, 60 днів) — отримуються через OAuth Desktop App
- Workflows: `facebook-monitor.yml` — кожні 2 год (парні години)
- Виправлено: DM, перший коментар, алерти

### БЛОК 4f — Webhook для Telegram ✅ (НОВЕ)
- `/api/telegram/webhook/[mage]` — окремий endpoint для кожного мага
- Секретна перевірка `X-Telegram-Bot-Api-Secret-Token`
- Fallback для legacy pending updates (без secret header)
- Виправлено `AgentType` import (Prisma vs @lumara/agents)
- Keep-alive механізм для Vercel Functions
- ACADEMY додано в AgentType enum

### БЛОК 4g — Спільна пам'ять магів (user_context) ✅ (НОВЕ)
- Таблиця `user_context` в Supabase — спільна пам'ять для всіх магів одного юзера
- Маги знають що розповідав юзер іншому магу (ім'я, дата народження тощо)
- Автоекстракція `fullName`, `birthDate`, `birthPlace` з діалогу
- RLS політики для захисту даних

### БЛОК 4h — Telegram Monitor (likes_only режим) ✅ (НОВЕ)
- **telegram-monitor.yml** — новий workflow для LUNA і ACADEMY (кожні 2 год)
- `MONITOR_MODE=likes_only` — тільки реакції, без текстових відповідей
- `ACTIVE_MONITOR=luna|academy` — визначає яку реакцію ставити (🌙/👍)
- `_send_reaction()` через Bot API `setMessageReaction` (Bot API 7.0+)
- `_is_topic_relevant()` — перевірка релевантності тексту для monitor

### БЛОК 5 — Відео аватари магів ⏳ (НЕ ПОЧИНАЛИ)
- 1 відео на тиждень × 4 маги
- ElevenLabs API (голос)
- HeyGen API (аватар)
- Автопублікація в Telegram
- Instagram напівавтомат

### БЛОК 6 — Монетизація ⏳
- Реферальна система
- Сезонні події (новолуння, повня)
- Щотижневий публічний розбір в Telegram
- Магазин артефактів (базова структура)
- Опитування курси vs магазин

### БЛОК 7 — Реактивація і утримання ⏳
- М'яка реклама академії і курсів
- Крос-промо між магами (автоматизація)
- Вірусний реферальний механізм

---

## 🔴 ПОТОЧНИЙ СТАН — Що працює прямо зараз

### GitHub Actions (головне репо schemchuk/lumara)
| Workflow | Розклад | Статус |
|---------|---------|--------|
| sync-mages.yml | при push main | ✅ |
| telegram-monitor.yml | кожні 2 год | ✅ LUNA + ACADEMY |
| keep-supabase-alive.yml | 3 рази на день | ✅ |

### GitHub Actions (репо магів — після sync)
| Workflow | Розклад | Статус |
|---------|---------|--------|
| instagram-monitor.yml | кожні 2 год | ✅ всі 5 репо |
| facebook-monitor.yml | парні години | ✅ всі 5 репо |
| daily-post.yml | LUNA: Пн/Пт, ARCAS: Вт, NUMI: Ср, UMBRA: Чт | ✅ |
| academy-weekend.yml | Сб о 10:00 | ✅ |

### Vercel (lumara.fyi)
- Авторизація через Google OAuth та Magic Link ✅
- Чат з магами (LUNA/ARCAS/NUMI/UMBRA) ✅
- Гостьовий чат (без реєстрації, 3 повідомлення) ✅
- Адмін панель /admin (тільки woshem68@gmail.com) ✅
- Адмін панель: Активність, Користувачі, Маги, UserBot, Витрати, Ліміти, Плітки ✅
- UNLIMITED_EMAILS — користувачі з безлімітом (env var) ✅
- Telegram webhook /api/telegram/webhook/[mage] ✅

---

## 🔧 Що потрібно зробити / Відкриті питання

### 1. Додати UNLIMITED_EMAILS у Vercel
```
UNLIMITED_EMAILS = andrejalexandrovic@gmail.com
```
(Vercel Dashboard → lumara → Settings → Environment Variables)

### 2. Налаштувати Telegram Bot Webhook для магів
Для кожного мага (якщо ще не налаштовано):
```bash
curl -X POST "https://api.telegram.org/bot{TOKEN}/setWebhook" \
  -d "url=https://lumara.fyi/api/telegram/webhook/{mage}" \
  -d "secret_token={SECRET}"
```

### 3. UserBot для інших магів (ARCAS, NUMI, UMBRA)
- Поки тільки LUNA і ACADEMY мають UserBot
- Для кожного нового — окремий Telegram акаунт, авторизація, сесія в Supabase

### 4. Оновити Bio у Instagram магів
Вручну (Instagram не дозволяє через API):
- @luna.lumara → lumara.fyi/links/luna
- @arcaslumara → lumara.fyi/links/arcas
- @numi.lumara → lumara.fyi/links/numi
- @umbra.lumara → lumara.fyi/links/umbra

### 5. Twitter/X апеляція
Статус @lumara — заблокований, апеляція подана. Стежити за відповіддю.

---

## 📋 Наступні блоки (ще не починали)

### БЛОК 5 — Відео аватари магів
- 1 відео на тиждень × 4 маги
- ElevenLabs API (голос) + HeyGen API (аватар)
- Автопублікація в Telegram, Instagram напівавтомат

### БЛОК 6 — Монетизація
- Реферальна система
- Сезонні події (новолуння, повня)
- Щотижневий публічний розбір в Telegram
- Магазин артефактів
- Курси

### БЛОК 7 — Реактивація і утримання
- Крос-промо між магами
- Вірусний реферальний механізм

---

## 🔒 Правила проекту

1. **Масштабованість** — кожне рішення для 100 000 користувачів
2. **INSTRUCTIONS.md** — кожен модуль починається з цього файлу
3. **Коміти** — після кожного завершеного блоку, українською
4. **Мова Claude** — завжди українська
5. **Персонажі** — ніколи не розкривають що вони AI
6. **Монетизація** — тільки після статусу підприємця
7. **Гілки** — НЕ створювати окремі гілки, коміт → пуш в main
8. **Промпти** — після зміни markdown: `pnpm --filter @lumara/agents build:prompts`
9. **Передача сесії** — при наближенні до ліміту контексту створити V(n+1).md
10. **Мова магів** — відповідають мовою користувача (UK/RU/EN/DE)
11. **Sync-mages** — будь-які зміни в workflow шаблонах пушити в main → автосинк у всі репо

---

## 👥 Персонажі академії

| Маг | Спеціалізація | Стиль | Telegram | GitHub репо |
|-----|--------------|-------|----------|-------------|
| 🌙 LUNA | Астрологія | М'який, поетичний | @luna_lumara | lunalumarafyi-lab/lumara |
| 🃏 ARCAS | Таро / Оракул | Прямий, гострий | @arcas_lumara | arcaslumara-max/lumara |
| 🔢 NUMI | Нумерологія | Спокійний, аналітичний | @numi_lumara | numilumara-design/lumara |
| 🧠 UMBRA | Езо-психологія | Глибокий, інтенсивний | @umbra_lumara | umbralumara-oss/lumara |
| 🔮 ACADEMY | Академія | — | @lumara_academy | starWoshe/lumara |

---

## 🛠️ Технічний стек
```
Frontend:   Next.js 14, TypeScript, Tailwind CSS, shadcn/ui
Auth:       Supabase SSR (Google OAuth + Magic Link)
Database:   Supabase (PostgreSQL) + Prisma
AI:         Claude API (основний, claude-sonnet-4-6 / claude-opus-4-6)
Payments:   Stripe (тестовий режим)
Email:      Resend
Deploy:     Vercel + GitHub Actions
DNS:        Cloudflare
Content:    Python + Claude API + GitHub Actions (кожен маг своє репо)
UserBot:    Telethon + Supabase sessions
Storage:    Google Drive
Монорепо:   pnpm workspaces + Turbo
Регіон:     fra1 (Frankfurt)
```

---

## 📝 Vercel змінні (є / статус)

### Основні ✅
- ANTHROPIC_API_KEY ✅
- TELEGRAM_BOT_TOKEN ✅
- TELEGRAM_ALERT_BOT_TOKEN ✅
- NEXT_PUBLIC_APP_URL ✅
- NEXT_PUBLIC_SUPABASE_URL ✅
- NEXT_PUBLIC_SUPABASE_ANON_KEY ✅
- SUPABASE_SERVICE_ROLE_KEY ✅
- DATABASE_URL ✅
- DIRECT_URL ✅
- STRIPE_* всі ✅
- CRON_SECRET ✅
- ADMIN_EMAIL ✅ (woshem68@gmail.com)
- GOOGLE_CLIENT_ID ✅
- GOOGLE_CLIENT_SECRET ✅

### Потрібно додати
- `UNLIMITED_EMAILS` — `andrejalexandrovic@gmail.com` (безліміт без адмінки)

---

## 📝 GitHub Secrets (schemchuk/lumara — головне репо)

### Є ✅
- ANTHROPIC_API_KEY, SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY
- IG_ACCESS_TOKEN
- LUNA_IG_USER_ID, ARCAS_IG_USER_ID, NUMI_IG_USER_ID, UMBRA_IG_USER_ID
- LUNA_FB_PAGE_ID, ARCAS_FB_PAGE_ID, NUMI_FB_PAGE_ID, UMBRA_FB_PAGE_ID
- LUNA_PAGE_ACCESS_TOKEN, ARCAS_PAGE_ACCESS_TOKEN, NUMI_PAGE_ACCESS_TOKEN, UMBRA_PAGE_ACCESS_TOKEN
- LUNA_TELEGRAM_CHANNEL_ID, ARCAS_TELEGRAM_CHANNEL_ID, NUMI_TELEGRAM_CHANNEL_ID, UMBRA_TELEGRAM_CHANNEL_ID
- LUNA_TELEGRAM_BOT_TOKEN, ARCAS_TELEGRAM_BOT_TOKEN, NUMI_TELEGRAM_BOT_TOKEN, UMBRA_TELEGRAM_BOT_TOKEN
- LUNA_GITHUB_TOKEN, ARCAS_GITHUB_TOKEN, NUMI_GITHUB_TOKEN, UMBRA_GITHUB_TOKEN, ACADEMY_GITHUB_TOKEN
- ACADEMY_IG_USER_ID, ACADEMY_FB_PAGE_ID, ACADEMY_PAGE_ACCESS_TOKEN
- TELEGRAM_BOT_TOKEN, TELEGRAM_ALERT_BOT_TOKEN
- INSTAGRAM_MAX_PER_DAY, FACEBOOK_MAX_PER_DAY
- OPENAI_API_KEY, DATABASE_URL, DIRECT_URL

---

## 🗄️ Supabase таблиці (є)
```
users                  — користувачі
profiles               — профілі (fullName, birthDate, birthPlace, academyDisclosureLevel...)
agents                 — AI персонажі (blockedUntil для rate limiting)
conversations          — сесії з магами
messages               — повідомлення
subscriptions          — підписки Stripe
content_queue          — черга контенту
outreach_responses     — відповіді в соцмережах
referral_clicks        — кліки по реферальних лінках
monitor_states         — стан моніторингу (offset, last_group_id...)
telegram_groups        — виявлені тематичні групи
userbot_sessions       — Telethon сесії магів
userbot_actions        — логи дій UserBot
userbot_configs        — конфіги UserBot per mage (enabled, mode)
token_usage            — витрати токенів per agent
activity_logs          — активність користувачів
announcement_states    — стан анонсів per user per agent
academy_gossip         — плітки академії для магів
```
