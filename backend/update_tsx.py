import os

tsx_content = """import React, { useState, useEffect } from 'react';
import { Bot, MoreVertical, Paperclip, Send, X, Mic, MicOff, Volume2, VolumeX, MessageSquare, Plus, Menu } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import { supabase } from '../lib/supabase';

type Message = {
  id: string;
  sender: 'user' | 'ai';
  text: string;
};

type ChatSession = {
  id: string;
  title: string;
  created_at: string;
};

const AGENT_STEPS = ['Intake', 'Research', 'Analysis', 'Triage', 'Report'];

export default function SymptomChecker() {
  const [input, setInput] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const [isTriaging, setIsTriaging] = useState(false);
  const [patientId, setPatientId] = useState<string | null>(null);
  const [currentStep, setCurrentStep] = useState(-1);
  const [attachedImage, setAttachedImage] = useState<{file: File, base64: string} | null>(null);
  const fileInputRef = React.useRef<HTMLInputElement>(null);
  const navigate = useNavigate();
  
  // Chat Sessions States
  const [sessions, setSessions] = useState<ChatSession[]>([]);
  const [currentSessionId, setCurrentSessionId] = useState<string | null>(null);
  const [isSidebarOpen, setIsSidebarOpen] = useState(false);
  
  // Voice Assistant States
  const [isListening, setIsListening] = useState(false);
  const [isSpeakingEnabled, setIsSpeakingEnabled] = useState(true);
  const [recognition, setRecognition] = useState<any>(null);
  const [wasLastInputVoice, setWasLastInputVoice] = useState(false);
  
  useEffect(() => {
    supabase.auth.getUser().then(({ data: { user } }) => {
      if (user) setPatientId(user.id);
    });
  }, []);

  // Simulate agent pipeline progress
  useEffect(() => {
    let interval: ReturnType<typeof setInterval>;
    if (isTriaging) {
      setCurrentStep(0);
      interval = setInterval(() => {
        setCurrentStep(prev => (prev < 4 ? prev + 1 : prev));
      }, 700);
    } else {
      setCurrentStep(-1);
    }
    return () => clearInterval(interval);
  }, [isTriaging]);

  // Initialize Speech Recognition
  useEffect(() => {
    const SpeechRecognitionAPI = (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition;
    if (SpeechRecognitionAPI) {
      const recog = new SpeechRecognitionAPI();
      recog.continuous = true;
      recog.interimResults = false;
      
      recog.onresult = (event: any) => {
        let finalTranscript = '';
        for (let i = event.resultIndex; i < event.results.length; ++i) {
          if (event.results[i].isFinal) {
            finalTranscript += event.results[i][0].transcript;
          }
        }
        if (finalTranscript) {
          setInput(prev => prev + (prev ? ' ' : '') + finalTranscript.trim());
          setWasLastInputVoice(true);
        }
      };
      recog.onend = () => setIsListening(false);
      setRecognition(recog);
    }
  }, []);

  const toggleListening = () => {
    if (isListening) {
      recognition?.stop();
      setIsListening(false);
    } else {
      try {
        recognition?.start();
        setIsListening(true);
      } catch(e) {
        console.error("Speech recognition error:", e);
      }
    }
  };
  
  const initialMessage = {
    id: '1',
    sender: 'ai' as const,
    text: "Hello. I am the CareTaker AI Health Assistant. I'm here to help you assess your symptoms. Please note that I am an AI and this is not a substitute for professional medical advice in an emergency.\\n\\nTo get started, could you briefly describe what's bothering you today?"
  };

  const [messages, setMessages] = useState<Message[]>([initialMessage]);

  useEffect(() => {
    if (!patientId) return;
    const fetchSessions = async () => {
      const apiUrl = import.meta.env.VITE_API_URL || 'http://localhost:8000';
      try {
        const res = await fetch(`${apiUrl}/api/v1/sessions/${patientId}`);
        if (res.ok) {
          const data = await res.json();
          setSessions(data);
        }
      } catch (e) {
        console.error("Failed to fetch sessions", e);
      }
    };
    fetchSessions();
  }, [patientId]);

  const loadSession = async (sessionId: string) => {
    setCurrentSessionId(sessionId);
    setIsSidebarOpen(false);
    const apiUrl = import.meta.env.VITE_API_URL || 'http://localhost:8000';
    try {
      const res = await fetch(`${apiUrl}/api/v1/sessions/${sessionId}/messages`);
      if (res.ok) {
        const data = await res.json();
        if (data && data.length > 0) {
          setMessages(data.map((msg: any) => ({
            id: msg.id,
            sender: msg.sender,
            text: msg.message
          })));
        } else {
          setMessages([initialMessage]);
        }
      }
    } catch (e) {
      console.error("Failed to load session messages", e);
    }
  };

  const startNewChat = () => {
    setCurrentSessionId(null);
    setMessages([initialMessage]);
    setIsSidebarOpen(false);
  };

  // AI Speech Synthesis
  useEffect(() => {
    // Only speak new messages, not the initial predefined message
    if (messages.length > 1) {
      const lastMessage = messages[messages.length - 1];
      if (lastMessage && lastMessage.sender === 'ai' && isSpeakingEnabled && wasLastInputVoice) {
        // Cancel any ongoing speech
        window.speechSynthesis.cancel();
        const utterance = new SpeechSynthesisUtterance(lastMessage.text);
        window.speechSynthesis.speak(utterance);
      }
    }
  }, [messages, isSpeakingEnabled]);

  const handleSend = async () => {
    if (!input.trim() && !attachedImage) return;

    const userMessage = input.trim() || "Please analyze this image.";
    setInput('');
    
    let imageBase64 = attachedImage?.base64 || null;
    let messageText = userMessage;
    
    if (imageBase64) {
      setMessages(prev => [...prev, { id: Date.now().toString(), sender: 'user', text: `[Image Attached] ${userMessage}` }]);
    } else {
      setMessages(prev => [...prev, { id: Date.now().toString(), sender: 'user', text: userMessage }]);
    }
    
    setAttachedImage(null);
    setIsTyping(true);

    try {
      const apiUrl = import.meta.env.VITE_API_URL || 'http://localhost:8000';
      let sessionIdToUse = currentSessionId;
      
      // If no session exists, create one!
      if (!sessionIdToUse) {
         try {
           const titleRes = await fetch(`${apiUrl}/api/v1/sessions`, {
             method: 'POST',
             headers: { 'Content-Type': 'application/json' },
             body: JSON.stringify({ patient_id: patientId || "demo-user-123", title: userMessage.substring(0, 30) + "..." })
           });
           if (titleRes.ok) {
              const newSession = await titleRes.json();
              sessionIdToUse = newSession.id;
              setCurrentSessionId(sessionIdToUse);
              setSessions(prev => [newSession, ...prev]);
           }
         } catch (e) {
           console.error("Failed to create session", e);
         }
      }

      const response = await fetch(`${apiUrl}/api/v1/chat`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          patient_id: patientId || "demo-user-123",
          message: messageText,
          image_data: imageBase64,
          session_id: sessionIdToUse
        })
      });

      if (!response.ok) throw new Error('Network response was not ok');

      const data = await response.json();
      setMessages(prev => [...prev, { id: Date.now().toString(), sender: 'ai', text: data.reply }]);
    } catch (error) {
      console.error('Error hitting chat backend:', error);
      setMessages(prev => [...prev, { 
        id: Date.now().toString(), 
        sender: 'ai', 
        text: "I'm having trouble connecting right now, but I have noted your symptoms. You can click 'Generate Triage Report' when you are ready."
      }]);
    } finally {
      setIsTyping(false);
    }
  };

  const handleGenerateTriage = async () => {
    setIsTriaging(true);
    
    // Combine all messages as the context for the triage agent
    const allMessages = messages.map(m => `${m.sender.toUpperCase()}: ${m.text}`).join('\\n\\n');

    try {
      const apiUrl = import.meta.env.VITE_API_URL || 'http://localhost:8000';
      const response = await fetch(`${apiUrl}/api/v1/triage`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          patient_id: patientId || "demo-user-123",
          message: allMessages,
          image_data: null // We skip passing image again since the chat history summarizes it
        })
      });

      if (!response.ok) throw new Error('Network error');

      const data = await response.json();
      setTimeout(() => navigate('/result', { state: { triageData: data } }), 3000);

    } catch (error) {
      setTimeout(() => navigate('/result', { 
        state: { 
          triageData: {
            urgency_level: "Medium",
            recommended_department: "General Practice",
            ai_explanation: "This is a fallback demo explanation because the backend API is currently offline."
          } 
        } 
      }), 3000);
    }
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    const reader = new FileReader();
    reader.onload = (event) => {
      const result = event.target?.result as string;
      const base64 = result.split(',')[1];
      setAttachedImage({ file, base64 });
    };
    reader.readAsDataURL(file);
  };

  return (
    <div className="flex-grow flex w-full relative h-[calc(100vh-73px)] overflow-hidden bg-slate-50">
      
      {/* Sidebar for Chat Sessions */}
      <div className={`absolute md:static top-0 left-0 h-full bg-slate-900 text-slate-300 w-64 flex flex-col transition-transform duration-300 z-50 ${isSidebarOpen ? 'translate-x-0' : '-translate-x-full md:translate-x-0'} flex-shrink-0`}>
        <div className="p-4 border-b border-slate-700 flex items-center justify-between">
          <h2 className="font-semibold text-white">Chat History</h2>
          <button onClick={() => setIsSidebarOpen(false)} className="md:hidden text-slate-400 hover:text-white p-1">
            <X className="w-5 h-5" />
          </button>
        </div>
        
        <div className="p-3">
          <button 
            onClick={startNewChat}
            className="w-full flex items-center gap-2 p-3 bg-slate-800 hover:bg-slate-700 text-white rounded-lg transition-colors border border-slate-700"
          >
            <Plus className="w-4 h-4" />
            <span className="text-sm font-medium">New Chat</span>
          </button>
        </div>
        
        <div className="flex-1 overflow-y-auto p-3 flex flex-col gap-1 custom-scrollbar">
          {sessions.map((session) => (
            <button 
              key={session.id}
              onClick={() => loadSession(session.id)}
              className={`flex items-center gap-2.5 p-2.5 rounded-lg text-sm text-left transition-colors ${currentSessionId === session.id ? 'bg-blue-600/20 text-blue-400' : 'hover:bg-slate-800 text-slate-300 hover:text-slate-100'}`}
            >
              <MessageSquare className="w-4 h-4 flex-shrink-0" />
              <span className="truncate">{session.title}</span>
            </button>
          ))}
          {sessions.length === 0 && (
            <div className="text-sm text-slate-500 p-4 text-center">
              No previous chats found.
            </div>
          )}
        </div>
      </div>
      
      {/* Overlay for mobile sidebar */}
      {isSidebarOpen && (
        <div 
          className="md:hidden fixed inset-0 bg-slate-900/50 z-40"
          onClick={() => setIsSidebarOpen(false)}
        />
      )}

      {/* Main Chat Area */}
      <div className="flex-1 flex flex-col max-w-4xl mx-auto w-full relative pt-4 pb-4 px-4 md:px-6 h-full">
        {/* Chat Header with Progress Strip */}
        <div className="bg-white rounded-t-2xl p-4 flex flex-col gap-4 shadow-sm border border-slate-200 border-b-slate-100 z-10">
          <div className="flex items-center gap-3">
            <button 
              onClick={() => setIsSidebarOpen(true)}
              className="md:hidden text-slate-500 hover:text-blue-600 transition-colors p-2 rounded-lg hover:bg-slate-50 border border-slate-200 bg-white"
            >
              <Menu className="w-5 h-5" />
            </button>
            <div className="w-10 h-10 rounded-full bg-blue-100 flex items-center justify-center text-blue-600">
              <Bot className="w-6 h-6" />
            </div>
            <div className="flex-1">
              <h1 className="text-lg font-bold text-slate-900">AI Health Assistant</h1>
              <div className="flex items-center gap-1.5 mt-0.5">
                <div className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse"></div>
                <span className="text-xs font-medium text-slate-500">Online</span>
              </div>
            </div>
            <div className="flex items-center gap-1">
              <button 
                onClick={() => {
                  setIsSpeakingEnabled(!isSpeakingEnabled);
                  if (isSpeakingEnabled) window.speechSynthesis.cancel();
                }}
                className="text-slate-400 hover:text-blue-600 transition-colors p-2 rounded-full hover:bg-slate-50"
                title={isSpeakingEnabled ? "Mute AI Voice" : "Enable AI Voice"}
              >
                {isSpeakingEnabled ? <Volume2 className="w-5 h-5" /> : <VolumeX className="w-5 h-5" />}
              </button>
              <button className="text-slate-400 hover:text-blue-600 transition-colors p-2 rounded-full hover:bg-slate-50">
                <MoreVertical className="w-5 h-5" />
              </button>
            </div>
          </div>

          {/* Agent Working Progress Strip */}
          {isTriaging && (
            <div className="flex items-center justify-between w-full bg-slate-50 p-2 rounded-lg border border-slate-100 px-4">
              {AGENT_STEPS.map((step, index) => {
                const isActive = index === currentStep;
                const isPast = index < currentStep;
                return (
                  <div key={step} className="flex items-center gap-2">
                    <div className={`text-xs font-medium ${isActive ? 'text-blue-600 font-bold' : isPast ? 'text-slate-500' : 'text-slate-300'}`}>
                      {step}
                    </div>
                    {index < AGENT_STEPS.length - 1 && (
                      <div className="w-4 h-[1px] bg-slate-200 hidden sm:block"></div>
                    )}
                  </div>
                );
              })}
            </div>
          )}
        </div>

        {/* Chat History Canvas */}
        <div className="flex-grow overflow-y-auto p-4 md:p-6 bg-slate-50 border-x border-slate-200 flex flex-col gap-6">
          {messages.map((msg) => (
            <div key={msg.id} className={`flex items-start gap-3 max-w-[85%] ${msg.sender === 'user' ? 'self-end flex-row-reverse' : ''}`}>
              {msg.sender === 'ai' && (
                <div className="w-8 h-8 rounded-full bg-blue-100 flex-shrink-0 flex items-center justify-center text-blue-600 mt-1 shadow-sm border border-blue-200">
                  <Bot className="w-5 h-5" />
                </div>
              )}
              <div className={`p-4 shadow-sm ${msg.sender === 'user' ? 'bg-blue-600 text-white rounded-2xl rounded-tr-sm' : 'bg-white text-slate-700 rounded-2xl rounded-tl-sm border border-slate-200'}`}>
                <p className="text-sm md:text-base leading-relaxed whitespace-pre-wrap">
                  {msg.text}
                </p>
              </div>
            </div>
          ))}

          {/* AI Typing Indicator */}
          {isTyping && (
            <div className="flex items-start gap-3 max-w-[85%]">
              <div className="w-8 h-8 rounded-full bg-blue-100 flex-shrink-0 flex items-center justify-center text-blue-600 mt-1 shadow-sm border border-blue-200">
                <Bot className="w-5 h-5" />
              </div>
              <div className="bg-white text-slate-700 p-4 rounded-2xl rounded-tl-sm shadow-sm border border-slate-200 flex items-center gap-1.5 h-12">
                <div className="w-2 h-2 bg-slate-400 rounded-full animate-bounce" style={{ animationDelay: '0ms' }}></div>
                <div className="w-2 h-2 bg-slate-400 rounded-full animate-bounce" style={{ animationDelay: '150ms' }}></div>
                <div className="w-2 h-2 bg-slate-400 rounded-full animate-bounce" style={{ animationDelay: '300ms' }}></div>
              </div>
            </div>
          )}
        </div>

        {/* Chat Input Footer */}
        <div className="bg-white rounded-b-2xl p-4 shadow-sm border border-slate-200 border-t-slate-100 z-10 flex flex-col gap-3">
          {/* Generate Report Button - Shows after at least 1 user message */}
          {messages.length > 1 && !isTriaging && (
            <div className="flex justify-center mb-2">
              <button 
                onClick={handleGenerateTriage}
                className="px-6 py-2.5 bg-blue-50 text-blue-700 hover:bg-blue-100 font-semibold rounded-full border border-blue-200 transition-colors flex items-center gap-2 shadow-sm text-sm"
              >
                <Bot className="w-4 h-4" />
                Generate Official Triage Report
              </button>
            </div>
          )}

          {/* Attachment Preview */}
          {attachedImage && (
            <div className="flex items-center gap-3 p-2 bg-slate-50 border border-slate-200 rounded-lg max-w-fit">
              <div className="w-10 h-10 bg-slate-200 rounded-md flex items-center justify-center overflow-hidden">
                <img src={`data:image/jpeg;base64,${attachedImage.base64}`} alt="Attachment" className="w-full h-full object-cover" />
              </div>
              <div className="flex flex-col">
                <span className="text-sm font-medium text-slate-700 truncate max-w-[150px]">{attachedImage.file.name}</span>
                <span className="text-xs text-slate-500">{(attachedImage.file.size / 1024).toFixed(1)} KB</span>
              </div>
              <button 
                onClick={() => setAttachedImage(null)}
                className="p-1 text-slate-400 hover:text-red-500 rounded-full hover:bg-slate-200 transition-colors ml-2"
              >
                <X className="w-4 h-4" />
              </button>
            </div>
          )}

          <div className="flex items-center gap-2 md:gap-3">
            <input 
              type="file" 
              accept="image/*" 
              className="hidden" 
              ref={fileInputRef} 
              onChange={handleFileChange}
            />
            <button 
              onClick={() => fileInputRef.current?.click()}
              className="text-slate-400 hover:text-blue-600 transition-colors p-2.5 rounded-full hover:bg-slate-50 flex-shrink-0"
            >
              <Paperclip className="w-5 h-5" />
            </button>
            <div className="flex-grow relative">
              <input 
                type="text" 
                value={input}
                onChange={(e) => {
                  setInput(e.target.value);
                  setWasLastInputVoice(false);
                }}
                onKeyDown={(e) => e.key === 'Enter' && handleSend()}
                placeholder={isListening ? "Listening..." : "Type your symptoms or speak..."} 
                className={`w-full text-slate-900 text-sm md:text-base rounded-xl py-3 pl-4 pr-12 border transition-all outline-none ${isListening ? 'bg-red-50 border-red-200 focus:border-red-500 focus:ring-2 focus:ring-red-500/20' : 'bg-slate-50 border-slate-200 focus:border-blue-500 focus:ring-2 focus:ring-blue-500/20'}`}
              />
              {isListening && (
                <div className="absolute right-4 top-1/2 -translate-y-1/2 flex items-center gap-1">
                  <div className="w-1.5 h-1.5 rounded-full bg-red-500 animate-pulse"></div>
                  <div className="w-1.5 h-1.5 rounded-full bg-red-500 animate-pulse" style={{ animationDelay: '150ms' }}></div>
                  <div className="w-1.5 h-1.5 rounded-full bg-red-500 animate-pulse" style={{ animationDelay: '300ms' }}></div>
                </div>
              )}
            </div>
            <button 
              onClick={toggleListening}
              className={`transition-colors p-3 rounded-xl flex items-center justify-center shadow-sm flex-shrink-0 ${isListening ? 'bg-red-100 text-red-600 hover:bg-red-200' : 'bg-slate-100 text-slate-600 hover:bg-slate-200'}`}
              title={isListening ? "Stop Recording" : "Start Voice Input"}
            >
              {isListening ? <MicOff className="w-5 h-5" /> : <Mic className="w-5 h-5" />}
            </button>
            <button 
              onClick={handleSend}
              className="bg-blue-600 text-white hover:bg-blue-700 transition-colors p-3 rounded-xl flex items-center justify-center shadow-sm flex-shrink-0 disabled:opacity-50" 
              disabled={(!input.trim() && !attachedImage) || isTyping}
            >
              <Send className="w-5 h-5 ml-0.5" />
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
"""

with open("e:/healthagent/frontend/src/pages/SymptomChecker.tsx", "w", encoding="utf-8") as f:
    f.write(tsx_content)
