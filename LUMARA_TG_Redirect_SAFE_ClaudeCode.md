# ЗАВДАННЯ: Система редірект-посилань для магів LUMARA
## Безпечна версія для Claude Code

*Квітень 2026*

---

## 🎯 Мета

Створити систему редірект-сторінок `lumara.fyi/tg/[маг]` яка:
- Коректно відкривається з Instagram і Facebook
- Миттєво перенаправляє користувача в Telegram канал мага
- Кожен маг і академія мають окремий URL

---

## ❌ Проблема яку вирішуємо

Instagram і Facebook блокують:
1. Прямі Telegram посилання — відкривається сторінка що безкінечно завантажується
2. @нікнейми в тексті — повністю неклікабельні

Telegram — працює нормально, там прямі посилання залишаємо як є.

---

## ✅ Логіка рішення

```
Користувач в Instagram бачить: lumara.fyi/tg/luna
        ↓ клікає (Instagram пропускає — це зовнішній сайт)
lumara.fyi/tg/luna відкривається
        ↓ HTML meta refresh + JavaScript (0 секунд)
Telegram канал LUNA відкривається ✅
```

---

## 📋 Змінні середовища

**Всі значення вже є в:**
`C:\Users\shemc\myVSCodeProjects\lumara\.env.local`

**Використовуй існуючі назви змінних з .env.local без перейменування.**

Потрібні змінні (назви можуть відрізнятись — перевір в .env.local):

```
# Invite посилання для кожного Telegram каналу
TG_LINK_LUNA        ← посилання на канал LUNA
TG_LINK_ARCAS       ← посилання на канал ARCAS
TG_LINK_NUMI        ← посилання на канал NUMI
TG_LINK_UMBRA       ← посилання на канал UMBRA
TG_LINK_ACADEMY     ← посилання на канал ACADEMY

# Channel IDs (для відправки повідомлень)
CHANNEL_ID_LUNA
CHANNEL_ID_ARCAS
CHANNEL_ID_NUMI
CHANNEL_ID_UMBRA
CHANNEL_ID_ACADEMY
```

Якщо назви в .env.local відрізняються — використовуй ті що є, не перейменовуй.

---

## 🗺️ URL які потрібно створити

| URL (для Instagram/Facebook) | Telegram канал |
|------------------------------|---------------|
| `lumara.fyi/tg/luna` | LUNA |
| `lumara.fyi/tg/arcas` | ARCAS |
| `lumara.fyi/tg/numi` | NUMI |
| `lumara.fyi/tg/umbra` | UMBRA |
| `lumara.fyi/tg/academy` | LUMARA Academy |

---

## 🏗️ Реалізація

### Файл 1 — Route Handler

Створити: `apps/web/app/tg/[mage]/route.ts`

```typescript
import { NextResponse } from 'next/server'

// Читаємо посилання з .env.local
// Назви змінних уточни з існуючого .env.local
const TELEGRAM_LINKS: Record<string, string> = {
  luna: process.env.TG_LINK_LUNA!,
  arcas: process.env.TG_LINK_ARCAS!,
  numi: process.env.TG_LINK_NUMI!,
  umbra: process.env.TG_LINK_UMBRA!,
  academy: process.env.TG_LINK_ACADEMY!,
}

const MAGE_NAMES: Record<string, string> = {
  luna: 'LUNA · Астролог',
  arcas: 'ARCAS · Таролог',
  numi: 'NUMI · Нумеролог',
  umbra: 'UMBRA · Езо-психолог',
  academy: 'LUMARA Academy',
}

const MAGE_DESCRIPTIONS: Record<string, string> = {
  luna: 'Зірки говорять особисто до тебе 🌙',
  arcas: 'Карти не передбачають — вони відображають 🃏',
  numi: 'Всесвіт говорить числами 🔢',
  umbra: 'Твоя тінь знає більше ніж ти думаєш 🧠',
  academy: 'Illuminate your path ✨',
}

export async function GET(
  request: Request,
  { params }: { params: { mage: string } }
) {
  const mage = params.mage.toLowerCase()
  const telegramUrl = TELEGRAM_LINKS[mage]

  if (!telegramUrl) {
    return NextResponse.redirect(new URL('/', request.url))
  }

  const name = MAGE_NAMES[mage]
  const description = MAGE_DESCRIPTIONS[mage]

  // HTML сторінка з миттєвим редіректом
  // meta refresh + JS — подвійна гарантія
  return new NextResponse(
    `<!DOCTYPE html>
