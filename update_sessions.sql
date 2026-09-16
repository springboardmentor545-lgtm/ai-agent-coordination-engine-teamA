-- Create chat_sessions table
CREATE TABLE IF NOT EXISTS public.chat_sessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    patient_id UUID REFERENCES public.users(id) ON DELETE CASCADE NOT NULL,
    title TEXT NOT NULL,
    created_at TIMESTAMPTZ DEFAULT now()
);

-- Add session_id to chat_history
ALTER TABLE public.chat_history 
ADD COLUMN session_id UUID REFERENCES public.chat_sessions(id) ON DELETE CASCADE;

-- Enable Row Level Security (RLS) on chat_sessions
ALTER TABLE public.chat_sessions ENABLE ROW LEVEL SECURITY;

-- Policy to allow users to see their own sessions
CREATE POLICY "Users can view their own chat sessions"
ON public.chat_sessions FOR SELECT
TO authenticated
USING (auth.uid() = patient_id);

-- Policy to allow users to insert their own sessions
CREATE POLICY "Users can insert their own chat sessions"
ON public.chat_sessions FOR INSERT
TO authenticated
WITH CHECK (auth.uid() = patient_id);

-- Policy to allow users to update their own sessions
CREATE POLICY "Users can update their own chat sessions"
ON public.chat_sessions FOR UPDATE
TO authenticated
USING (auth.uid() = patient_id);

-- Policy to allow users to delete their own sessions
CREATE POLICY "Users can delete their own chat sessions"
ON public.chat_sessions FOR DELETE
TO authenticated
USING (auth.uid() = patient_id);

-- Update RLS for chat_history if needed (optional)
-- The existing policy for chat_history based on patient_id should still apply.
