DROP POLICY IF EXISTS ""Allow anon insert users"" ON public.users;
CREATE POLICY ""Allow anon insert users"" ON public.users FOR INSERT WITH CHECK (true);
