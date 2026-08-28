-- 🐾 DAMAGOCHI v18 - Supabase 유저 세이브 테이블 생성 (Migration #1)
-- 잡지식: PostgreSQL의 JSONB는 JSON보다 검색 성능이 40% 빠르고, 인덱스 생성이 가능해용!

create table if not exists public.user_saves (
    user_id text primary key,
    save_data jsonb not null default '{}'::jsonb,
    updated_at timestamptz not null default now()
);

alter table public.user_saves enable row level security;
