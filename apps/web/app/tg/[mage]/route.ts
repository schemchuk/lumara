import { NextResponse } from 'next/server'

// Назви змінних відповідають .env.local (NEXT_PUBLIC_TG_*)
const TELEGRAM_LINKS: Record<string, string | undefined> = {
  luna: process.env.NEXT_PUBLIC_TG_LUNA,
  arcas: process.env.NEXT_PUBLIC_TG_ARCAS,
  numi: process.env.NEXT_PUBLIC_TG_NUMI,
  umbra: process.env.NEXT_PUBLIC_TG_UMBRA,
  academy: process.env.NEXT_PUBLIC_TG_ACADEMY,
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

  const name = MAGE_NAMES[mage] ?? 'LUMARA Academy'
  const description = MAGE_DESCRIPTIONS[mage] ?? ''

  const html = `<!DOCTYPE html>
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
</html>`

  return new NextResponse(html, {
    status: 200,
    headers: {
      'Content-Type': 'text/html; charset=utf-8',
      'Cache-Control': 'no-cache',
    },
  })
}
