import os
import json
from langchain_groq import ChatGroq
from pydantic import BaseModel, Field

with open('.env') as f:
    for line in f:
        if line.startswith('GROQ_API_KEY='):
            api_key = line.strip().split('=')[1]

class DecisionSchema(BaseModel):
    urgency_level: str = Field(description="The assigned urgency level. Must be one of: 'Low', 'Medium', 'High', 'Critical'.")
    recommended_department: str = Field(description="The recommended medical department for the patient (e.g., 'Cardiology', 'General Practice', 'Emergency').")

models = ['openai/gpt-oss-120b', 'qwen/qwen3.8-27b', 'groq/compound', 'qwen/qwen3.6-27b']

for model in models:
    try:
        llm = ChatGroq(api_key=api_key, model_name=model, temperature=0.1)
        structured_llm = llm.with_structured_output(DecisionSchema)
        res = structured_llm.invoke('Patient has a severe headache and blurry vision.')
        print(f'SUCCESS structured output: {model} -> {res}')
    except Exception as e:
        print(f'FAILED structured output: {model} - {str(e)}')
