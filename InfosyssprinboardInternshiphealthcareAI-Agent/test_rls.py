import os, asyncio
from dotenv import load_dotenv
from supabase import create_client
import json

load_dotenv('.env')
sb = create_client(os.environ['SUPABASE_URL'], os.environ['SUPABASE_KEY'])

try:
    sb.auth.sign_in_with_password({'email': 'vikram23@gmail.com', 'password': '123456'})
    user = sb.auth.get_user().user
    res = sb.table('appointments').insert({
        'patient_id': user.id,
        'doctor_id': '555edd04-6cb3-4769-9e7a-6bce568c9320',
        'department': 'Test',
        'appointment_time': 'test',
        'status': 'scheduled'
    }).execute()
    print('Patient Insert Success:', res.data)
except Exception as e:
    print('Patient Insert Failed:', getattr(e, 'message', str(e)))

try:
    sb.auth.sign_in_with_password({'email': 'abi23@gmail.com', 'password': '123456'})
    user = sb.auth.get_user().user
    res = sb.table('appointments').insert({
        'patient_id': user.id,
        'doctor_id': user.id,
        'department': 'Locked Block',
        'appointment_time': 'test',
        'status': 'scheduled'
    }).execute()
    print('Doctor Insert Success:', res.data)
except Exception as e:
    print('Doctor Insert Failed:', getattr(e, 'message', str(e)))
