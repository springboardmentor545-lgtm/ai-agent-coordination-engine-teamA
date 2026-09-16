<<<<<<< HEAD
import React, { useState, useEffect } from 'react';
import { UserPlus, User, Mail, Lock, AlertCircle, Trash2, Key, CheckCircle2, XCircle } from 'lucide-react';
=======
import React, { useState } from 'react';
import { UserPlus, User, Mail, Lock, AlertCircle } from 'lucide-react';
>>>>>>> team/main
import { supabase } from '../lib/supabase';
import { useNavigate } from 'react-router-dom';

export default function AdminCreateDoctor() {
  const [docName, setDocName] = useState('');
  const [docEmail, setDocEmail] = useState('');
  const [docPassword, setDocPassword] = useState('');
  const [docCreating, setDocCreating] = useState(false);
  const [docMsg, setDocMsg] = useState({ text: '', type: '' });
  const navigate = useNavigate();

<<<<<<< HEAD
  const [doctors, setDoctors] = useState<any[]>([]);
  const [isLoadingDocs, setIsLoadingDocs] = useState(true);
  const [resettingId, setResettingId] = useState<string | null>(null);
  const [newPassword, setNewPassword] = useState('');
  const [actionMsg, setActionMsg] = useState({ text: '', type: '' });

  useEffect(() => {
    checkAdmin();
    fetchDoctors();
=======
  React.useEffect(() => {
    checkAdmin();
>>>>>>> team/main
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

<<<<<<< HEAD
  const fetchDoctors = async () => {
    setIsLoadingDocs(true);
    try {
      const apiUrl = import.meta.env.VITE_API_URL || 'http://localhost:8000';
      const response = await fetch(`${apiUrl}/api/v1/admin/doctors`);
      if (response.ok) {
        const data = await response.json();
        setDoctors(data);
      }
    } catch (err) {
      console.error("Failed to fetch doctors", err);
    }
    setIsLoadingDocs(false);
  };

=======
>>>>>>> team/main
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
<<<<<<< HEAD
        fetchDoctors(); // Refresh list
=======
>>>>>>> team/main
      } else {
        setDocMsg({ text: data.detail || 'Failed to create doctor.', type: 'error' });
      }
    } catch (err) {
      setDocMsg({ text: 'Network error. Backend might be down.', type: 'error' });
    }
    setDocCreating(false);
  };

<<<<<<< HEAD
  const handleResetPassword = async (userId: string) => {
    if (!newPassword || newPassword.length < 6) {
      setActionMsg({ text: 'Password must be at least 6 characters', type: 'error' });
      return;
    }
    try {
      const apiUrl = import.meta.env.VITE_API_URL || 'http://localhost:8000';
      const response = await fetch(`${apiUrl}/api/v1/admin/doctors/${userId}/reset-password`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ new_password: newPassword })
      });
      if (response.ok) {
        setActionMsg({ text: 'Password updated successfully!', type: 'success' });
        setResettingId(null);
        setNewPassword('');
      } else {
        setActionMsg({ text: 'Failed to reset password.', type: 'error' });
      }
    } catch (err) {
      setActionMsg({ text: 'Network error.', type: 'error' });
    }
    setTimeout(() => setActionMsg({ text: '', type: '' }), 3000);
  };

  const handleRevokeAccess = async (userId: string) => {
    if (!window.confirm("Are you sure you want to revoke this doctor's login access? Their historical patient data will remain intact.")) return;
    
    try {
      const apiUrl = import.meta.env.VITE_API_URL || 'http://localhost:8000';
      const response = await fetch(`${apiUrl}/api/v1/admin/doctors/${userId}`, {
        method: 'DELETE'
      });
      if (response.ok) {
        setActionMsg({ text: 'Doctor access revoked successfully.', type: 'success' });
        fetchDoctors();
      } else {
        setActionMsg({ text: 'Failed to revoke access.', type: 'error' });
      }
    } catch (err) {
      setActionMsg({ text: 'Network error.', type: 'error' });
    }
    setTimeout(() => setActionMsg({ text: '', type: '' }), 3000);
  };

