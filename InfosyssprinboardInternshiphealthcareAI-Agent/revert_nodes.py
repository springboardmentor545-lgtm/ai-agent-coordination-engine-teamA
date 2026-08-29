import glob

nodes = glob.glob('backend/app/agents/nodes/*.py')
for f in nodes:
    with open(f, 'r') as file:
        content = file.read()
    
    # Switch LLM back to Groq
    if 'langchain_google_genai' in content:
        content = content.replace('from langchain_google_genai import ChatGoogleGenerativeAI', 'from langchain_groq import ChatGroq')
        content = content.replace('ChatGoogleGenerativeAI(model="gemini-flash-latest", google_api_key=settings.GEMINI_API_KEY)', 'ChatGroq(api_key=settings.GROQ_API_KEY, model_name="qwen/qwen3.6-27b")')
        content = content.replace('ChatGoogleGenerativeAI(model="gemini-flash-latest", google_api_key=settings.GEMINI_API_KEY, temperature=0.1)', 'ChatGroq(api_key=settings.GROQ_API_KEY, model_name="qwen/qwen3.6-27b", temperature=0.1)')
        content = content.replace('ChatGoogleGenerativeAI(model="gemini-flash-latest", google_api_key=settings.GEMINI_API_KEY, temperature=0.2)', 'ChatGroq(api_key=settings.GROQ_API_KEY, model_name="qwen/qwen3.6-27b", temperature=0.2)')
        content = content.replace('ChatGoogleGenerativeAI(model="gemini-flash-latest", google_api_key=settings.GEMINI_API_KEY, temperature=0.3)', 'ChatGroq(api_key=settings.GROQ_API_KEY, model_name="qwen/qwen3.6-27b", temperature=0.3)')
    
    with open(f, 'w') as file:
        file.write(content)
