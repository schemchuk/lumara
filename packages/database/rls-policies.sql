-- LUMARA Academy — Row Level Security (RLS) policies
-- Застосовується автоматично через CI/CD (.github/workflows/db-deploy.yml)

-- ──────────────────────────────────────────────────────────────────────────────
-- 1. Увімкнути RLS на всіх таблицях
-- ──────────────────────────────────────────────────────────────────────────────

ALTER TABLE "users"               ENABLE ROW LEVEL SECURITY;
ALTER TABLE "accounts"            ENABLE ROW LEVEL SECURITY;
ALTER TABLE "sessions"            ENABLE ROW LEVEL SECURITY;
ALTER TABLE "verification_tokens" ENABLE ROW LEVEL SECURITY;
ALTER TABLE "profiles"            ENABLE ROW LEVEL SECURITY;
ALTER TABLE "agents"              ENABLE ROW LEVEL SECURITY;
ALTER TABLE "conversations"       ENABLE ROW LEVEL SECURITY;
ALTER TABLE "messages"            ENABLE ROW LEVEL SECURITY;
ALTER TABLE "subscriptions"       ENABLE ROW LEVEL SECURITY;
ALTER TABLE "courses"             ENABLE ROW LEVEL SECURITY;
ALTER TABLE "enrollments"         ENABLE ROW LEVEL SECURITY;
ALTER TABLE "content_queue"       ENABLE ROW LEVEL SECURITY;
ALTER TABLE "activity_logs"       ENABLE ROW LEVEL SECURITY;
ALTER TABLE "token_usage"         ENABLE ROW LEVEL SECURITY;
ALTER TABLE "admin_settings"      ENABLE ROW LEVEL SECURITY;

-- ──────────────────────────────────────────────────────────────────────────────
-- ПРИМІТКА: service_role (Prisma backend) автоматично обходить RLS.
-- Політики нижче захищають прямий доступ через anon/authenticated ключі.
-- ──────────────────────────────────────────────────────────────────────────────

-- ──────────────────────────────────────────────────────────────────────────────
-- 2. users
-- ──────────────────────────────────────────────────────────────────────────────

DROP POLICY IF EXISTS "users: власний перегляд" ON "users";
CREATE POLICY "users: власний перегляд"
  ON "users" FOR SELECT
  TO authenticated
  USING (auth.uid()::text = id::text);

DROP POLICY IF EXISTS "users: власне оновлення" ON "users";
CREATE POLICY "users: власне оновлення"
  ON "users" FOR UPDATE
  TO authenticated
  USING (auth.uid()::text = id::text)
  WITH CHECK (auth.uid()::text = id::text);

-- ──────────────────────────────────────────────────────────────────────────────
-- 3. accounts (NextAuth — тільки через backend)
-- ──────────────────────────────────────────────────────────────────────────────

DROP POLICY IF EXISTS "accounts: власний перегляд" ON "accounts";
CREATE POLICY "accounts: власний перегляд"
  ON "accounts" FOR SELECT
  TO authenticated
  USING (auth.uid()::text = user_id::text);

-- ──────────────────────────────────────────────────────────────────────────────
-- 4. sessions (NextAuth — тільки через backend)
-- ──────────────────────────────────────────────────────────────────────────────

DROP POLICY IF EXISTS "sessions: власний перегляд" ON "sessions";
CREATE POLICY "sessions: власний перегляд"
  ON "sessions" FOR SELECT
  TO authenticated
  USING (auth.uid()::text = user_id::text);

-- ──────────────────────────────────────────────────────────────────────────────
-- 5. verification_tokens (NextAuth — тільки через backend, без user_id)
-- ──────────────────────────────────────────────────────────────────────────────
-- Немає user_id, тому доступ тільки через service_role (Prisma)
-- Жодних публічних політик — RLS блокує прямий доступ

-- ──────────────────────────────────────────────────────────────────────────────
-- 6. profiles
-- ──────────────────────────────────────────────────────────────────────────────

DROP POLICY IF EXISTS "profiles: власний перегляд" ON "profiles";
CREATE POLICY "profiles: власний перегляд"
  ON "profiles" FOR SELECT
  TO authenticated
  USING (auth.uid()::text = user_id::text);

DROP POLICY IF EXISTS "profiles: власне створення" ON "profiles";
CREATE POLICY "profiles: власне створення"
  ON "profiles" FOR INSERT
  TO authenticated
  WITH CHECK (auth.uid()::text = user_id::text);

