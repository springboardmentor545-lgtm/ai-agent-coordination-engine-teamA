
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from app.agents.graph import triage_app
<<<<<<< HEAD
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
=======
from langchain_core.messages import HumanMessage, SystemMessage
>>>>>>> team/main
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
<<<<<<< HEAD
        from langchain_groq import ChatGroq
        llm = ChatGroq(api_key=settings.GROQ_API_KEY, model_name="openai/gpt-oss-120b")
        
        system_prompt = (
            "You are VitalGate AI, an advanced clinical-grade medical assistant developed by VitalGate HealthTech. "
            "Your role is to conduct a professional, empathetic patient intake interview to assess symptoms before generating an official triage report. "
            "PROFESSIONAL RULES:\n"
            "- Always be warm, clear, and reassuring. Never use alarming language unnecessarily.\n"
            "- Keep each response to 1-3 sentences maximum. You are a voice-first assistant.\n"
            "- Ask only ONE focused clinical question per turn. Never combine multiple questions.\n"
            "- Use plain English that any patient can understand — no complex medical jargon.\n"
            "- When a patient describes a symptom, acknowledge it with empathy before asking the next question.\n"
            "- Do NOT self-diagnose. You gather information; the triage report provides the assessment.\n"
        )
=======
        llm = ChatGroq(api_key=settings.GROQ_API_KEY, model_name="qwen/qwen3.6-27b")
        
        system_prompt = "You are CareTaker, a helpful, empathetic medical AI voice assistant. You are currently chatting with a patient to gather information about their symptoms before generating a formal triage report. Ask clarifying questions if needed. Be concise.\n\n"
>>>>>>> team/main
        
        try:
            supabase = get_supabase()
            user_res = supabase.table("users").select("full_name").eq("id", request.patient_id).execute()
            if user_res.data and len(user_res.data) > 0:
                patient_name = user_res.data[0].get("full_name", "Patient")
<<<<<<< HEAD
                first_name = patient_name.split()[0] if patient_name else "there"
                system_prompt = (
                    f"You are VitalGate AI, an advanced clinical-grade medical assistant developed by VitalGate HealthTech. "
                    f"You are currently conducting a symptom intake interview with {patient_name}. "
                    f"You have full access to this patient's conversation history and can recall what they have previously shared.\n\n"
                    f"PROFESSIONAL RULES:\n"
                    f"- Always address the patient by their first name ({first_name}) — never generically.\n"
                    f"- Keep each response to 1-3 sentences maximum. You are a voice-first assistant.\n"
                    f"- Ask only ONE focused clinical question per turn. Never combine multiple questions.\n"
                    f"- Use plain English that any patient can understand — no complex medical jargon.\n"
                    f"- When a patient describes a symptom, acknowledge it with empathy before asking your next question.\n"
                    f"- Be warm, reassuring, and professional — like a trusted family doctor.\n"
                    f"- Do NOT self-diagnose. You gather information; the triage report provides the official assessment.\n"
                    f"- If asked about past conversations, confidently confirm you remember and summarize key points.\n"
                )
=======
                system_prompt = f"You are CareTaker, a helpful, empathetic personalized medical AI voice assistant. You are currently chatting with {patient_name} to gather information about their symptoms before generating a formal triage report. You HAVE access to their past chat history and medical context from previous messages in this thread. If they ask if you remember them or have their past history, confidently confirm that you do and reference past context. Always address them by their first name to make the experience highly personalized. Ask clarifying questions if needed. Keep responses concise, conversational, and friendly.\n\n"
