-- Enable UUID extension
create extension if not exists "uuid-ossp";

-- Users Table
create table if not exists users (
  id uuid default uuid_generate_v4() primary key,
  email text unique not null,
  username text unique not null,
  password_hash text not null,
  created_at timestamp with time zone default timezone('utc'::text, now()) not null
);

-- Conversations Table (Private Chats)
create table if not exists conversations (
  id uuid default uuid_generate_v4() primary key,
  created_at timestamp with time zone default timezone('utc'::text, now()) not null,
  updated_at timestamp with time zone default timezone('utc'::text, now()) not null
);

-- Participants Table (Who is in which conversation)
create table if not exists participants (
  conversation_id uuid references conversations(id) on delete cascade not null,
  user_id uuid references users(id) on delete cascade not null,
  joined_at timestamp with time zone default timezone('utc'::text, now()) not null,
  primary key (conversation_id, user_id)
);

-- Add indexes for performance
create index if not exists idx_participants_user_id on participants(user_id);
create index if not exists idx_participants_conversation_id on participants(conversation_id);

-- Update Messages Table (add moderation columns)
-- Run these only if columns don't exist (manual check might be needed or catch errors)
alter table messages add column if not exists moderation_status text default 'pending'; -- 'pending', 'allowed', 'flagged', 'blocked'
alter table messages add column if not exists moderation_details jsonb;

-- Policy helper (if RLS is enabled, but we are using service role for backend usually, 
-- though Supabase-py is client. We assume backend handles auth logic for now).
