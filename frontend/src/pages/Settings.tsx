import { useState, useEffect } from 'react';
import { supabase } from '../lib/supabase';
import { User, Mail, ShieldCheck, Hash, LogOut } from 'lucide-react';
import { useNavigate } from 'react-router-dom';

export default function Settings() {
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();
  const [profile, setProfile] = useState<{
    email: string;
    id: string;
    full_name: string;
    role: string;
  } | null>(null);

  useEffect(() => {
    fetchProfile();
  }, []);

  const fetchProfile = async () => {
    try {
      const { data: { session } } = await supabase.auth.getSession();
      if (!session) {
        navigate('/auth');
        return;
      }

      const { data: userData } = await supabase
        .from('users')
        .select('*')
        .eq('id', session.user.id)
        .single();

      setProfile({
        email: session.user.email || 'N/A',
        id: session.user.id,
        full_name: userData?.full_name || 'User',
        role: userData?.role || 'Patient'
      });
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleLogout = async () => {
    await supabase.auth.signOut();
    navigate('/auth');
  };

  if (loading) {
    return (
      <div className="flex h-full items-center justify-center">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  return (
    <div className="p-8 max-w-4xl mx-auto font-sans">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-slate-900">Account Settings</h1>
        <p className="text-slate-500 mt-1">View and manage your profile details.</p>
      </div>

      <div className="bg-white p-8 rounded-2xl shadow-sm border border-slate-200">
        <div className="flex items-center gap-4 mb-8 pb-8 border-b border-slate-100">
          <div className="w-16 h-16 bg-blue-100 text-blue-700 rounded-full flex items-center justify-center flex-shrink-0">
            <User className="w-8 h-8" />
          </div>
          <div>
            <h2 className="text-2xl font-bold text-slate-900">{profile?.full_name}</h2>
            <p className="text-slate-500 capitalize">{profile?.role} Account</p>
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
          {/* Detail Item */}
          <div className="space-y-1">
            <label className="text-xs font-bold text-slate-400 uppercase tracking-wider flex items-center gap-1.5">
              <Mail className="w-4 h-4" /> Email Address
            </label>
            <div className="p-3 bg-slate-50 border border-slate-200 rounded-xl text-slate-700 font-medium">
              {profile?.email}
            </div>
          </div>

          {/* Detail Item */}
          <div className="space-y-1">
            <label className="text-xs font-bold text-slate-400 uppercase tracking-wider flex items-center gap-1.5">
              <ShieldCheck className="w-4 h-4" /> Role
            </label>
            <div className="p-3 bg-slate-50 border border-slate-200 rounded-xl text-slate-700 font-medium capitalize">
              {profile?.role}
            </div>
          </div>

          {/* Detail Item */}
          <div className="space-y-1 md:col-span-2">
            <label className="text-xs font-bold text-slate-400 uppercase tracking-wider flex items-center gap-1.5">
              <Hash className="w-4 h-4" /> Account ID
            </label>
            <div className="p-3 bg-slate-50 border border-slate-200 rounded-xl text-slate-500 font-mono text-sm break-all">
              {profile?.id}
            </div>
          </div>
        </div>
        
        <div className="mt-10 pt-6 border-t border-slate-100 flex justify-end">
          <button 
            onClick={handleLogout}
            className="flex items-center gap-2 px-6 py-2.5 bg-red-50 text-red-600 hover:bg-red-100 rounded-xl font-bold transition-colors"
          >
            <LogOut className="w-5 h-5" />
            Sign Out
          </button>
        </div>
      </div>
    </div>
  );
}
