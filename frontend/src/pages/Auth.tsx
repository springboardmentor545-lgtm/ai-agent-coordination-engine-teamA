import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { supabase } from '../lib/supabase';
<<<<<<< HEAD
import { ShieldCheck, User, Stethoscope, Mail, Lock, UserPlus, LogIn, KeyRound, ArrowLeft, Eye, EyeOff } from 'lucide-react';

type AuthView = 'patient_login' | 'patient_signup' | 'forgot_password' | 'internal_login';

export default function Auth() {
  const [view, setView] = useState<AuthView>('patient_login');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [internalRole, setInternalRole] = useState<'doctor' | 'admin' | null>(null);
  
  const [loading, setLoading] = useState(false);
  const [errorMsg, setErrorMsg] = useState('');
  const [successMsg, setSuccessMsg] = useState('');
  const navigate = useNavigate();

  const handleInternalDemoFill = (role: 'doctor' | 'admin') => {
    setView('internal_login');
    setInternalRole(role);
    setEmail('');
    setPassword('');
  };

  const resetState = () => {
    setEmail('');
    setPassword('');
    setErrorMsg('');
    setSuccessMsg('');
    setShowPassword(false);
  };

  const handleGoogleSignIn = async () => {
    try {
      const { error } = await supabase.auth.signInWithOAuth({
        provider: 'google',
        options: {
          redirectTo: `${window.location.origin}/dashboard`
        }
      });
      if (error) throw error;
    } catch (err: any) {
      console.error(err);
      setErrorMsg(err.message || 'Google authentication failed');
    }
  };

  const handleResetPassword = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setErrorMsg('');
    setSuccessMsg('');
    
    try {
      const { error } = await supabase.auth.resetPasswordForEmail(email, {
        redirectTo: `${window.location.origin}/update-password`,
      });
      if (error) throw error;
      setSuccessMsg('Check your email for the password reset link!');
    } catch (err: any) {
      console.error(err);
      setErrorMsg(err.message || 'Failed to send reset link');
    } finally {
      setLoading(false);
    }
  };

=======
import { ShieldCheck, User, Stethoscope } from 'lucide-react';

