import os
import requests
from dotenv import load_dotenv

load_dotenv('.env')

# Supabase Postgres REST API allows running SQL via RPC if defined, but we don't have one.
# So I'll modify the backend endpoints.py to also mirror the insert into `triage_reports` so the foreign key passes!
