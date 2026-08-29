DROP POLICY IF EXISTS ""Doctors can view all users"" ON public.users;
DROP POLICY IF EXISTS ""Allow authenticated to read users"" ON public.users;
CREATE POLICY ""Allow authenticated to read users"" ON public.users FOR SELECT USING (auth.role() = 'authenticated');