=======
>>>>>>> team/main
  return (
    <div className="p-6 md:p-10 max-w-5xl mx-auto flex-grow h-screen overflow-y-auto w-full bg-slate-50">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between mb-8 gap-4">
        <div>
          <h1 className="text-2xl font-bold text-slate-900 flex items-center gap-2">
            <UserPlus className="w-7 h-7 text-indigo-600" />
<<<<<<< HEAD
            Manage Doctors
          </h1>
          <p className="text-slate-500 mt-1">Register and manage doctor accounts securely.</p>
        </div>
      </div>

      <div className="bg-white p-6 rounded-2xl shadow-sm border border-slate-100 mb-10 max-w-2xl mx-auto mt-6">
        <h2 className="text-lg font-bold text-slate-900 mb-6">Create New Doctor</h2>
=======
            Create Doctor ID
          </h1>
          <p className="text-slate-500 mt-1">Register new doctor accounts securely.</p>
        </div>
      </div>

      <div className="bg-white p-6 rounded-2xl shadow-sm border border-slate-100 mb-10 max-w-2xl mx-auto mt-10">
        <h2 className="text-lg font-bold text-slate-900 mb-6">Doctor Account Details</h2>
>>>>>>> team/main
        
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
<<<<<<< HEAD
      </div>

      <div className="bg-white p-6 rounded-2xl shadow-sm border border-slate-100 mb-10 max-w-5xl mx-auto">
        <div className="flex items-center justify-between mb-6">
          <h2 className="text-lg font-bold text-slate-900">Registered Doctors</h2>
          {actionMsg.text && (
            <div className={`text-sm px-3 py-1.5 rounded-md flex items-center gap-1.5 ${actionMsg.type === 'success' ? 'bg-emerald-50 text-emerald-700' : 'bg-red-50 text-red-700'}`}>
              {actionMsg.text}
            </div>
          )}
        </div>
        
        {isLoadingDocs ? (
          <div className="text-center py-10 text-slate-500">Loading doctors...</div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left border-collapse">
              <thead>
                <tr className="border-b border-slate-200 text-sm font-medium text-slate-500">
                  <th className="py-3 px-4">Doctor Name</th>
                  <th className="py-3 px-4">System ID</th>
                  <th className="py-3 px-4 text-center">Status</th>
                  <th className="py-3 px-4 text-right">Actions</th>
                </tr>
              </thead>
              <tbody>
                {doctors.map(doc => {
                  // Safely handle is_active if column doesn't exist yet
                  const isActive = doc.is_active !== false; 
                  return (
                    <tr key={doc.id} className="border-b border-slate-100 last:border-0 hover:bg-slate-50 transition-colors">
                      <td className="py-4 px-4 font-medium text-slate-900">
                        {doc.full_name}
                      </td>
                      <td className="py-4 px-4 text-sm text-slate-500 font-mono">
                        {doc.id.substring(0,8)}...
                      </td>
                      <td className="py-4 px-4 text-center">
                        {isActive ? (
                          <span className="inline-flex items-center gap-1 px-2.5 py-1 rounded-full text-xs font-medium bg-emerald-100 text-emerald-800">
                            <CheckCircle2 className="w-3.5 h-3.5" /> Active
                          </span>
                        ) : (
                          <span className="inline-flex items-center gap-1 px-2.5 py-1 rounded-full text-xs font-medium bg-red-100 text-red-800">
                            <XCircle className="w-3.5 h-3.5" /> Revoked
                          </span>
                        )}
                      </td>
                      <td className="py-4 px-4 flex items-center justify-end gap-2">
                        {resettingId === doc.id ? (
                          <div className="flex items-center gap-2">
                            <input 
                              type="text" 
                              placeholder="New password" 
                              value={newPassword}
                              onChange={(e) => setNewPassword(e.target.value)}
                              className="text-sm px-2 py-1 border border-slate-300 rounded focus:border-indigo-500 outline-none w-32"
                            />
                            <button onClick={() => handleResetPassword(doc.id)} className="text-xs bg-indigo-600 text-white px-2 py-1.5 rounded hover:bg-indigo-700">Save</button>
                            <button onClick={() => {setResettingId(null); setNewPassword('');}} className="text-xs bg-slate-200 text-slate-700 px-2 py-1.5 rounded hover:bg-slate-300">Cancel</button>
                          </div>
                        ) : (
                          <>
                            {isActive && (
                              <button 
                                onClick={() => setResettingId(doc.id)}
                                className="p-2 text-slate-400 hover:text-indigo-600 hover:bg-indigo-50 rounded-lg transition-colors"
                                title="Change Password"
                              >
                                <Key className="w-4 h-4" />
                              </button>
                            )}
                            {isActive && (
                              <button 
                                onClick={() => handleRevokeAccess(doc.id)}
                                className="p-2 text-slate-400 hover:text-red-600 hover:bg-red-50 rounded-lg transition-colors"
                                title="Revoke Login Access (Soft Delete)"
                              >
                                <Trash2 className="w-4 h-4" />
                              </button>
                            )}
                          </>
                        )}
                      </td>
                    </tr>
                  );
                })}
                {doctors.length === 0 && (
                  <tr>
                    <td colSpan={4} className="py-8 text-center text-slate-500 text-sm">
                      No doctors registered yet.
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
        )}
=======
        <p className="mt-6 text-xs text-slate-500 flex items-center gap-1 justify-center">
          <AlertCircle className="w-3.5 h-3.5" /> Requires SUPABASE_SERVICE_ROLE_KEY to bypass authentication flows securely.
        </p>
>>>>>>> team/main
      </div>
    </div>
  );
}
