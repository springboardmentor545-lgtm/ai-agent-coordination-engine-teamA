import os, asyncio
from dotenv import load_dotenv
from supabase import create_client
import json

load_dotenv('.env')
sb = create_client(os.environ['SUPABASE_URL'], os.environ['SUPABASE_KEY'])

try:
    sb.auth.sign_in_with_password({'email': 'abi23@gmail.com', 'password': '123456'})
    user = sb.auth.get_user().user
    res = sb.table('appointments').select('*, users!appointments_patient_id_fkey(full_name)').execute()
    print('Query Result:', res.data)
except Exception as e:
    print('Query Error:', getattr(e, 'message', str(e)))
