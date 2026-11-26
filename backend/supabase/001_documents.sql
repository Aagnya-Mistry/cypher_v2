-- Run once in Supabase > SQL Editor > New query.
-- Creates the table for uploaded reports and a private Storage bucket for the PDFs.

create table if not exists public.documents (
  id                uuid primary key default gen_random_uuid(),
  user_id           uuid not null references auth.users (id) on delete cascade,
  company_name      text not null,
  fiscal_year       text not null,
  original_filename text not null,
  storage_path      text not null,
  sha256            text not null,
  size_bytes        bigint not null,
  page_count        integer not null,
  status            text not null default 'uploaded',
  created_at        timestamptz not null default now(),
  unique (user_id, sha256)   -- the same user can't store the same file twice
);

create index if not exists documents_user_created_idx on public.documents (user_id, created_at desc);

-- Row Level Security on, with no policies: the browser's publishable key can't read or write
-- this table at all. Only our backend (secret key) can, and it filters by the logged-in user.
alter table public.documents enable row level security;

-- Private bucket: files are never publicly downloadable. 50 MB limit, PDFs only.
insert into storage.buckets (id, name, public, file_size_limit, allowed_mime_types)
values ('documents', 'documents', false, 52428800, array['application/pdf'])
on conflict (id) do nothing;
