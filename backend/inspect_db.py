import asyncio
from app.db import get_supabase

async def check_tables():
    supabase = get_supabase()
    tables_to_check = ['triages', 'medical_knowledge', 'users']
    for table in tables_to_check:
        try:
            res = supabase.table(table).select("*").limit(1).execute()
            print(f"Table '{table}' exists. Data: {res.data}")
        except Exception as e:
            print(f"Table '{table}' error: {e}")

if __name__ == "__main__":
    asyncio.run(check_tables())