export default function Auth() {
  const [isLogin] = useState(true);
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [activeRoleDemo, setActiveRoleDemo] = useState<string | null>(null);
  const [role] = useState<'patient' | 'doctor'>('patient');
  const [loading, setLoading] = useState(false);
  const [errorMsg, setErrorMsg] = useState('');
  const navigate = useNavigate();

>>>>>>> team/main
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setErrorMsg('');
<<<<<<< HEAD
    setSuccessMsg('');

    try {
      if (view === 'patient_login' || view === 'internal_login') {
=======

    try {
      if (isLogin) {
>>>>>>> team/main
        // Log in
        const { error: signInError } = await supabase.auth.signInWithPassword({ email, password });
        if (signInError) throw signInError;

        const { data: { user } } = await supabase.auth.getUser();
        if (!user) throw new Error("No user found.");

        const { data: userData } = await supabase.from('users').select('role').eq('id', user.id).single();
        const userRole = userData?.role || 'patient';
        
        if (userRole === 'admin') navigate('/admin');
        else if (userRole === 'doctor') navigate('/doctor');
        else navigate('/dashboard');

<<<<<<< HEAD
      } else if (view === 'patient_signup') {
        // Sign up (Always defaults to 'patient' for external signups)
        const role = 'patient';
=======
      } else {
        // Sign up
>>>>>>> team/main
        const { data, error: signUpError } = await supabase.auth.signUp({
          email,
          password,
          options: {
            data: {
              full_name: email.split('@')[0],
              role: role
            }
          }
        });
        
        if (signUpError) throw signUpError;

<<<<<<< HEAD
=======
        // Auto sign in if session was not established automatically
>>>>>>> team/main
        let currentUser = data.user;
        if (!data.session) {
          const { data: signInData, error: autoSignInError } = await supabase.auth.signInWithPassword({ email, password });
          if (!autoSignInError && signInData.user) {
            currentUser = signInData.user;
          }
        }
        
        if (currentUser) {
<<<<<<< HEAD
=======
          // Insert role & name into public.users
>>>>>>> team/main
          const { error: profileError } = await supabase.from('users').upsert({
            id: currentUser.id,
            role: role,
            full_name: email.split('@')[0]
          });
<<<<<<< HEAD
          if (profileError) console.warn('Profile creation notice:', profileError.message);
        }

        navigate('/dashboard'); 
=======
          
          if (profileError) {
            console.warn('Profile creation notice:', profileError.message);
          }
        }

        if (role === 'doctor') navigate('/doctor');
        else navigate('/dashboard');
>>>>>>> team/main
      }
    } catch (err: any) {
      console.error(err);
      setErrorMsg(err.message || 'Authentication failed');
    } finally {
      setLoading(false);
    }
  };

  return (
<<<<<<< HEAD
    <div className="min-h-screen w-full flex justify-center bg-slate-50 font-sans text-slate-900 overflow-y-auto py-8 sm:py-12 px-4 sm:px-6">
      <div className="w-full max-w-[450px] my-auto bg-white p-8 rounded-3xl shadow-xl border border-slate-100">
        
        {/* Header Section */}
        <div className="flex justify-center mb-6">
          <div className="w-16 h-16 bg-blue-50 rounded-2xl flex items-center justify-center">
            {view === 'internal_login' ? (
               internalRole === 'doctor' ? <Stethoscope className="w-8 h-8 text-indigo-600" /> : <ShieldCheck className="w-8 h-8 text-emerald-600" />
            ) : view === 'forgot_password' ? (
               <KeyRound className="w-8 h-8 text-blue-600" />
            ) : (
               <ShieldCheck className="w-8 h-8 text-blue-600" />
            )}
          </div>
        </div>
        
        <h2 className="text-2xl font-bold text-center mb-2">
          {view === 'patient_login' && 'Welcome Back'}
          {view === 'patient_signup' && 'Create an Account'}
          {view === 'internal_login' && (internalRole === 'doctor' ? 'Doctor Portal' : 'Admin Portal')}
          {view === 'forgot_password' && 'Reset Password'}
        </h2>
        <p className="text-slate-500 mt-2 text-center text-sm">
          {view === 'patient_login' && 'Enter your credentials to access your portal'}
          {view === 'patient_signup' && 'Join VitalGate AI to start tracking your health'}
          {view === 'internal_login' && 'Secure internal staff access'}
          {view === 'forgot_password' && 'Enter your email to receive a secure reset link'}
        </p>

        {/* Back Button for Internal/Forgot Password */}
        {(view === 'internal_login' || view === 'forgot_password') && (
           <button 
             onClick={() => {
               resetState();
               setView('patient_login');
             }}
             className="mt-4 mb-2 flex items-center justify-center gap-2 w-full py-2 text-sm text-slate-500 hover:text-slate-800 transition-colors"
           >
             <ArrowLeft className="w-4 h-4" /> Back to Patient Portal
           </button>
        )}

        {/* Toggle Login / Signup (Only for Patients) */}
        {(view === 'patient_login' || view === 'patient_signup') && (
          <div className="flex p-1 bg-slate-100 rounded-xl mt-6 mb-8">
            <button
              type="button"
              onClick={() => { resetState(); setView('patient_login'); }}
              className={`flex-1 py-2 text-sm font-medium rounded-lg transition-all ${view === 'patient_login' ? 'bg-white text-blue-600 shadow-sm' : 'text-slate-500 hover:text-slate-700'}`}
            >
              Sign In
            </button>
            <button
              type="button"
              onClick={() => { resetState(); setView('patient_signup'); }}
              className={`flex-1 py-2 text-sm font-medium rounded-lg transition-all ${view === 'patient_signup' ? 'bg-white text-blue-600 shadow-sm' : 'text-slate-500 hover:text-slate-700'}`}
            >
              Sign Up
            </button>
          </div>
        )}

        {/* Messages */}
        {errorMsg && (
          <div className="mb-6 mt-4 p-4 bg-red-50 border border-red-200 text-red-600 rounded-xl text-sm font-medium flex items-start gap-2">
            <ShieldCheck className="w-5 h-5 flex-shrink-0 mt-0.5" />
            <span>{errorMsg}</span>
          </div>
        )}
        {successMsg && (
          <div className="mb-6 mt-4 p-4 bg-emerald-50 border border-emerald-200 text-emerald-600 rounded-xl text-sm font-medium flex items-start gap-2">
            <ShieldCheck className="w-5 h-5 flex-shrink-0 mt-0.5" />
            <span>{successMsg}</span>
          </div>
        )}

        {/* Google OAuth (Only for Patients) */}
        {(view === 'patient_login' || view === 'patient_signup') && (
          <>
            <button 
              type="button" 
              onClick={handleGoogleSignIn}
              className="w-full mb-6 py-3 bg-white border border-slate-200 hover:bg-slate-50 text-slate-700 rounded-xl font-semibold shadow-sm transition-all flex items-center justify-center gap-3"
            >
              <svg className="w-5 h-5" viewBox="0 0 24 24">
                <path d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z" fill="#4285F4"/>
                <path d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z" fill="#34A853"/>
                <path d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z" fill="#FBBC05"/>
                <path d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z" fill="#EA4335"/>
              </svg>
              Continue with Google
            </button>

            <div className="flex items-center gap-3 mb-6">
              <div className="flex-1 h-px bg-slate-200"></div>
              <span className="text-xs font-semibold text-slate-400 uppercase tracking-widest">Or</span>
              <div className="flex-1 h-px bg-slate-200"></div>
            </div>
          </>
        )}

        {/* Main Form */}
        <form onSubmit={view === 'forgot_password' ? handleResetPassword : handleSubmit} className="space-y-5 mt-4">
          <div>
            <label className="block text-sm font-medium text-slate-700 mb-1.5">Email Address</label>
            <div className="relative">
              <Mail className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-slate-400" />
              <input 
                type="email" 
                required
                className="w-full pl-11 pr-4 py-3 bg-slate-50 border border-slate-200 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-all outline-none text-sm"
                placeholder="you@example.com"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
              />
            </div>
          </div>
          
          {view !== 'forgot_password' && (
            <div>
              <div className="flex justify-between items-center mb-1.5">
                <label className="block text-sm font-medium text-slate-700">Password</label>
                {view === 'patient_login' && (
                  <button 
                    type="button" 
                    onClick={() => { resetState(); setView('forgot_password'); }}
                    className="text-xs font-semibold text-blue-600 hover:text-blue-700 transition-colors"
                  >
                    Forgot Password?
                  </button>
                )}
              </div>
              <div className="relative">
                <Lock className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-slate-400" />
                <input 
                  type={showPassword ? "text" : "password"} 
                  required
                  minLength={6}
                  className="w-full pl-11 pr-12 py-3 bg-slate-50 border border-slate-200 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-all outline-none text-sm"
                  placeholder="••••••••"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                />
                <button
                  type="button"
                  onClick={() => setShowPassword(!showPassword)}
                  className="absolute right-4 top-1/2 -translate-y-1/2 text-slate-400 hover:text-slate-600 transition-colors"
                >
                  {showPassword ? <EyeOff className="w-5 h-5" /> : <Eye className="w-5 h-5" />}
                </button>
              </div>
            </div>
          )}
=======
    <div className="absolute inset-0 w-full h-full flex items-center justify-center bg-gradient-to-br from-blue-50 to-indigo-50 font-sans text-slate-900 p-6 overflow-hidden">
      <div className="w-full max-w-[450px] bg-white p-8 rounded-2xl shadow-xl border border-slate-100">
        
        <div className="flex justify-center mb-6">
          <ShieldCheck className="w-12 h-12 text-blue-600" />
        </div>
        <h2 className="text-2xl font-bold text-center mb-2">
          {isLogin ? 'Welcome Back' : 'Create an Account'}
        </h2>
        <p className="text-slate-500 mt-2">
          {isLogin ? 'Enter your credentials to access your account' : 'Join CareTaker AI today'}
        </p>

        {errorMsg && (
          <div className="mb-6 p-4 bg-red-50 border border-red-200 text-red-600 rounded-lg text-sm font-medium">
            {errorMsg}
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-5">
          <div>
            <label className="block text-sm font-medium text-slate-700 mb-1">Email</label>
            <input 
              type="email" 
              required
              className="w-full px-4 py-3 bg-slate-50 border border-slate-200 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-all outline-none"
              placeholder="you@example.com"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
            />
          </div>
          
          <div>
            <label className="block text-sm font-medium text-slate-700 mb-1">Password</label>
            <input 
              type="password" 
              required
              minLength={6}
              className="w-full px-4 py-3 bg-slate-50 border border-slate-200 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-all outline-none"
              placeholder="••••••••"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
            />
          </div>
>>>>>>> team/main

          <button 
            type="submit" 
            disabled={loading}
<<<<<<< HEAD
            className={`w-full mt-2 py-3.5 text-white rounded-xl font-semibold shadow-lg transition-all disabled:opacity-50 flex items-center justify-center gap-2 ${
              view === 'internal_login' ? (internalRole === 'doctor' ? 'bg-indigo-600 hover:bg-indigo-700 shadow-indigo-500/30' : 'bg-emerald-600 hover:bg-emerald-700 shadow-emerald-500/30') : 'bg-blue-600 hover:bg-blue-700 shadow-blue-500/30'
            }`}
          >
            {loading ? (
              <div className="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin" />
            ) : view === 'patient_login' || view === 'internal_login' ? (
              <><LogIn className="w-5 h-5" /> Sign In</>
            ) : view === 'patient_signup' ? (
              <><UserPlus className="w-5 h-5" /> Create Account</>
            ) : (
              <><Mail className="w-5 h-5" /> Send Reset Link</>
            )}
          </button>
        </form>

        {/* Internal Staff & Demo Section (Only visible on patient auth pages) */}
        {(view === 'patient_login' || view === 'patient_signup') && (
          <div className="mt-10 pt-8 border-t border-slate-100 relative">
            <div className="absolute top-0 left-1/2 -translate-x-1/2 -translate-y-1/2 bg-white px-4 text-xs font-bold text-slate-300 uppercase tracking-widest flex items-center gap-1.5 whitespace-nowrap">
              <KeyRound className="w-3.5 h-3.5" /> 
              Internal Staff Portals
            </div>
            
            <div className="flex flex-col sm:flex-row gap-3 mt-2">
              <button
                type="button"
                onClick={() => { resetState(); setView('patient_login'); }}
                className="flex-1 py-3 px-3 text-xs font-bold rounded-xl border transition-all flex items-center justify-center gap-2 bg-white hover:bg-slate-50 text-slate-600 border-slate-200"
              >
                <User className="w-4 h-4 text-blue-500" /> Patient
              </button>
              <button
                type="button"
                onClick={() => handleInternalDemoFill('doctor')}
                className="flex-1 py-3 px-3 text-xs font-bold rounded-xl border transition-all flex items-center justify-center gap-2 bg-white hover:bg-indigo-50 text-slate-600 border-slate-200 hover:border-indigo-200 hover:text-indigo-700"
              >
                <Stethoscope className="w-4 h-4 text-indigo-500" /> Doctor
              </button>
              <button
                type="button"
                onClick={() => handleInternalDemoFill('admin')}
                className="flex-1 py-3 px-3 text-xs font-bold rounded-xl border transition-all flex items-center justify-center gap-2 bg-white hover:bg-emerald-50 text-slate-600 border-slate-200 hover:border-emerald-200 hover:text-emerald-700"
              >
                <ShieldCheck className="w-4 h-4 text-emerald-500" /> Admin
              </button>
            </div>
          </div>
        )}

=======
            className="w-full mt-4 py-3 bg-blue-600 hover:bg-blue-700 text-white rounded-xl font-medium shadow-md shadow-blue-500/20 transition-all disabled:opacity-50"
          >
            {loading ? 'Signing In...' : 'Sign In'}
          </button>
        </form>

        {/* Role Selection Logins */}
        <div className="mt-8 border-t border-slate-100 pt-6">
          <p className="text-xs font-bold text-slate-400 uppercase tracking-wider text-center mb-3">Select Role to Continue</p>
          <div className="flex flex-col sm:flex-row gap-3">
            <button
              type="button"
              onClick={() => setActiveRoleDemo('patient')}
              className={`flex-1 py-2.5 px-3 text-xs font-bold rounded-xl border transition-colors flex items-center justify-center gap-1.5 ${activeRoleDemo === 'patient' ? 'bg-blue-600 text-white border-blue-600 shadow-md shadow-blue-500/30' : 'bg-slate-50 hover:bg-slate-100 text-slate-600 border-slate-200'}`}
            >
              <User className="w-4 h-4" /> Patient
            </button>
            <button
              type="button"
              onClick={() => setActiveRoleDemo('doctor')}
              className={`flex-1 py-2.5 px-3 text-xs font-bold rounded-xl border transition-colors flex items-center justify-center gap-1.5 ${activeRoleDemo === 'doctor' ? 'bg-blue-600 text-white border-blue-600 shadow-md shadow-blue-500/30' : 'bg-slate-50 hover:bg-slate-100 text-slate-600 border-slate-200'}`}
            >
              <Stethoscope className="w-4 h-4" /> Doctor
            </button>
            <button
              type="button"
              onClick={() => setActiveRoleDemo('admin')}
              className={`flex-1 py-2.5 px-3 text-xs font-bold rounded-xl border transition-colors flex items-center justify-center gap-1.5 ${activeRoleDemo === 'admin' ? 'bg-blue-600 text-white border-blue-600 shadow-md shadow-blue-500/30' : 'bg-slate-50 hover:bg-slate-100 text-slate-600 border-slate-200'}`}
            >
              <ShieldCheck className="w-4 h-4" /> Admin
            </button>
          </div>
        </div>
>>>>>>> team/main
      </div>
    </div>
  );
}
