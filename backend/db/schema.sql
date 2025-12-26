-- Enable UUID extension
create extension if not exists "uuid-ossp";

-- Messages Table
create table public.messages (
  id uuid default uuid_generate_v4() primary key,
  room_id text not null,
  user_id text not null,
  content text,
  type text default 'text', -- text, image, video, document
  file_url text,
  status text default 'allowed', -- pending, allowed, warning, blocked
  created_at timestamp with time zone default timezone('utc'::text, now()) not null
);

-- Enable RLS
alter table public.messages enable row level security;

-- Policy: Allow read access to all (for this demo)
create policy "Allow read access for all"
  on public.messages for select
  using (true);

-- Policy: Allow insert access to all (usually service role only, but for direct client access if needed)
create policy "Allow insert access for all"
  on public.messages for insert
  with check (true);

-- Moderation Logs Table
create table public.moderation_logs (
  id uuid default uuid_generate_v4() primary key,
  message_id uuid references public.messages(id),
  category text,
  severity text,
  action text,
  confidence float,
  explanation text,
  raw_response jsonb,
  created_at timestamp with time zone default timezone('utc'::text, now()) not null
);

-- Enable RLS
alter table public.moderation_logs enable row level security;

-- Policy: Admin only (conceptually)
create policy "Allow read for admins"
  on public.moderation_logs for select
  using (true); -- Simplified for demo
