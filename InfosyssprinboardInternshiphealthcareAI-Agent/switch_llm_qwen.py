import glob
import os

files = glob.glob('backend/app/**/*.py', recursive=True)

for f in files:
    with open(f, 'r', encoding='utf-8') as file:
        content = file.read()
    
    if 'ChatGoogleGenerativeAI' in content and 'gemini-1.5-flash' in content:
        content = content.replace('from langchain_google_genai import ChatGoogleGenerativeAI', 'from langchain_groq import ChatGroq')
        content = content.replace('ChatGoogleGenerativeAI(model="gemini-1.5-flash", google_api_key=settings.GEMINI_API_KEY)', 'ChatGroq(api_key=settings.GROQ_API_KEY, model_name="qwen/qwen3.6-27b")')
        
        with open(f, 'w', encoding='utf-8') as file:
            file.write(content)
        print(f"Updated {f}")