<html lang="uk">
  <head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <meta http-equiv="refresh" content="0;url=${telegramUrl}">
    <meta property="og:title" content="${name} · LUMARA Academy">
    <meta property="og:description" content="${description}">
    <meta property="og:image" content="https://lumara.fyi/og/${mage}.jpg">
    <meta property="og:url" content="https://lumara.fyi/tg/${mage}">
    <meta property="og:type" content="website">
    <title>${name} · LUMARA Academy</title>
    <style>
      body {
        background: #0D1B2A;
        color: #F9CB42;
        font-family: serif;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        min-height: 100vh;
        margin: 0;
        text-align: center;
        padding: 20px;
      }
      h1 { font-size: 24px; margin-bottom: 8px; }
      p { color: #1D9E75; margin-bottom: 24px; }
      a {
        color: #F9CB42;
        border: 1px solid #F9CB42;
        padding: 12px 24px;
        border-radius: 8px;
        text-decoration: none;
      }
    </style>
    <script>window.location.replace("${telegramUrl}");</script>
  </head>
  <body>
    <h1>${name}</h1>
    <p>${description}</p>
    <a href="${telegramUrl}">Відкрити Telegram →</a>
  </body>
</html>`,
    {
      status: 200,
      headers: {
        'Content-Type': 'text/html; charset=utf-8',
        'Cache-Control': 'no-cache',
      },
    }
  )
}
```

---

### Файл 2 — Оновити Instagram коментарі

Знайти в проекті файл де визначені `IG_FIRST_COMMENTS` або перший коментар під Instagram постом.

Замінити всі прямі Telegram посилання на редірект через сайт:

```python
# БУЛО (не працює в Instagram):
# "📲 Telegram: @luna_lumara"
# "📲 Telegram: t.me/+..."

# СТАЛО (працює в Instagram):
IG_FIRST_COMMENTS = {
    'luna': (
        "✨ Хочеш дізнатись більше особисто?\n"
        "🌙 Telegram LUNA: lumara.fyi/tg/luna\n"
        "🔮 Академія: lumara.fyi"
    ),
    'arcas': (
        "🃏 Карти можуть розказати більше особисто.\n"
        "🃏 Telegram ARCAS: lumara.fyi/tg/arcas\n"
        "🔮 Академія: lumara.fyi"
    ),
    'numi': (
        "🔢 Твої числа чекають розрахунку.\n"
        "🔢 Telegram NUMI: lumara.fyi/tg/numi\n"
        "🔮 Академія: lumara.fyi"
    ),
    'umbra': (
        "🌑 Тінь знає більше ніж ти думаєш.\n"
        "🧠 Telegram UMBRA: lumara.fyi/tg/umbra\n"
        "🔮 Академія: lumara.fyi"
    ),
    'academy': (
        "🔮 LUMARA Academy\n"
        "✨ lumara.fyi/tg/academy\n"
        "🌙 lumara.fyi"
    ),
}
```

---

### Файл 3 — Додати в GitHub Secrets

Додати ті самі змінні що є в `.env.local` в:
`GitHub → Repository → Settings → Secrets → Actions`

Щоб GitHub Actions також мав доступ до посилань при автопублікації.

---

## ✅ Чеклист

- [ ] Перевірити назви змінних в `.env.local` і підставити правильні в `route.ts`
- [ ] Створити `apps/web/app/tg/[mage]/route.ts`
- [ ] Оновити `IG_FIRST_COMMENTS` — замінити прямі Telegram посилання
- [ ] Додати змінні в GitHub Secrets
- [ ] Коміт: `feat: редірект-посилання /tg для Instagram і Facebook`
- [ ] Деплой на Vercel
- [ ] Перевірити всі 5 посилань вручну в браузері

---

## 🧪 Перевірка після деплою

```bash
curl -I https://lumara.fyi/tg/luna
curl -I https://lumara.fyi/tg/arcas
curl -I https://lumara.fyi/tg/numi
curl -I https://lumara.fyi/tg/umbra
curl -I https://lumara.fyi/tg/academy
```

Кожне має повертати `200 OK` і відкривати Telegram без зависання.

---

## ⚠️ Правила безпеки

- Invite links — тільки в `.env.local` і GitHub Secrets
- В публічному коді — тільки через `process.env.НАЗВА_ЗМІННОЇ`
- `.env.local` не комітити в Git (має бути в `.gitignore`)

---

*LUMARA Academy · lumara.fyi · 🌙🃏🧠🔢 · Квітень 2026*
