import { Link, useLocation, useNavigate } from 'react-router-dom';
import { ShieldCheck, UserCircle, LogOut, LayoutDashboard, Stethoscope, MessageSquare, Settings, X, UserPlus, FileText, Calendar } from 'lucide-react';
import { useEffect, useState } from 'react';
import { supabase } from '../lib/supabase';

export default function Sidebar({ isOpen = false, setIsOpen = (_v: boolean) => {} }: { isOpen?: boolean, setIsOpen?: (v: boolean) => void }) {
  const location = useLocation();
  const navigate = useNavigate();
  const [role, setRole] = useState<string | null>(null);
  const [userName, setUserName] = useState<string>('User');

  useEffect(() => {
    async function getUser() {
      const { data: { session } } = await supabase.auth.getSession();
      if (session?.user) {
        const { data } = await supabase.from('users').select('role, full_name').eq('id', session.user.id).single();
        if (data) {
          setRole(data.role);
          let name = data.full_name || session.user.email?.split('@')[0] || 'User';
          name = name.replace(/Hospital Admin \((.*?)\)/i, '$1').replace(/\s*\((Patient|Doctor|Admin|patient|doctor|admin)\)/gi, '');
          setUserName(name);
        }
      }
    }
    getUser();
  }, [location.pathname]);

  const handleLogout = async () => {
    await supabase.auth.signOut();
    navigate('/auth');
  };

  // Do not render nav on auth page
  if (location.pathname === '/auth' || location.pathname === '/') return null;

  return (
    <>
      {/* Mobile Backdrop */}
      {isOpen && (
        <div 
          className="fixed inset-0 bg-slate-900/50 z-40 md:hidden"
          onClick={() => setIsOpen(false)}
        />
      )}

      {/* Sidebar Content */}
      <aside className={`
        fixed inset-y-0 left-0 z-50 w-64 bg-white border-r border-slate-200 h-screen flex flex-col shadow-xl md:shadow-sm flex-shrink-0
        transform transition-transform duration-300 ease-in-out
        ${isOpen ? 'translate-x-0' : '-translate-x-full'}
        md:relative md:translate-x-0
      `}>
        {/* Logo Area */}
        <div className="h-16 flex items-center justify-between px-6 border-b border-slate-100">
          <Link to={role === 'admin' ? '/admin' : role === 'doctor' ? '/doctor' : '/dashboard'} className="flex items-center gap-2 text-xl font-bold text-blue-600" onClick={() => setIsOpen(false)}>
            <ShieldCheck className="w-7 h-7 text-emerald-500" />
            CareTaker AI
          </Link>
          <button className="md:hidden p-1 text-slate-400 hover:text-slate-600 rounded-lg" onClick={() => setIsOpen(false)}>
            <X className="w-5 h-5" />
          </button>
        </div>

      {/* Navigation Links */}
      <div className="flex-1 overflow-y-auto py-6 px-4 flex flex-col gap-2">
        <div className="text-xs font-bold text-slate-400 uppercase tracking-wider mb-2 px-2">Menu</div>
        
        {role === 'admin' ? (
          <>
            <Link 
              to="/admin" 
              className={`flex items-center gap-3 px-4 py-3 rounded-xl font-medium transition-colors ${location.pathname === '/admin' ? 'bg-blue-50 text-blue-700' : 'text-slate-600 hover:bg-slate-50 hover:text-slate-900'}`}
            >
              <LayoutDashboard className={`w-5 h-5 ${location.pathname === '/admin' ? 'text-blue-600' : 'text-slate-400'}`} />
              Command Center
            </Link>
            <Link 
              to="/admin/reports" 
              className={`flex items-center gap-3 px-4 py-3 rounded-xl font-medium transition-colors ${location.pathname === '/admin/reports' ? 'bg-blue-50 text-blue-700' : 'text-slate-600 hover:bg-slate-50 hover:text-slate-900'}`}
            >
              <FileText className={`w-5 h-5 ${location.pathname === '/admin/reports' ? 'text-blue-600' : 'text-slate-400'}`} />
              Generate Reports
            </Link>
            <Link 
              to="/admin/create-doctor" 
              className={`flex items-center gap-3 px-4 py-3 rounded-xl font-medium transition-colors ${location.pathname === '/admin/create-doctor' ? 'bg-blue-50 text-blue-700' : 'text-slate-600 hover:bg-slate-50 hover:text-slate-900'}`}
            >
              <UserPlus className={`w-5 h-5 ${location.pathname === '/admin/create-doctor' ? 'text-blue-600' : 'text-slate-400'}`} />
              Create Doctor ID
            </Link>
          </>
        ) : role === 'doctor' ? (
          <>
            <Link 
              to="/doctor" 
              className={`flex items-center gap-3 px-4 py-3 rounded-xl font-medium transition-colors ${location.pathname === '/doctor' ? 'bg-blue-50 text-blue-700' : 'text-slate-600 hover:bg-slate-50 hover:text-slate-900'}`}
            >
              <Stethoscope className={`w-5 h-5 ${location.pathname === '/doctor' ? 'text-blue-600' : 'text-slate-400'}`} />
              Patient Queue
            </Link>
            <Link 
              to="/doctor/schedule" 
              className={`flex items-center gap-3 px-4 py-3 rounded-xl font-medium transition-colors ${location.pathname === '/doctor/schedule' ? 'bg-blue-50 text-blue-700' : 'text-slate-600 hover:bg-slate-50 hover:text-slate-900'}`}
            >
              <Calendar className={`w-5 h-5 ${location.pathname === '/doctor/schedule' ? 'text-blue-600' : 'text-slate-400'}`} />
              My Schedule
            </Link>
          </>
        ) : (
          <>
            <Link 
              to="/dashboard" 
              className={`flex items-center gap-3 px-4 py-3 rounded-xl font-medium transition-colors ${location.pathname === '/dashboard' ? 'bg-blue-50 text-blue-700' : 'text-slate-600 hover:bg-slate-50 hover:text-slate-900'}`}
            >
              <LayoutDashboard className={`w-5 h-5 ${location.pathname === '/dashboard' ? 'text-blue-600' : 'text-slate-400'}`} />
              Dashboard
            </Link>
            <Link 
              to="/chat" 
              className={`flex items-center gap-3 px-4 py-3 rounded-xl font-medium transition-colors ${location.pathname === '/chat' ? 'bg-blue-50 text-blue-700' : 'text-slate-600 hover:bg-slate-50 hover:text-slate-900'}`}
            >
              <MessageSquare className={`w-5 h-5 ${location.pathname === '/chat' ? 'text-blue-600' : 'text-slate-400'}`} />
              Symptom Checker
            </Link>
          </>
        )}

      </div>

      {/* Settings & Profile Area - Fixed at bottom */}
      <div className="p-4 border-t border-slate-100 flex flex-col gap-4">
        <Link 
          to="/settings" 
          onClick={() => setIsOpen(false)}
          className={`flex items-center gap-3 px-4 py-3 rounded-xl font-medium transition-colors ${location.pathname === '/settings' ? 'bg-blue-50 text-blue-700' : 'text-slate-600 hover:bg-slate-50 hover:text-slate-900'}`}
        >
          <Settings className={`w-5 h-5 ${location.pathname === '/settings' ? 'text-blue-600' : 'text-slate-400'}`} />
          Settings
        </Link>


        <div className="flex items-center justify-between bg-slate-50 border border-slate-200 p-3 rounded-xl">
          <div className="flex items-center gap-3 truncate">
            <div className="w-8 h-8 bg-blue-100 text-blue-700 rounded-full flex items-center justify-center flex-shrink-0">
              <UserCircle className="w-5 h-5" />
            </div>
            <div className="flex flex-col truncate">
              <span className="text-sm font-bold text-slate-700 truncate">{userName}</span>
              <span className="text-xs font-medium text-slate-500 capitalize">{role || 'Patient'}</span>
            </div>
          </div>
          <button 
            onClick={handleLogout} 
            className="p-2 text-slate-400 hover:text-red-600 hover:bg-red-50 rounded-lg transition-colors flex-shrink-0" 
            title="Log out"
          >
            <LogOut className="w-4 h-4" />
          </button>
        </div>
      </div>
    </aside>
    </>
  );
}
