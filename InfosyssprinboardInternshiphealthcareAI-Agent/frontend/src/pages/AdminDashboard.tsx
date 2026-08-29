import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { supabase } from '../lib/supabase';
import { 
  Activity, 
  CalendarCheck, 
  Building2,
  LogOut,
  TrendingUp,
  AlertCircle,
  Map
} from 'lucide-react';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell
} from 'recharts';

export default function AdminDashboard() {
  const navigate = useNavigate();
  const [loading, setLoading] = useState(true);
  const [adminName, setAdminName] = useState('');
  
  
  // Stats
  const [stats, setStats] = useState({
    totalTriages: 0,
    totalAppointments: 0,
    highUrgency: 0,
  });

  // Chart Data
  const [deptData, setDeptData] = useState<{name: string, count: number}[]>([]);
  const [urgencyData, setUrgencyData] = useState<{name: string, value: number}[]>([]);

  const COLORS = ['#ef4444', '#f59e0b', '#10b981']; // Red, Yellow, Green

  useEffect(() => {
    checkSession();
  }, []);

  const checkSession = async () => {
    const { data: { session } } = await supabase.auth.getSession();
    if (!session) {
      navigate('/auth');
      return;
    }
    
    // Check if user is admin
    const { data: userData } = await supabase
      .from('users')
      .select('role, full_name')
      .eq('id', session.user.id)
      .single();
      
    if (userData?.role !== 'admin') {
      navigate('/dashboard'); // Kick out non-admins
      return;
    }

    let name = userData.full_name || 'Administrator';
    name = name.replace(/Hospital Admin \((.*?)\)/i, '$1').replace(/\s*\((Patient|Doctor|Admin|patient|doctor|admin)\)/gi, '');
    setAdminName(name);
    fetchDashboardData();
  };

  const fetchDashboardData = async () => {
    try {
      setLoading(true);
      
      // Fetch triages
      const { data: triages, error: triageError } = await supabase
        .from('triages')
        .select('*');
        
      if (triageError) throw triageError;

      // Fetch appointments
      const { data: appointments, error: apptError } = await supabase
        .from('appointments')
        .select('*');
        
      if (apptError) throw apptError;

      // Process Stats
      const highUrgencyCount = triages?.filter(t => t.urgency === 'High').length || 0;
      
      setStats({
        totalTriages: triages?.length || 0,
        totalAppointments: appointments?.length || 0,
        highUrgency: highUrgencyCount
      });

      // Process Department Chart Data
      const deptCounts: Record<string, number> = {};
      triages?.forEach(t => {
        const dept = t.department || 'Unknown';
        deptCounts[dept] = (deptCounts[dept] || 0) + 1;
      });
      const processedDeptData = Object.keys(deptCounts).map(key => ({
        name: key,
        count: deptCounts[key]
      }));
      setDeptData(processedDeptData);

      // Process Urgency Pie Chart Data
      const urgencyCounts = { High: 0, Medium: 0, Low: 0 };
      triages?.forEach(t => {
        if (t.urgency === 'High') urgencyCounts.High++;
        else if (t.urgency === 'Medium') urgencyCounts.Medium++;
        else urgencyCounts.Low++;
      });
      setUrgencyData([
        { name: 'High', value: urgencyCounts.High },
        { name: 'Medium', value: urgencyCounts.Medium },
        { name: 'Low', value: urgencyCounts.Low }
      ]);

    } catch (error) {
      console.error("Error fetching admin data", error);
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
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-emerald-600"></div>
      </div>
    );
  }

  return (
    <div className="p-8 max-w-7xl mx-auto font-sans">
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center mb-8 gap-4">
        <div>
          <h1 className="text-3xl font-bold text-slate-900">Command Center</h1>
          <p className="text-slate-500 mt-1">Welcome back, {adminName}</p>
        </div>
        <button 
          onClick={handleLogout}
          className="flex items-center gap-2 px-4 py-2 bg-white border border-slate-200 rounded-lg text-slate-600 hover:bg-slate-50 hover:text-red-600 transition-colors shadow-sm"
        >
          <LogOut className="w-4 h-4" />
          <span className="font-medium text-sm">Sign Out</span>
        </button>
      </div>

      {/* KPI Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
        <div className="bg-white p-6 rounded-2xl shadow-sm border border-slate-100 flex items-center justify-between">
          <div>
            <p className="text-sm font-medium text-slate-500 mb-1">Total Triages</p>
            <h3 className="text-3xl font-bold text-slate-900">{stats.totalTriages}</h3>
          </div>
          <div className="w-12 h-12 bg-blue-50 text-blue-600 rounded-full flex items-center justify-center">
            <Activity className="w-6 h-6" />
          </div>
        </div>

        <div className="bg-white p-6 rounded-2xl shadow-sm border border-slate-100 flex items-center justify-between">
          <div>
            <p className="text-sm font-medium text-slate-500 mb-1">Total Appointments</p>
            <h3 className="text-3xl font-bold text-slate-900">{stats.totalAppointments}</h3>
          </div>
          <div className="w-12 h-12 bg-indigo-50 text-indigo-600 rounded-full flex items-center justify-center">
            <CalendarCheck className="w-6 h-6" />
          </div>
        </div>

        <div className="bg-white p-6 rounded-2xl shadow-sm border border-slate-100 flex items-center justify-between">
          <div>
            <p className="text-sm font-medium text-slate-500 mb-1">Critical Cases (High)</p>
            <h3 className="text-3xl font-bold text-slate-900">{stats.highUrgency}</h3>
          </div>
          <div className="w-12 h-12 bg-red-50 text-red-600 rounded-full flex items-center justify-center">
            <AlertCircle className="w-6 h-6" />
          </div>
        </div>
      </div>

      {/* Charts Section */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        
        {/* Department Bar Chart */}
        <div className="bg-white p-6 rounded-2xl shadow-sm border border-slate-100">
          <div className="flex items-center gap-2 mb-6">
            <Building2 className="w-5 h-5 text-indigo-600" />
            <h2 className="text-lg font-bold text-slate-900">Cases by Department</h2>
          </div>
          <div className="h-[300px] w-full">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={deptData} margin={{ top: 10, right: 30, left: 0, bottom: 0 }}>
                <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#e2e8f0" />
                <XAxis dataKey="name" axisLine={false} tickLine={false} tick={{fill: '#64748b', fontSize: 12}} />
                <YAxis axisLine={false} tickLine={false} tick={{fill: '#64748b', fontSize: 12}} />
                <Tooltip cursor={{fill: '#f1f5f9'}} contentStyle={{borderRadius: '8px', border: 'none', boxShadow: '0 4px 6px -1px rgb(0 0 0 / 0.1)'}} />
                <Bar dataKey="count" fill="#4f46e5" radius={[4, 4, 0, 0]} barSize={40} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Urgency Pie Chart */}
        <div className="bg-white p-6 rounded-2xl shadow-sm border border-slate-100">
          <div className="flex items-center gap-2 mb-6">
            <TrendingUp className="w-5 h-5 text-emerald-600" />
            <h2 className="text-lg font-bold text-slate-900">Urgency Distribution</h2>
          </div>
          <div className="relative h-[300px] w-full flex items-center justify-center">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie
                  data={urgencyData}
                  cx="50%"
                  cy="50%"
                  innerRadius={80}
                  outerRadius={110}
                  paddingAngle={5}
                  dataKey="value"
                  stroke="none"
                >
                  {urgencyData.map((_entry, index) => (
                    <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip contentStyle={{borderRadius: '8px', border: 'none', boxShadow: '0 4px 6px -1px rgb(0 0 0 / 0.1)'}} />
              </PieChart>
            </ResponsiveContainer>
            
            {/* Custom Legend */}
            <div className="absolute flex flex-col gap-3 right-8">
              {urgencyData.map((entry, index) => (
                <div key={entry.name} className="flex items-center gap-2">
                  <div className="w-3 h-3 rounded-full" style={{ backgroundColor: COLORS[index] }}></div>
                  <span className="text-sm font-medium text-slate-600">{entry.name} ({entry.value})</span>
                </div>
              ))}
            </div>
          </div>
        </div>

      </div>

      {/* Live Hospital Heatmap */}
      <div className="mt-6 bg-white p-6 rounded-2xl shadow-sm border border-slate-100">
        <div className="flex items-center gap-2 mb-6">
          <Map className="w-5 h-5 text-blue-600" />
          <h2 className="text-lg font-bold text-slate-900">Live Hospital Department Heatmap</h2>
        </div>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          {deptData.map((dept, index) => {
            const heatLevel = dept.count > 5 ? 'bg-red-500 text-white' : dept.count > 2 ? 'bg-orange-400 text-white' : 'bg-emerald-100 text-emerald-800';
            const pulse = dept.count > 5 ? 'animate-pulse' : '';
            return (
              <div key={index} className={`p-4 rounded-xl border border-slate-200 shadow-sm flex flex-col items-center justify-center text-center h-32 ${heatLevel} transition-all`}>
                <span className="text-sm font-bold opacity-90">{dept.name}</span>
                <span className={`text-3xl font-black mt-2 ${pulse}`}>{dept.count}</span>
                <span className="text-xs mt-1 opacity-75">Waiting Patients</span>
              </div>
            );
          })}
            {deptData.length === 0 && (
              <div className="col-span-full py-8 text-center text-slate-500 bg-slate-50 rounded-xl border border-slate-200">
                No live data available for heatmap.
              </div>
            )}
          </div>
        </div>
      </div>
  );
}