DROP POLICY IF EXISTS "profiles: власне оновлення" ON "profiles";
CREATE POLICY "profiles: власне оновлення"
  ON "profiles" FOR UPDATE
  TO authenticated
  USING (auth.uid()::text = user_id::text)
  WITH CHECK (auth.uid()::text = user_id::text);

-- ──────────────────────────────────────────────────────────────────────────────
-- 7. agents (публічно читаються всіма — це контент-персонажі)
-- ──────────────────────────────────────────────────────────────────────────────

DROP POLICY IF EXISTS "agents: публічний перегляд активних" ON "agents";
CREATE POLICY "agents: публічний перегляд активних"
  ON "agents" FOR SELECT
  TO authenticated, anon
  USING (is_active = true AND deleted_at IS NULL);

-- ──────────────────────────────────────────────────────────────────────────────
-- 8. conversations
-- ──────────────────────────────────────────────────────────────────────────────

DROP POLICY IF EXISTS "conversations: власний перегляд" ON "conversations";
CREATE POLICY "conversations: власний перегляд"
  ON "conversations" FOR SELECT
  TO authenticated
  USING (auth.uid()::text = user_id::text AND deleted_at IS NULL);

DROP POLICY IF EXISTS "conversations: власне створення" ON "conversations";
CREATE POLICY "conversations: власне створення"
  ON "conversations" FOR INSERT
  TO authenticated
  WITH CHECK (auth.uid()::text = user_id::text);

DROP POLICY IF EXISTS "conversations: власне оновлення" ON "conversations";
CREATE POLICY "conversations: власне оновлення"
  ON "conversations" FOR UPDATE
  TO authenticated
  USING (auth.uid()::text = user_id::text);

-- ──────────────────────────────────────────────────────────────────────────────
-- 9. messages (через conversations)
-- ──────────────────────────────────────────────────────────────────────────────

DROP POLICY IF EXISTS "messages: перегляд своїх розмов" ON "messages";
CREATE POLICY "messages: перегляд своїх розмов"
  ON "messages" FOR SELECT
  TO authenticated
  USING (
    EXISTS (
      SELECT 1 FROM "conversations" c
      WHERE c.id = conversation_id
        AND auth.uid()::text = c.user_id::text
        AND c.deleted_at IS NULL
    )
  );

DROP POLICY IF EXISTS "messages: створення в своїх розмовах" ON "messages";
CREATE POLICY "messages: створення в своїх розмовах"
  ON "messages" FOR INSERT
  TO authenticated
  WITH CHECK (
    EXISTS (
      SELECT 1 FROM "conversations" c
      WHERE c.id = conversation_id
        AND auth.uid()::text = c.user_id::text
    )
  );

-- ──────────────────────────────────────────────────────────────────────────────
-- 10. subscriptions
-- ──────────────────────────────────────────────────────────────────────────────

DROP POLICY IF EXISTS "subscriptions: власний перегляд" ON "subscriptions";
CREATE POLICY "subscriptions: власний перегляд"
  ON "subscriptions" FOR SELECT
  TO authenticated
  USING (auth.uid()::text = user_id::text AND deleted_at IS NULL);

-- ──────────────────────────────────────────────────────────────────────────────
-- 11. courses (опубліковані — публічні)
-- ──────────────────────────────────────────────────────────────────────────────

DROP POLICY IF EXISTS "courses: публічний перегляд опублікованих" ON "courses";
CREATE POLICY "courses: публічний перегляд опублікованих"
  ON "courses" FOR SELECT
  TO authenticated, anon
  USING (is_published = true AND deleted_at IS NULL);

-- ──────────────────────────────────────────────────────────────────────────────
-- 12. enrollments
-- ──────────────────────────────────────────────────────────────────────────────

DROP POLICY IF EXISTS "enrollments: власний перегляд" ON "enrollments";
CREATE POLICY "enrollments: власний перегляд"
  ON "enrollments" FOR SELECT
  TO authenticated
  USING (auth.uid()::text = user_id::text AND deleted_at IS NULL);

DROP POLICY IF EXISTS "enrollments: власне створення" ON "enrollments";
CREATE POLICY "enrollments: власне створення"
  ON "enrollments" FOR INSERT
  TO authenticated
  WITH CHECK (auth.uid()::text = user_id::text);

-- ──────────────────────────────────────────────────────────────────────────────
-- 13. content_queue (тільки backend/admin — жодних публічних політик)
-- ──────────────────────────────────────────────────────────────────────────────
-- Доступ тільки через service_role (GitHub Actions, Prisma)
-- RLS заблокує будь-який прямий доступ через anon/authenticated

