-- Add Soft Delete flags to triages table
ALTER TABLE public.triages 
ADD COLUMN IF NOT EXISTS patient_hidden BOOLEAN DEFAULT FALSE,
ADD COLUMN IF NOT EXISTS doctor_hidden BOOLEAN DEFAULT FALSE;

-- Ensure RLS allows updates to these flags
CREATE POLICY "Patients can update their own triages" ON public.triages FOR UPDATE USING (auth.uid() = patient_id);
-- (Doctors already have broad access or we can add a specific policy if needed, 
-- but usually doctors update via backend or existing policies)
