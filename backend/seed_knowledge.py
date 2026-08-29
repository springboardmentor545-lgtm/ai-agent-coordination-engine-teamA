import asyncio
import os
from sentence_transformers import SentenceTransformer
from app.db import get_supabase
from dotenv import load_dotenv

load_dotenv()

async def seed_db():
    print("Loading ML Model (this may take a minute if downloading for the first time)...")
    model = SentenceTransformer('all-mpnet-base-v2')
    supabase = get_supabase()

    knowledge_base = [
        {
            "symptom": "Severe chest pain, shortness of breath, radiating pain to left arm",
            "condition": "Myocardial Infarction (Heart Attack)",
            "department": "Emergency Room",
            "urgency": "High"
        },
        {
            "symptom": "Persistent headache, mild nausea, sensitivity to light",
            "condition": "Migraine",
            "department": "General Practice",
            "urgency": "Medium"
        },
        {
            "symptom": "Itchy red rash on forearm, mild swelling after being outdoors",
            "condition": "Contact Dermatitis",
            "department": "Dermatology",
            "urgency": "Low"
        },
        {
            "symptom": "High fever, severe body aches, dry cough, fatigue",
            "condition": "Influenza (Flu)",
            "department": "General Practice",
            "urgency": "Medium"
        },
        {
            "symptom": "Sudden numbness on one side of face, difficulty speaking, confusion",
            "condition": "Stroke",
            "department": "Emergency Room",
            "urgency": "High"
        }
    ]

    print("Generating embeddings and saving to Supabase...")
    for item in knowledge_base:
        # Generate embedding vector
        embedding = model.encode(item["symptom"]).tolist()
        
        # Insert into DB
        try:
            supabase.table("medical_knowledge").insert({
                "symptom": item["symptom"],
                "condition": item["condition"],
                "department": item["department"],
                "urgency": item["urgency"],
                "embedding": embedding
            }).execute()
            print(f"Saved: {item['condition']}")
        except Exception as e:
            print(f"Failed to save {item['condition']}: {e}")

if __name__ == "__main__":
    asyncio.run(seed_db())