-- ──────────────────────────────────────────────────────────────────────────────
-- 14. activity_logs
-- ──────────────────────────────────────────────────────────────────────────────

DROP POLICY IF EXISTS "activity_logs: власний перегляд" ON "activity_logs";
CREATE POLICY "activity_logs: власний перегляд"
  ON "activity_logs" FOR SELECT
  TO authenticated
  USING (auth.uid()::text = user_id::text);

-- ──────────────────────────────────────────────────────────────────────────────
-- 15. token_usage
-- ──────────────────────────────────────────────────────────────────────────────

DROP POLICY IF EXISTS "token_usage: власний перегляд" ON "token_usage";
CREATE POLICY "token_usage: власний перегляд"
  ON "token_usage" FOR SELECT
  TO authenticated
  USING (auth.uid()::text = user_id::text);

-- ──────────────────────────────────────────────────────────────────────────────
-- 16. admin_settings (тільки backend/admin — жодних публічних політик)
-- ──────────────────────────────────────────────────────────────────────────────
-- Доступ тільки через service_role (Prisma backend)
-- RLS заблокує будь-який прямий доступ через anon/authenticated

-- ──────────────────────────────────────────────────────────────────────────────
-- 17. outreach_responses (тільки backend/admin — жодних публічних політик)
-- ──────────────────────────────────────────────────────────────────────────────

ALTER TABLE "outreach_responses" ENABLE ROW LEVEL SECURITY;

-- ──────────────────────────────────────────────────────────────────────────────
-- 18. referral_clicks (anon може створювати для трекінгу)
-- ──────────────────────────────────────────────────────────────────────────────

ALTER TABLE "referral_clicks" ENABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS "referral_clicks: anon insert" ON "referral_clicks";
CREATE POLICY "referral_clicks: anon insert"
  ON "referral_clicks" FOR INSERT
  TO anon
  WITH CHECK (true);

-- ──────────────────────────────────────────────────────────────────────────────
-- 19. announcement_states (власний перегляд)
-- ──────────────────────────────────────────────────────────────────────────────

ALTER TABLE "announcement_states" ENABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS "announcement_states: власний перегляд" ON "announcement_states";
CREATE POLICY "announcement_states: власний перегляд"
  ON "announcement_states" FOR SELECT
  TO authenticated
  USING (auth.uid()::text = user_id::text);

-- ──────────────────────────────────────────────────────────────────────────────
-- 20. monitor_states (тільки backend)
-- ──────────────────────────────────────────────────────────────────────────────

ALTER TABLE "monitor_states" ENABLE ROW LEVEL SECURITY;

-- ──────────────────────────────────────────────────────────────────────────────
-- 21. telegram_groups (тільки backend/admin)
-- ──────────────────────────────────────────────────────────────────────────────

ALTER TABLE "telegram_groups" ENABLE ROW LEVEL SECURITY;

-- ──────────────────────────────────────────────────────────────────────────────
-- 22. user_context (власний перегляд)
-- ──────────────────────────────────────────────────────────────────────────────

ALTER TABLE "user_context" ENABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS "user_context: власний перегляд" ON "user_context";
CREATE POLICY "user_context: власний перегляд"
  ON "user_context" FOR SELECT
  TO authenticated
  USING (auth.uid()::text = user_id::text);

-- ──────────────────────────────────────────────────────────────────────────────
-- 23. telegram_conversations (тільки backend — webhook від бота)
-- ──────────────────────────────────────────────────────────────────────────────

ALTER TABLE "telegram_conversations" ENABLE ROW LEVEL SECURITY;

-- ──────────────────────────────────────────────────────────────────────────────
-- 24. verification_tokens (NextAuth — тільки через backend)
-- ──────────────────────────────────────────────────────────────────────────────
-- Немає user_id, тому доступ тільки через service_role (Prisma)
-- Жодних публічних політик — RLS блокує прямий доступ

-- ──────────────────────────────────────────────────────────────────────────────
-- 25. monitored_groups (тільки backend / admin)
-- ──────────────────────────────────────────────────────────────────────────────

ALTER TABLE "monitored_groups" ENABLE ROW LEVEL SECURITY;

-- ──────────────────────────────────────────────────────────────────────────────
-- 26. userbot_sessions (тільки backend)
-- ──────────────────────────────────────────────────────────────────────────────

ALTER TABLE "userbot_sessions" ENABLE ROW LEVEL SECURITY;

