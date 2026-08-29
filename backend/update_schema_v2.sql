-- 1. Create chat_history table for Long-Term Memory
CREATE TABLE IF NOT EXISTS public.chat_history (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    patient_id UUID REFERENCES public.users(id) ON DELETE CASCADE,
    sender TEXT NOT NULL CHECK (sender IN ('user', 'ai')),
    message TEXT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL
);

-- 2. Create emergency_alerts table for the Tool Integration
CREATE TABLE IF NOT EXISTS public.emergency_alerts (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    patient_id UUID REFERENCES public.users(id) ON DELETE CASCADE,
    alert_reason TEXT NOT NULL,
    resolved BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL
);

-- Add RLS Policies
ALTER TABLE public.chat_history ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Users can view their own chat history" ON public.chat_history FOR SELECT USING (auth.uid() = patient_id);
CREATE POLICY "Users can insert their own chat history" ON public.chat_history FOR INSERT WITH CHECK (auth.uid() = patient_id);
-- Allow service role full access
CREATE POLICY "Service role full access chat_history" ON public.chat_history USING (true);

ALTER TABLE public.emergency_alerts ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Users can view their own alerts" ON public.emergency_alerts FOR SELECT USING (auth.uid() = patient_id);
CREATE POLICY "Doctors can view all alerts" ON public.emergency_alerts FOR SELECT USING (exists (select 1 from public.users as u where u.id = auth.uid() and u.role = 'doctor'));
CREATE POLICY "Admin can view all alerts" ON public.emergency_alerts FOR SELECT USING (exists (select 1 from public.users as u where u.id = auth.uid() and u.role = 'admin'));
CREATE POLICY "Service role full access emergency_alerts" ON public.emergency_alerts USING (true);
