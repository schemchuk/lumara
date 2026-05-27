-- LUMARA Academy — автоматичне надання дозволів для Supabase PostgREST/API
-- З 30 травня 2026 нові таблиці у схемі public потребують явного GRANT.
-- Цей скрипт виконується в CI/CD після створення/оновлення таблиць.
-- https://github.com/orgs/supabase/discussions/9314

GRANT USAGE ON SCHEMA public TO anon, authenticated, service_role;

-- Функція для автоматичного grant всіх існуючих таблиць у схемі public
CREATE OR REPLACE FUNCTION public.grant_public_tables()
RETURNS void
LANGUAGE plpgsql
SECURITY DEFINER
AS $$
DECLARE
  r RECORD;
BEGIN
  FOR r IN
    SELECT tablename FROM pg_tables WHERE schemaname = 'public'
  LOOP
    -- service_role: повний доступ (вона обходить RLS, але потребує GRANT для PostgREST)
    EXECUTE format('GRANT ALL ON TABLE %I TO service_role', r.tablename);

    -- anon та authenticated: базовий SELECT (RLS політики контролюють доступ до рядків)
    EXECUTE format('GRANT SELECT ON TABLE %I TO anon, authenticated', r.tablename);
  END LOOP;
END;
$$;

-- Застосувати до всіх існуючих таблиць
SELECT public.grant_public_tables();
