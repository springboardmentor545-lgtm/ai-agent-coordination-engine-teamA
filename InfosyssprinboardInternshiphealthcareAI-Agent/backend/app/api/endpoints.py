
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from app.agents.graph import triage_app
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_groq import ChatGroq
from app.core.config import settings
from app.db import get_supabase
import re
import os
from supabase import create_client

router = APIRouter()

class SymptomRequest(BaseModel):
    patient_id: str
    message: str
    image_data: str | None = None

class TriageResponse(BaseModel):
    urgency_level: str
    recommended_department: str
    suspected_condition: str
    ai_explanation: str
    appointment_id: str
    triage_id: str | None = None

class ChatRequest(BaseModel):
    patient_id: str
    message: str
    image_data: str | None = None
    session_id: str | None = None

class SessionCreateRequest(BaseModel):
    patient_id: str
    title: str

class ChatResponse(BaseModel):
    reply: str

def clean_think_tags(text: str) -> str:
    return re.sub(r'<think>.*?</think>', '', text, flags=re.DOTALL).strip()

@router.post("/sessions")
async def create_session(request: SessionCreateRequest):
    try:
        supabase = get_supabase()
        res = supabase.table("chat_sessions").insert({
            "patient_id": request.patient_id,
            "title": request.title
        }).execute()
        return res.data[0]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/sessions/{patient_id}")
async def get_sessions(patient_id: str):
    try:
        supabase = get_supabase()
        res = supabase.table("chat_sessions").select("*").eq("patient_id", patient_id).order("created_at", desc=True).execute()
        return res.data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/sessions/{session_id}")
