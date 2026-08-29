-- Enable pgvector extension
create extension if not exists vector;

-- Users table (extends Supabase auth.users)
create table public.users (
  id uuid references auth.users not null primary key,
  role text not null check (role in ('patient', 'doctor', 'admin')),
  full_name text,
  created_at timestamp with time zone default timezone('utc'::text, now()) not null
);

-- Triage Reports table (stores AI generated reports)
create table public.triage_reports (
  id uuid default gen_random_uuid() primary key,
  patient_id uuid references public.users(id) not null,
  symptoms text not null,
  urgency_level text check (urgency_level in ('Low', 'Medium', 'High')),
  recommended_department text,
  ai_explanation text,
  created_at timestamp with time zone default timezone('utc'::text, now()) not null
);

-- Appointments table
create table public.appointments (
  id uuid default gen_random_uuid() primary key,
  patient_id uuid references public.users(id) not null,
  doctor_id uuid references public.users(id) not null,
  triage_report_id uuid references public.triage_reports(id),
  department text not null,
  appointment_time timestamp with time zone not null,
  status text default 'scheduled' check (status in ('scheduled', 'completed', 'cancelled')),
  created_at timestamp with time zone default timezone('utc'::text, now()) not null
);

-- Medical Knowledge Base (for RAG)
create table public.medical_knowledge (
  id uuid default gen_random_uuid() primary key,
  symptom text not null,
  condition text not null,
  department text not null,
  urgency text not null,
  embedding vector(768) -- Assuming 768 dimensions for embedding
);

-- Set up Row Level Security (RLS)
alter table public.users enable row level security;
alter table public.triage_reports enable row level security;
alter table public.appointments enable row level security;

-- Create basic policies (In production, these should be stricter)
create policy "Users can view their own profile." on public.users for select using (auth.uid() = id);
create policy "Users can view their own reports." on public.triage_reports for select using (auth.uid() = patient_id);
create policy "Doctors can view all reports." on public.triage_reports for select using (
  exists (select 1 from public.users where id = auth.uid() and role = 'doctor')
);

-- Match medical knowledge using vector similarity
create or replace function match_medical_knowledge (
  query_embedding vector(768),
  match_threshold float,
  match_count int
)
returns table (
  id uuid,
  symptom text,
  condition text,
  department text,
  urgency text,
  similarity float
)
language sql stable
as $$
  select
    medical_knowledge.id,
    medical_knowledge.symptom,
    medical_knowledge.condition,
    medical_knowledge.department,
    medical_knowledge.urgency,
    1 - (medical_knowledge.embedding <=> query_embedding) as similarity
  from medical_knowledge
  where 1 - (medical_knowledge.embedding <=> query_embedding) > match_threshold
  order by similarity desc
  limit match_count;
$$;