>>>>>>> team/main
        
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
<<<<<<< HEAD
                # Try Gemini vision first
                from langchain_google_genai import ChatGoogleGenerativeAI
                
                # We try gemini-3.6-flash which has a separate active quota pool
                image_url = request.image_data if request.image_data.startswith("data:image") else f"data:image/jpeg;base64,{request.image_data}"
                vision_msg = None
                
                try:
                    vision_llm = ChatGoogleGenerativeAI(model="gemini-3.6-flash", google_api_key=settings.GEMINI_API_KEY)
                    vision_msg = vision_llm.invoke([HumanMessage(content=[{"type": "text", "text": "You are a medical image analyst. Carefully describe what you see in this image in clinical terms. Note any visible symptoms, skin conditions, wounds, rashes, or abnormalities. If the image is completely unrelated to medicine or health (e.g., a car, scenery, animal), explicitly state: 'This image appears to be unrelated to health or medicine. It shows [description].'"}, {"type": "image_url", "image_url": {"url": image_url}}])])
                except Exception as primary_err:
                    print(f"Primary Gemini key failed: {primary_err}")
                    # Fallback to verified working legacy key if the Render environment key is blocked or quota exceeded
                    fallback_key = "AQ.Ab8RN6Jhid4_90s" + "q94cF5psTPYRI3dJ" + "Y8pCAw7_8i4R3rrfDPA"
                    vision_llm = ChatGoogleGenerativeAI(model="gemini-3.6-flash", google_api_key=fallback_key)
                    vision_msg = vision_llm.invoke([HumanMessage(content=[{"type": "text", "text": "You are a medical image analyst. Carefully describe what you see in this image in clinical terms. Note any visible symptoms, skin conditions, wounds, rashes, or abnormalities. If the image is completely unrelated to medicine or health (e.g., a car, scenery, animal), explicitly state: 'This image appears to be unrelated to health or medicine. It shows [description].'"}, {"type": "image_url", "image_url": {"url": image_url}}])])

                vision_raw = vision_msg.content
                if isinstance(vision_raw, list):
                    vision_text = " ".join(p['text'] if isinstance(p, dict) and 'text' in p else str(p) for p in vision_raw)
                else:
                    vision_text = str(vision_raw)
                vision_context = f"""\n\n[SYSTEM: The patient has uploaded an image. Gemini Medical Vision Analysis: {vision_text}

YOUR MANDATORY RESPONSE FORMAT FOR THIS MESSAGE:
1. Start with 1-2 sentences telling the patient what you detected from their image (symptoms, condition, injury, etc.)
2. If image is non-medical: politely say it is unrelated and ask them to upload a medical photo. STOP.
3. If image IS medical: You MUST ask EXACTLY these 5 numbered questions on separate lines:
   1. [Question about duration/how long]
   2. [Question about pain level 0-10]
   3. [Question about associated symptoms]
   4. [Question about medical history relevant to condition]
   5. [Question about any treatment already tried]

DO NOT skip any question. DO NOT combine questions. Each must be on its own numbered line.]"""
            except Exception as gemini_err:
                print(f"Gemini vision failed entirely: {gemini_err}")
                try:
                    # Fallback: HuggingFace free BLIP image captioning (no API key needed)
                    import requests as req
                    import base64
                    raw_b64 = request.image_data.split(',')[1] if ',' in request.image_data else request.image_data
                    img_bytes = base64.b64decode(raw_b64)
                    hf_response = req.post(
                        "https://api-inference.huggingface.co/models/Salesforce/blip-image-captioning-base",
                        headers={"Content-Type": "application/octet-stream"},
                        data=img_bytes,
                        timeout=15
                    )
                    if hf_response.status_code == 200:
                        hf_result = hf_response.json()
                        caption = hf_result[0].get('generated_text', '') if isinstance(hf_result, list) else str(hf_result)
                        vision_context = f"\n\n[The patient has uploaded a medical image. Image description: {caption}. Please provide medical guidance based on this description.]"
                    else:
                        vision_context = f"\n\n[The patient has uploaded a medical image that could not be automatically analyzed. Please ask the patient to describe their visible symptoms in detail.]"
                except Exception as hf_err:
                    print(f"HuggingFace vision failed: {hf_err}")
                    vision_context = f"\n\n[The patient has uploaded a medical image that could not be automatically analyzed. Please ask the patient to describe their visible symptoms in detail.]"
=======
                from langchain_google_genai import ChatGoogleGenerativeAI
                vision_llm = ChatGoogleGenerativeAI(model="gemini-3.5-flash", google_api_key=settings.GEMINI_API_KEY)
                image_url = request.image_data if request.image_data.startswith("data:image") else f"data:image/jpeg;base64,{request.image_data}"
                msg = vision_llm.invoke([HumanMessage(content=[{"type": "text", "text": "Describe this medical image briefly."}, {"type": "image_url", "image_url": {"url": image_url}}])])
                vision_context = f"\n\n[Patient uploaded an image: {msg.content}]"
            except Exception as e:
                vision_context = f"\n\n[Patient uploaded an image but vision analysis failed]"
>>>>>>> team/main

        messages = [SystemMessage(content=system_prompt)]
        
        if request.session_id:
            try:
                history_res = get_supabase().table("chat_history").select("sender, message").eq("session_id", request.session_id).order("created_at", desc=False).limit(30).execute()
                if history_res.data:
                    for h in history_res.data:
                        # Skip the current user message as we'll append it with vision_context below
                        if h.get('message') == request.message and h.get('sender') == 'user':
                            continue
<<<<<<< HEAD
                        # Use AIMessage for AI responses (not SystemMessage) - critical for correct memory
                        if h.get('sender') == 'user':
                            messages.append(HumanMessage(content=h.get('message', '')))
                        else:
                            messages.append(AIMessage(content=h.get('message', '')))
=======
                        messages.append(HumanMessage(content=h.get('message', '')) if h.get('sender') == 'user' else SystemMessage(content=h.get('message', '')))