async def delete_session(session_id: str):
    try:
        supabase = get_supabase()
        supabase.table("chat_sessions").delete().eq("id", session_id).execute()
        return {"message": "Session deleted"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/sessions/{session_id}/messages")
async def get_session_messages(session_id: str):
    try:
        supabase = get_supabase()
        res = supabase.table("chat_history").select("*").eq("session_id", session_id).order("created_at", desc=False).execute()
        return res.data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/chat", response_model=ChatResponse)
async def chat_interaction(request: ChatRequest):
    try:
        llm = ChatGroq(api_key=settings.GROQ_API_KEY, model_name="qwen/qwen3.6-27b")
        
        system_prompt = "You are CareTaker, a helpful, empathetic medical AI voice assistant. You are currently chatting with a patient to gather information about their symptoms before generating a formal triage report. Ask clarifying questions if needed. Be concise.\n\n"
        
        try:
            supabase = get_supabase()
            user_res = supabase.table("users").select("full_name").eq("id", request.patient_id).execute()
            if user_res.data and len(user_res.data) > 0:
                patient_name = user_res.data[0].get("full_name", "Patient")
                system_prompt = f"You are CareTaker, a helpful, empathetic personalized medical AI voice assistant. You are currently chatting with {patient_name} to gather information about their symptoms before generating a formal triage report. You HAVE access to their past chat history and medical context from previous messages in this thread. If they ask if you remember them or have their past history, confidently confirm that you do and reference past context. Always address them by their first name to make the experience highly personalized. Ask clarifying questions if needed. Keep responses concise, conversational, and friendly.\n\n"
        
            if request.message:
                data_to_insert = {
                    "patient_id": request.patient_id,
                    "sender": "user",
                    "message": request.message
                }
                if request.session_id:
                    data_to_insert["session_id"] = request.session_id
                supabase.table("chat_history").insert(data_to_insert).execute()
        except Exception as e:
            pass

        vision_context = ""
        if request.image_data:
            try:
                from langchain_google_genai import ChatGoogleGenerativeAI
                vision_llm = ChatGoogleGenerativeAI(model="gemini-3.5-flash", google_api_key=settings.GEMINI_API_KEY)
                image_url = request.image_data if request.image_data.startswith("data:image") else f"data:image/jpeg;base64,{request.image_data}"
                msg = vision_llm.invoke([HumanMessage(content=[{"type": "text", "text": "Describe this medical image briefly."}, {"type": "image_url", "image_url": {"url": image_url}}])])
                vision_context = f"\n\n[Patient uploaded an image: {msg.content}]"
            except Exception as e:
                vision_context = f"\n\n[Patient uploaded an image but vision analysis failed]"

        messages = [SystemMessage(content=system_prompt)]
        
        if request.session_id:
            try:
                history_res = get_supabase().table("chat_history").select("sender, message").eq("session_id", request.session_id).order("created_at", desc=False).limit(30).execute()
                if history_res.data:
                    for h in history_res.data:
                        # Skip the current user message as we'll append it with vision_context below
                        if h.get('message') == request.message and h.get('sender') == 'user':
                            continue
                        messages.append(HumanMessage(content=h.get('message', '')) if h.get('sender') == 'user' else SystemMessage(content=h.get('message', '')))
            except Exception:
                pass

        messages.append(HumanMessage(content=request.message + vision_context))
        
        ai_response = llm.invoke(messages)
        reply_text = clean_think_tags(ai_response.content)

        try:
            supabase = get_supabase()
            data_to_insert = {
                "patient_id": request.patient_id,
                "sender": "ai",
                "message": reply_text
            }
            if request.session_id:
                data_to_insert["session_id"] = request.session_id
            supabase.table("chat_history").insert(data_to_insert).execute()
        except Exception:
            pass

        return ChatResponse(reply=reply_text)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/triage", response_model=TriageResponse)
async def process_symptoms(request: SymptomRequest):
    try:
        # Pre-process image to text using Gemini so the downstream Groq graph doesn't need to handle vision
        vision_context = ""
        if request.image_data:
            try:
                from langchain_google_genai import ChatGoogleGenerativeAI
                vision_llm = ChatGoogleGenerativeAI(model="gemini-3.5-flash", google_api_key=settings.GEMINI_API_KEY)
                image_url = request.image_data if request.image_data.startswith("data:image") else f"data:image/jpeg;base64,{request.image_data}"
                msg = vision_llm.invoke([HumanMessage(content=[{"type": "text", "text": "Describe this medical image for clinical triage."}, {"type": "image_url", "image_url": {"url": image_url}}])])
                vision_context = f"\n\n[Patient uploaded an image: {msg.content}]"
            except Exception as e:
                pass
                
        initial_state = {
            "messages": [HumanMessage(content=request.message + vision_context)],
            "patient_id": request.patient_id,
            "image_data": None # Consumed
        }
        
        result = triage_app.invoke(initial_state)
        
        triage_id = None
        try:
            supabase = get_supabase()
            insert_result = supabase.table("triages").insert({
                "patient_id": request.patient_id,
                "symptoms": result.get("symptoms", request.message),
                "analysis": result.get("final_summary", ""),
                "urgency": result.get("urgency_level", "Unknown"),
                "department": result.get("recommended_department", "Unknown"),
                "image_data": request.image_data,
                "status": "pending"
            }).execute()
            if insert_result.data and len(insert_result.data) > 0:
                triage_id = insert_result.data[0]["id"]
                try:
                    supabase.table("triage_reports").insert({
                        "id": triage_id,
                        "patient_id": request.patient_id,
                        "symptoms": result.get("symptoms", request.message),
                        "urgency_level": result.get("urgency_level", "Unknown") if result.get("urgency_level") in ["Low", "Medium", "High"] else "Low",
                        "recommended_department": result.get("recommended_department", "Unknown"),
                        "ai_explanation": result.get("final_summary", "")
                    }).execute()
                except Exception as mirror_err:
                    print("Mirror to triage_reports failed:", mirror_err)
        except Exception as db_err:
            print(f"Failed to save triage to DB: {db_err}")

        return TriageResponse(
            urgency_level=result.get("urgency_level", "Unknown"),
            recommended_department=result.get("recommended_department", "Unknown"),
            suspected_condition=result.get("suspected_condition", "Pending Evaluation"),
            ai_explanation=result.get("final_summary", ""),
            appointment_id=result.get("appointment_id", ""),
            triage_id=triage_id or ""
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

class CreateDoctorRequest(BaseModel):
    email: str
    password: str
    full_name: str

@router.post("/admin/create-doctor")
async def create_doctor(request: CreateDoctorRequest):
    service_key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY")
    if not service_key:
        raise HTTPException(status_code=500, detail="Missing SUPABASE_SERVICE_ROLE_KEY")
    try:
        admin_supabase = create_client(os.environ.get("SUPABASE_URL"), service_key)
        auth_res = admin_supabase.auth.admin.create_user({
            "email": request.email,
            "password": request.password,
            "email_confirm": True
        })
        user_id = auth_res.user.id
        admin_supabase.table("users").insert({
            "id": user_id,
            "email": request.email,
            "full_name": request.full_name,
            "role": "doctor"
        }).execute()
        return {"message": "Doctor created successfully", "user_id": user_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
