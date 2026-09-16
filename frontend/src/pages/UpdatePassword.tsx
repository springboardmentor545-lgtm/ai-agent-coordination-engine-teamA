import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { supabase } from '../lib/supabase';
import { ShieldCheck, Lock, CheckCircle2 } from 'lucide-react';

export default function UpdatePassword() {
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const [errorMsg, setErrorMsg] = useState('');
  const [success, setSuccess] = useState(false);
  const navigate = useNavigate();

  useEffect(() => {
    // Check if the user has a valid session (e.g. they clicked the email link)
    supabase.auth.getSession().then(({ data: { session } }) => {
      if (!session) {
        setErrorMsg('Invalid or expired password reset link. Please try again.');
      }
    });

    // Listen for hash changes (Supabase auth redirects)
    const { data: authListener } = supabase.auth.onAuthStateChange((event) => {
      if (event === 'PASSWORD_RECOVERY') {
        setErrorMsg('');
      }
    });

    return () => {
      authListener.subscription.unsubscribe();
    };
  }, []);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (password !== confirmPassword) {
      setErrorMsg("Passwords do not match");
      return;
    }
    
    setLoading(true);
    setErrorMsg('');

    try {
      const { error } = await supabase.auth.updateUser({ password });
      if (error) throw error;
      
      setSuccess(true);
      setTimeout(() => navigate('/dashboard'), 2000);
    } catch (err: any) {
      console.error(err);
      setErrorMsg(err.message || 'Failed to update password');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen w-full flex items-center justify-center bg-slate-50 font-sans text-slate-900 p-4 sm:p-6">
      <div className="w-full max-w-[450px] bg-white p-8 rounded-3xl shadow-xl border border-slate-100 my-8">
        
        <div className="flex justify-center mb-6">
          <div className="w-16 h-16 bg-blue-50 rounded-2xl flex items-center justify-center">
            <ShieldCheck className="w-8 h-8 text-blue-600" />
          </div>
        </div>
        
        <h2 className="text-2xl font-bold text-center mb-2">Set New Password</h2>
        <p className="text-slate-500 mt-2 text-center text-sm mb-8">
          Please enter your new password below.
        </p>

        {errorMsg && (
          <div className="mb-6 p-4 bg-red-50 border border-red-200 text-red-600 rounded-xl text-sm font-medium flex items-start gap-2">
            <ShieldCheck className="w-5 h-5 flex-shrink-0 mt-0.5" />
            <span>{errorMsg}</span>
          </div>
        )}

        {success ? (
          <div className="text-center py-6">
            <CheckCircle2 className="w-16 h-16 text-emerald-500 mx-auto mb-4" />
            <h3 className="text-xl font-bold text-slate-800 mb-2">Password Updated!</h3>
            <p className="text-slate-500 text-sm">Redirecting you to your dashboard...</p>
          </div>
        ) : (
          <form onSubmit={handleSubmit} className="space-y-5">
            <div>
              <label className="block text-sm font-medium text-slate-700 mb-1.5">New Password</label>
              <div className="relative">
                <Lock className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-slate-400" />
                <input 
                  type="password" 
                  required
                  minLength={6}
                  className="w-full pl-11 pr-4 py-3 bg-slate-50 border border-slate-200 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-all outline-none text-sm"
                  placeholder="••••••••"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                />
              </div>
            </div>
            
            <div>
              <label className="block text-sm font-medium text-slate-700 mb-1.5">Confirm New Password</label>
              <div className="relative">
                <Lock className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-slate-400" />
                <input 
                  type="password" 
                  required
                  minLength={6}
                  className="w-full pl-11 pr-4 py-3 bg-slate-50 border border-slate-200 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-all outline-none text-sm"
                  placeholder="••••••••"
                  value={confirmPassword}
                  onChange={(e) => setConfirmPassword(e.target.value)}
                />
              </div>
            </div>

            <button 
              type="submit" 
              disabled={loading}
              className="w-full mt-2 py-3.5 text-white bg-blue-600 hover:bg-blue-700 shadow-blue-500/30 rounded-xl font-semibold shadow-lg transition-all disabled:opacity-50 flex items-center justify-center gap-2"
            >
              {loading ? (
                <div className="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin" />
              ) : (
                'Save New Password'
              )}
            </button>
          </form>
        )}

      </div>
    </div>
  );
}