-- ──────────────────────────────────────────────────────────────────────────────
-- 27. userbot_logs (тільки backend / admin)
-- ──────────────────────────────────────────────────────────────────────────────

ALTER TABLE "userbot_logs" ENABLE ROW LEVEL SECURITY;

-- ──────────────────────────────────────────────────────────────────────────────
-- 28. GRANT: явні дозволи для доступу через Supabase PostgREST/API
-- З 30.05.2026 Supabase вимагає явні GRANT для таблиць у схемі public.
-- service_role отримує ALL (вона обходить RLS), authenticated/anon отримують
-- SELECT + write-дозволи відповідно до політик вище.
-- ──────────────────────────────────────────────────────────────────────────────

GRANT USAGE ON SCHEMA public TO anon, authenticated, service_role;

-- Базовий SELECT для authenticated/anon на всі таблиці з RLS політиками
GRANT SELECT ON "users" TO authenticated;
GRANT SELECT ON "accounts" TO authenticated;
GRANT SELECT ON "sessions" TO authenticated;
GRANT SELECT ON "profiles" TO authenticated;
GRANT SELECT ON "agents" TO anon, authenticated;
GRANT SELECT ON "conversations" TO authenticated;
GRANT SELECT ON "messages" TO authenticated;
GRANT SELECT ON "subscriptions" TO authenticated;
GRANT SELECT ON "courses" TO anon, authenticated;
GRANT SELECT ON "enrollments" TO authenticated;
GRANT SELECT ON "activity_logs" TO authenticated;
GRANT SELECT ON "token_usage" TO authenticated;
GRANT SELECT ON "announcement_states" TO authenticated;
GRANT SELECT ON "user_context" TO authenticated;
GRANT SELECT ON "outreach_responses" TO authenticated;
GRANT SELECT ON "referral_clicks" TO anon, authenticated;
GRANT SELECT ON "monitor_states" TO service_role;
GRANT SELECT ON "telegram_groups" TO service_role;
GRANT SELECT ON "telegram_conversations" TO service_role;
GRANT SELECT ON "monitored_groups" TO service_role;
GRANT SELECT ON "userbot_sessions" TO service_role;
GRANT SELECT ON "userbot_logs" TO service_role;
GRANT SELECT ON "content_queue" TO service_role;
GRANT SELECT ON "admin_settings" TO service_role;
GRANT SELECT ON "verification_tokens" TO service_role;
GRANT SELECT ON "academy_gossip" TO anon, authenticated;

-- Write-дозволи відповідно до RLS політик
GRANT INSERT, UPDATE ON "users" TO authenticated;
GRANT INSERT, UPDATE ON "profiles" TO authenticated;
GRANT INSERT, UPDATE ON "conversations" TO authenticated;
GRANT INSERT ON "messages" TO authenticated;
GRANT INSERT ON "enrollments" TO authenticated;
GRANT INSERT ON "referral_clicks" TO anon;

-- service_role: повний доступ на всі таблиці (backend, Python скрипти, Prisma)
GRANT ALL ON "users" TO service_role;
GRANT ALL ON "accounts" TO service_role;
GRANT ALL ON "sessions" TO service_role;
GRANT ALL ON "profiles" TO service_role;
GRANT ALL ON "agents" TO service_role;
GRANT ALL ON "conversations" TO service_role;
GRANT ALL ON "messages" TO service_role;
GRANT ALL ON "subscriptions" TO service_role;
GRANT ALL ON "courses" TO service_role;
GRANT ALL ON "enrollments" TO service_role;
GRANT ALL ON "activity_logs" TO service_role;
GRANT ALL ON "token_usage" TO service_role;
GRANT ALL ON "announcement_states" TO service_role;
GRANT ALL ON "user_context" TO service_role;
GRANT ALL ON "outreach_responses" TO service_role;
GRANT ALL ON "referral_clicks" TO service_role;
GRANT ALL ON "monitor_states" TO service_role;
GRANT ALL ON "telegram_groups" TO service_role;
GRANT ALL ON "telegram_conversations" TO service_role;
GRANT ALL ON "monitored_groups" TO service_role;
GRANT ALL ON "userbot_sessions" TO service_role;
GRANT ALL ON "userbot_logs" TO service_role;
GRANT ALL ON "content_queue" TO service_role;
GRANT ALL ON "admin_settings" TO service_role;
GRANT ALL ON "verification_tokens" TO service_role;
GRANT ALL ON "academy_gossip" TO service_role;
