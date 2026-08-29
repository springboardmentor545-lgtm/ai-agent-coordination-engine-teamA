import glob
import os

files = glob.glob('backend/app/**/*.py', recursive=True)

for f in files:
    with open(f, 'r', encoding='utf-8') as file:
        content = file.read()
    
    if 'ChatGroq' in content:
        content = content.replace('from langchain_groq import ChatGroq', 'from langchain_google_genai import ChatGoogleGenerativeAI')
        content = content.replace('ChatGroq(api_key=settings.GROQ_API_KEY, model_name="mixtral-8x7b-32768")', 'ChatGoogleGenerativeAI(model="gemini-1.5-flash", google_api_key=settings.GEMINI_API_KEY)')
        content = content.replace('ChatGroq(api_key=settings.GROQ_API_KEY, model_name="llama-3.1-70b-versatile")', 'ChatGoogleGenerativeAI(model="gemini-1.5-flash", google_api_key=settings.GEMINI_API_KEY)')
        
        with open(f, 'w', encoding='utf-8') as file:
            file.write(content)
        print(f"Updated {f}")
