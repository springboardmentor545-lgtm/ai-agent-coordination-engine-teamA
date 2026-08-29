import os
import asyncio
from dotenv import load_dotenv
from supabase import create_client, Client

load_dotenv()

url: str = os.environ.get("SUPABASE_URL")
key: str = os.environ.get("SUPABASE_KEY")
supabase: Client = create_client(url, key)

users_to_create = [
    {"email": "vicky23@gmail.com", "password": "123456", "role": "patient", "name": "Vicky (Patient)"},
    {"email": "pooja24@gmail.com", "password": "123456", "role": "doctor", "name": "Dr. Pooja"},
    {"email": "admin23@gmail.com", "password": "123456", "role": "admin", "name": "System Admin"}
]

async def seed_users():
    for u in users_to_create:
        print(f"Creating user {u['email']}...")
        
        # 1. Sign up user
        try:
            res = supabase.auth.sign_up({
                "email": u["email"],
                "password": u["password"],
            })
            print(f"Auth creation result: {res}")
            
            user_id = res.user.id if res.user else None
            if not user_id:
                print(f"Failed to get user ID for {u['email']}")
                continue
            
            # 2. Insert into public.users
            try:
                profile_res = supabase.table("users").upsert({
                    "id": user_id,
                    "full_name": u["name"],
                    "role": u["role"]
                }).execute()
                print(f"Profile creation result: {profile_res}")
            except Exception as e:
                print(f"Failed to insert into public.users for {u['email']}: {e}")
                
        except Exception as e:
            print(f"Failed to sign up {u['email']}: {e}")

if __name__ == "__main__":
    asyncio.run(seed_users())
