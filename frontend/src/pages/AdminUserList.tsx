import { useState, useEffect } from 'react';
import { supabase } from '../lib/supabase';
import { useNavigate } from 'react-router-dom';
import { Users, User, Search, UserCircle2, UserCog, Mail, Calendar } from 'lucide-react';

export default function AdminUserList() {
  const [users, setUsers] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState<'patient' | 'doctor'>('patient');
  const [search, setSearch] = useState('');
  const navigate = useNavigate();

  useEffect(() => {
    checkAdminAndFetchUsers();
  }, []);

  const checkAdminAndFetchUsers = async () => {
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

    await fetchUsers();
  };

  const fetchUsers = async () => {
    setLoading(true);
    // Note: We only want patients and doctors, ignoring admins to keep it clean.
    const { data, error } = await supabase
      .from('users')
      .select('*')
      .in('role', ['patient', 'doctor'])
      .order('created_at', { ascending: false });

    if (error) {
      console.error('Error fetching users:', error);
    } else if (data) {
      setUsers(data);
    }
    setLoading(false);
  };

  // Filter Logic
  const filteredUsers = users.filter(u => {
    const roleMatch = u.role === activeTab;
    const searchMatch = 
      (u.full_name && u.full_name.toLowerCase().includes(search.toLowerCase())) ||
      (u.email && u.email.toLowerCase().includes(search.toLowerCase()));
    
    return roleMatch && searchMatch;
  });

  return (
    <div className="p-6 md:p-8 max-w-7xl mx-auto flex-grow h-screen overflow-y-auto">
      <div className="flex flex-col md:flex-row items-start md:items-center justify-between mb-8 gap-4">
        <div>
          <h1 className="text-2xl font-bold text-slate-900 flex items-center gap-2">
            <Users className="w-7 h-7 text-indigo-600" />
            User Directory
          </h1>
          <p className="text-slate-500 mt-1">View and manage all registered Patients and Doctors.</p>
        </div>
      </div>

      <div className="bg-white rounded-2xl border border-slate-200 shadow-sm overflow-hidden mb-8">
        
        {/* Tabs */}
        <div className="flex border-b border-slate-200">
          <button
            onClick={() => setActiveTab('patient')}
            className={`flex-1 py-4 text-sm font-bold flex items-center justify-center gap-2 transition-colors ${
              activeTab === 'patient' 
                ? 'text-indigo-600 border-b-2 border-indigo-600 bg-indigo-50/50' 
                : 'text-slate-500 hover:text-slate-700 hover:bg-slate-50'
            }`}
          >
            <UserCircle2 className="w-5 h-5" />
            Patient List
          </button>
          <button
            onClick={() => setActiveTab('doctor')}
            className={`flex-1 py-4 text-sm font-bold flex items-center justify-center gap-2 transition-colors ${
              activeTab === 'doctor' 
                ? 'text-indigo-600 border-b-2 border-indigo-600 bg-indigo-50/50' 
                : 'text-slate-500 hover:text-slate-700 hover:bg-slate-50'
            }`}
          >
            <UserCog className="w-5 h-5" />
            Doctor List
          </button>
        </div>

        {/* Search */}
        <div className="p-5 border-b border-slate-100 bg-slate-50">
          <div className="relative max-w-md">
            <Search className="w-5 h-5 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2" />
            <input 
              type="text" 
              placeholder={`Search ${activeTab}s by name or email...`}
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              className="w-full pl-10 pr-4 py-2 border border-slate-200 rounded-xl focus:outline-none focus:border-indigo-500 focus:ring-2 focus:ring-indigo-500/20"
            />
          </div>
        </div>

        {/* User Table */}
        <div className="overflow-x-auto">
          {loading ? (
             <div className="p-12 flex justify-center items-center">
               <div className="animate-spin w-8 h-8 border-4 border-indigo-600 border-t-transparent rounded-full"></div>
             </div>
          ) : filteredUsers.length === 0 ? (
            <div className="p-12 text-center flex flex-col items-center justify-center">
              <User className="w-12 h-12 text-slate-300 mb-4" />
              <h3 className="text-lg font-bold text-slate-900">No {activeTab}s found</h3>
              <p className="text-slate-500 mt-1">Try adjusting your search query.</p>
            </div>
          ) : (
            <table className="w-full text-left border-collapse">
              <thead>
                <tr className="bg-slate-50 border-b border-slate-200">
                  <th className="px-6 py-4 text-xs font-bold text-slate-500 uppercase tracking-wider">Name</th>
                  <th className="px-6 py-4 text-xs font-bold text-slate-500 uppercase tracking-wider">Email</th>
                  <th className="px-6 py-4 text-xs font-bold text-slate-500 uppercase tracking-wider">Role</th>
                  <th className="px-6 py-4 text-xs font-bold text-slate-500 uppercase tracking-wider">Status</th>
                  <th className="px-6 py-4 text-xs font-bold text-slate-500 uppercase tracking-wider">Date Joined</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {filteredUsers.map((user) => {
                  const isActive = user.is_active !== false;
                  return (
                    <tr key={user.id} className="hover:bg-slate-50/50 transition-colors">
                      <td className="px-6 py-4 text-sm whitespace-nowrap">
                        <div className="flex items-center gap-3">
                          <div className="w-8 h-8 rounded-full bg-indigo-100 flex items-center justify-center text-indigo-700 font-bold">
                            {user.full_name ? user.full_name.charAt(0).toUpperCase() : 'U'}
                          </div>
                          <span className="font-semibold text-slate-700">
                            {(user.full_name || 'Unknown').replace(/\s*\((Patient|Doctor|Admin|patient|doctor|admin)\)/gi, '')}
                          </span>
                        </div>
                      </td>
                      <td className="px-6 py-4 text-sm text-slate-600 whitespace-nowrap flex items-center gap-2">
                        <Mail className="w-4 h-4 text-slate-400" />
                        {user.email || 'N/A'}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <span className="capitalize px-2.5 py-1 rounded-md text-xs font-bold bg-slate-100 text-slate-600 border border-slate-200">
                          {user.role}
                        </span>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        {isActive ? (
                          <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-bold bg-emerald-100 text-emerald-800">
                            <span className="w-1.5 h-1.5 rounded-full bg-emerald-500"></span>
                            Active
                          </span>
                        ) : (
                          <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-bold bg-red-100 text-red-800">
                            <span className="w-1.5 h-1.5 rounded-full bg-red-500"></span>
                            Revoked
                          </span>
                        )}
                      </td>
                      <td className="px-6 py-4 text-sm text-slate-500 whitespace-nowrap flex items-center gap-1.5">
                        <Calendar className="w-4 h-4" />
                        {new Date(user.created_at).toLocaleDateString()}
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          )}
        </div>
      </div>
    </div>
  );
}
