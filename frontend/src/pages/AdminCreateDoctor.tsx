import React, { useState } from 'react';
import { UserPlus, User, Mail, Lock, AlertCircle } from 'lucide-react';
import { supabase } from '../lib/supabase';
import { useNavigate } from 'react-router-dom';

export default function AdminCreateDoctor() {
  const [docName, setDocName] = useState('');
  const [docEmail, setDocEmail] = useState('');
  const [docPassword, setDocPassword] = useState('');
  const [docCreating, setDocCreating] = useState(false);
  const [docMsg, setDocMsg] = useState({ text: '', type: '' });
  const navigate = useNavigate();

  React.useEffect(() => {
    checkAdmin();
  }, []);

  const checkAdmin = async () => {
    const { data: { session } } = await supabase.auth.getSession();
    if (!session?.user) {
      navigate('/auth');
      return;
    }
    const { data: userData } = await supabase
      .from('users')
      .select('role')
      .eq('id', session.user.id)
      .single();

    if (userData?.role !== 'admin') {
      navigate('/dashboard');
      return;
    }
  };

  const handleCreateDoctor = async (e: React.FormEvent) => {
    e.preventDefault();
    setDocCreating(true);
    setDocMsg({ text: '', type: '' });
    try {
      const apiUrl = import.meta.env.VITE_API_URL || 'http://localhost:8000';
      const response = await fetch(`${apiUrl}/api/v1/admin/create-doctor`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          email: docEmail,
          password: docPassword,
          full_name: docName
        })
      });
      const data = await response.json();
      if (response.ok) {
        setDocMsg({ text: 'Doctor created successfully!', type: 'success' });
        setDocName(''); setDocEmail(''); setDocPassword('');
      } else {
        setDocMsg({ text: data.detail || 'Failed to create doctor.', type: 'error' });
      }
    } catch (err) {
      setDocMsg({ text: 'Network error. Backend might be down.', type: 'error' });
    }
    setDocCreating(false);
  };

  return (
    <div className="p-6 md:p-10 max-w-5xl mx-auto flex-grow h-screen overflow-y-auto w-full bg-slate-50">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between mb-8 gap-4">
        <div>
          <h1 className="text-2xl font-bold text-slate-900 flex items-center gap-2">
            <UserPlus className="w-7 h-7 text-indigo-600" />
            Create Doctor ID
          </h1>
          <p className="text-slate-500 mt-1">Register new doctor accounts securely.</p>
        </div>
      </div>

      <div className="bg-white p-6 rounded-2xl shadow-sm border border-slate-100 mb-10 max-w-2xl mx-auto mt-10">
        <h2 className="text-lg font-bold text-slate-900 mb-6">Doctor Account Details</h2>
        
        <form onSubmit={handleCreateDoctor} className="space-y-5">
          <div>
            <label className="block text-sm font-medium text-slate-700 mb-1 flex items-center gap-1.5"><User className="w-3.5 h-3.5"/> Full Name</label>
            <input type="text" required value={docName} onChange={e => setDocName(e.target.value)} className="w-full px-3 py-2 border border-slate-200 rounded-lg outline-none focus:border-indigo-500 focus:ring-2 focus:ring-indigo-500/20" placeholder="Dr. Sarah Smith" />
          </div>
          <div>
            <label className="block text-sm font-medium text-slate-700 mb-1 flex items-center gap-1.5"><Mail className="w-3.5 h-3.5"/> Email</label>
            <input type="email" required value={docEmail} onChange={e => setDocEmail(e.target.value)} className="w-full px-3 py-2 border border-slate-200 rounded-lg outline-none focus:border-indigo-500 focus:ring-2 focus:ring-indigo-500/20" placeholder="sarah@hospital.com" />
          </div>
          <div>
            <label className="block text-sm font-medium text-slate-700 mb-1 flex items-center gap-1.5"><Lock className="w-3.5 h-3.5"/> Password</label>
            <input type="password" required value={docPassword} onChange={e => setDocPassword(e.target.value)} minLength={6} className="w-full px-3 py-2 border border-slate-200 rounded-lg outline-none focus:border-indigo-500 focus:ring-2 focus:ring-indigo-500/20" placeholder="••••••••" />
          </div>
          <button 
            type="submit" 
            disabled={docCreating}
            className="w-full py-3 bg-indigo-600 hover:bg-indigo-700 text-white font-medium rounded-lg transition-colors disabled:opacity-50 mt-4 shadow-sm"
          >
            {docCreating ? 'Registering...' : 'Create Doctor'}
          </button>
        </form>
        {docMsg.text && (
          <div className={`mt-6 p-4 rounded-xl text-sm font-medium flex items-center gap-2 ${docMsg.type === 'success' ? 'bg-emerald-50 text-emerald-700 border border-emerald-200' : 'bg-red-50 text-red-700 border border-red-200'}`}>
            {docMsg.type === 'error' && <AlertCircle className="w-4 h-4" />}
            {docMsg.text}
          </div>
        )}
        <p className="mt-6 text-xs text-slate-500 flex items-center gap-1 justify-center">
          <AlertCircle className="w-3.5 h-3.5" /> Requires SUPABASE_SERVICE_ROLE_KEY to bypass authentication flows securely.
        </p>
      </div>
    </div>
  );
}
