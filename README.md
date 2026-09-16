# VitalGate AI 🏥

VitalGate AI is a state-of-the-art Healthcare AI Assistant built with React, FastAPI, LangGraph, and Supabase. It uses a multi-agent AI architecture (powered by Google Gemini) to perform patient symptom intake, clinical research via pgvector RAG, and automated triage reporting. 

## Features
- **Multi-Agent AI Workflow**: Uses LangGraph to coordinate Intake, Research, Analysis, and Report agents.
- **RAG Medical Knowledge**: Embeds and searches a vector database of medical knowledge to ground AI decisions.
- **Secure Authentication & RBAC**: Supabase Auth securely segregates Patients, Doctors, and Admins.
- **Doctor Dashboard**: Doctors can view Active Triage queues, auto-generated Scribe SOAP notes, and manage their schedules.
- **End-to-End Monitoring**: Server-side agent tracing and structured error handling.

## 🚀 Installation & Setup

### Prerequisites
- Node.js (v18+)
- Python (v3.11+)
- Supabase Account
- Google Gemini API Key

### 1. Supabase Setup
1. Create a new Supabase project.
2. Go to the SQL Editor and run the queries inside `backend/supabase_schema.sql` to create tables, enable `pgvector`, and configure Row Level Security (RLS).
3. Obtain your Supabase Project URL and Anon Key.

### 2. Backend Setup
1. Open a terminal and navigate to the `backend/` directory:
   ```bash
   cd backend
   ```
2. Create a virtual environment and install dependencies:
   ```bash
   python -m venv venv
   # Windows: venv\Scripts\activate
   # Mac/Linux: source venv/bin/activate
   pip install -r requirements.txt
   ```
3. Create a `.env` file in the `backend/` folder and add your API keys:
   ```env
   SUPABASE_URL=your_supabase_url
   SUPABASE_KEY=your_supabase_anon_key
   GEMINI_API_KEY=your_google_gemini_key
   ```
4. Start the FastAPI server:
   ```bash
   uvicorn app.main:app --reload
   ```
   The backend will run on `http://localhost:8000`.

### 3. Frontend Setup
1. Open a new terminal and navigate to the `frontend/` directory:
   ```bash
   cd frontend
   ```
2. Install the Node dependencies:
   ```bash
   npm install
   ```
3. Create a `.env.local` file in the `frontend/` folder:
   ```env
   VITE_SUPABASE_URL=your_supabase_url
   VITE_SUPABASE_ANON_KEY=your_supabase_anon_key
   VITE_API_URL=http://localhost:8000
   ```
4. Start the React development server:
   ```bash
   npm run dev
   ```
   The frontend will run on `http://localhost:5173`.

## 🧪 Testing the Application
To verify the application works end-to-end:
1. **Authentication**: Register a new user as a Patient. Register another user as a Doctor.
2. **AI Workflow**: As a Patient, go to the Symptom Checker and describe a medical issue (e.g., "I have severe chest pain"). Verify the AI asks follow-up questions, determines urgency, and recommends a department.
3. **Doctor Verification**: Log in as the Doctor, navigate to "Active Triage", and verify the patient's report is generated with the AI Scribe SOAP note.

## License
This project is licensed under the [MIT License](LICENSE).
