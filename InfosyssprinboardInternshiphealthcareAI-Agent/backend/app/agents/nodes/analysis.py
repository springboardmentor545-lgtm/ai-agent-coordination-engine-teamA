from langchain_groq import ChatGroq
from app.agents.state import AgentState
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from app.core.config import settings
from langchain_core.output_parsers import StrOutputParser

def analysis_node(state: AgentState) -> dict:
    """
    Analysis Agent: Evaluates the symptoms against the retrieved medical knowledge.
    Uses ChatGroq to produce clinical reasoning.
    """
    symptoms = state.get("symptoms", "")
    duration = state.get("duration", "unknown")
    severity = state.get("severity", "unknown")
    context = state.get("medical_knowledge_context", "")
    
    try:
        # Initialize LLM
        from langchain_groq import ChatGroq
        llm = ChatGroq(api_key=settings.GROQ_API_KEY, model_name="qwen/qwen3.6-27b", temperature=0.2)
        
        # Define Prompt
        prompt = ChatPromptTemplate.from_messages([
            ("system", "You are an expert AI clinical analyst. Your job is to analyze the patient's symptoms based ONLY on the provided medical knowledge context. Provide a concise, clear clinical reasoning paragraph explaining potential risks and evaluating the situation. Do NOT invent medical facts outside the context. If the context is empty, state that general evaluation is needed."),
            ("human", "Symptoms: {symptoms}\\nDuration: {duration}\\nSeverity: {severity}\\n\\nMedical Knowledge Context:\\n{context}")
        ])
        
        # Create chain
        chain = prompt | llm | StrOutputParser()
        
        # Invoke
        reasoning = chain.invoke({
            "symptoms": symptoms,
            "duration": duration,
            "severity": severity,
            "context": context
        })
        import re
        reasoning = re.sub(r'<think>.*?</think>', '', reasoning, flags=re.DOTALL).strip()
        
    except Exception as e:
        print(f"Analysis node error: {str(e)}")
        raise RuntimeError(f"Failed to generate clinical reasoning: {str(e)}")
            
    return {
        "analysis_reasoning": reasoning
    }