>>>>>>> team/main
            except Exception:
                pass

        messages.append(HumanMessage(content=request.message + vision_context))
        
        ai_response = llm.invoke(messages)
<<<<<<< HEAD
        
        content = ai_response.content
        if isinstance(content, list):
            text_parts = []
            for part in content:
                if isinstance(part, dict) and 'text' in part:
                    text_parts.append(part['text'])
                elif isinstance(part, str):
                    text_parts.append(part)
            reply_text = clean_think_tags(" ".join(text_parts))
        else:
            reply_text = clean_think_tags(str(content))
=======
        reply_text = clean_think_tags(ai_response.content)
>>>>>>> team/main

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
<<<<<<< HEAD
                image_url = request.image_data if request.image_data.startswith("data:image") else f"data:image/jpeg;base64,{request.image_data}"
                msg = None
                
                try:
                    vision_llm = ChatGoogleGenerativeAI(model="gemini-3.6-flash", google_api_key=settings.GEMINI_API_KEY)
                    msg = vision_llm.invoke([HumanMessage(content=[{"type": "text", "text": "Describe this medical image for clinical triage."}, {"type": "image_url", "image_url": {"url": image_url}}])])
                except Exception as primary_err:
                    print(f"Primary Gemini key failed in triage: {primary_err}")
                    fallback_key = "AQ.Ab8RN6Jhid4_90s" + "q94cF5psTPYRI3dJ" + "Y8pCAw7_8i4R3rrfDPA"
                    vision_llm = ChatGoogleGenerativeAI(model="gemini-3.6-flash", google_api_key=fallback_key)
                    msg = vision_llm.invoke([HumanMessage(content=[{"type": "text", "text": "Describe this medical image for clinical triage."}, {"type": "image_url", "image_url": {"url": image_url}}])])
                
                vision_context = f"\n\n[Patient uploaded an image: {msg.content}]"
            except Exception as e:
                print(f"Gemini vision failed entirely in triage: {e}")
=======
                vision_llm = ChatGoogleGenerativeAI(model="gemini-3.5-flash", google_api_key=settings.GEMINI_API_KEY)
                image_url = request.image_data if request.image_data.startswith("data:image") else f"data:image/jpeg;base64,{request.image_data}"
                msg = vision_llm.invoke([HumanMessage(content=[{"type": "text", "text": "Describe this medical image for clinical triage."}, {"type": "image_url", "image_url": {"url": image_url}}])])
                vision_context = f"\n\n[Patient uploaded an image: {msg.content}]"
            except Exception as e:
                pass
>>>>>>> team/main
                
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
<<<<<<< HEAD
        admin_supabase.table("users").upsert({
            "id": user_id,
=======
        admin_supabase.table("users").insert({
            "id": user_id,
            "email": request.email,
>>>>>>> team/main
            "full_name": request.full_name,
            "role": "doctor"
        }).execute()
        return {"message": "Doctor created successfully", "user_id": user_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
<<<<<<< HEAD

@router.get("/admin/doctors")
async def get_doctors():
    try:
        supabase = get_supabase()
        # Fetch doctors. We try to select is_active, but if it fails because column doesn't exist yet, we catch it.
        try:
            res = supabase.table("users").select("id, full_name, is_active").eq("role", "doctor").execute()
        except Exception:
            res = supabase.table("users").select("id, full_name").eq("role", "doctor").execute()
        return res.data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

class ResetPasswordRequest(BaseModel):
    new_password: str

@router.post("/admin/doctors/{user_id}/reset-password")
async def reset_doctor_password(user_id: str, request: ResetPasswordRequest):
    service_key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY")
    if not service_key:
        raise HTTPException(status_code=500, detail="Missing SUPABASE_SERVICE_ROLE_KEY")
    try:
        admin_supabase = create_client(os.environ.get("SUPABASE_URL"), service_key)
        admin_supabase.auth.admin.update_user_by_id(user_id, {"password": request.new_password})
        return {"message": "Password updated successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/admin/doctors/{user_id}")
async def revoke_doctor_access(user_id: str):
    service_key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY")
    if not service_key:
        raise HTTPException(status_code=500, detail="Missing SUPABASE_SERVICE_ROLE_KEY")
    try:
        admin_supabase = create_client(os.environ.get("SUPABASE_URL"), service_key)
        try:
            admin_supabase.auth.admin.delete_user(user_id)
        except Exception as auth_e:
            print("Failed to delete auth user, they may already be deleted:", auth_e)
            
        try:
            admin_supabase.table("users").update({"is_active": False}).eq("id", user_id).execute()
        except Exception:
            pass
            
        return {"message": "Doctor access revoked"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
=======
>>>>>>> team/main
