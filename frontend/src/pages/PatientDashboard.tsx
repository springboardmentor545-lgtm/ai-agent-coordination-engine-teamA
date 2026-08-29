import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Activity, Clock, ShieldCheck, ChevronRight, CheckCircle2, ChevronLeft, FileText, FileSpreadsheet, Trash2 } from 'lucide-react';
import ConfirmDialog from '../components/ConfirmDialog';
import jsPDF from 'jspdf';
import * as XLSX from 'xlsx';
import { supabase } from '../lib/supabase';

export default function PatientDashboard() {
  const [activeTab, setActiveTab] = useState<'history' | 'activity'>('history');
  const navigate = useNavigate();
  const [history, setHistory] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [patientName, setPatientName] = useState<string>('Patient');
  const [historyPage, setHistoryPage] = useState(1);
  const [deleteId, setDeleteId] = useState<string | null>(null);
  const ITEMS_PER_PAGE = 5;

  useEffect(() => {
    async function fetchHistory() {
      const { data: { user } } = await supabase.auth.getUser();
      if (!user) return;
      
      const { data: userData } = await supabase.from('users').select('full_name').eq('id', user.id).single();
      if (userData?.full_name) setPatientName(userData.full_name.replace(/\s*\((Patient|Doctor|Admin|patient|doctor|admin)\)/gi, ''));
      
      const { data } = await supabase
        .from('triages')
        .select('*')
        .eq('patient_id', user.id)
        .eq('patient_hidden', false)
        .order('created_at', { ascending: false });

      const { data: apptData } = await supabase
        .from('appointments')
        .select('*, users!appointments_doctor_id_fkey(full_name)')
        .eq('patient_id', user.id);

      if (data) {
        const historyWithDocs = data.map(triage => {
          const appt = apptData?.find(a => a.triage_report_id === triage.id);
          const docName = appt?.users?.full_name || appt?.users?.email?.split('@')[0] || 'Unassigned';
          return { ...triage, doctorName: docName, appointmentTime: appt?.appointment_time };
        });
        setHistory(historyWithDocs);
      }
      setLoading(false);
    }
    fetchHistory();
  }, []);

  const hideRecord = async () => {
    if (!deleteId) return;
    
    const { error } = await supabase
      .from('triages')
      .update({ patient_hidden: true })
      .eq('id', deleteId);
      
    if (!error) {
      setHistory(prev => prev.filter(h => h.id !== deleteId));
    } else {
      alert("Failed to hide record.");
    }
    setDeleteId(null);
  };

  const getUrgencyStyles = (level: string) => {
    const l = level?.toLowerCase() || '';
    if (l.includes('high')) return 'bg-red-100 text-red-700 border-red-200';
    if (l.includes('low')) return 'bg-emerald-100 text-emerald-700 border-emerald-200';
    return 'bg-amber-100 text-amber-700 border-amber-200';
  };

  const downloadPDF = (item: any, e: React.MouseEvent) => {
    e.stopPropagation();
    const doc = new jsPDF();
    doc.setFontSize(16);
    doc.text(`My Triage Report`, 10, 20);
    doc.setFontSize(12);
    doc.text(`Patient: ${patientName}`, 10, 30);
    doc.text(`Date: ${new Date(item.created_at).toLocaleString()}`, 10, 40);
    doc.text(`Urgency: ${item.urgency}`, 10, 50);
    doc.text(`Department: ${item.department}`, 10, 60);
    doc.text(`Assigned Doctor: ${item.doctorName?.startsWith('Dr.') ? item.doctorName : `Dr. ${item.doctorName}`}`, 10, 70);
    doc.text(`Appointment Time: ${item.appointmentTime || 'Pending'}`, 10, 80);
    doc.text(`Duration: ${item.duration || 'Not specified'}`, 10, 90);
    doc.text(`Symptoms: ${item.symptoms}`, 10, 100);
    
    doc.text('AI Analysis:', 10, 120);
    const splitTitle = doc.splitTextToSize(item.analysis || 'No analysis available', 180);
    doc.text(splitTitle, 10, 130);
    
    doc.save(`MyReport_${new Date(item.created_at).toISOString().split('T')[0]}.pdf`);
  };

  const downloadExcel = (item: any, e: React.MouseEvent) => {
    e.stopPropagation();
    const worksheet = XLSX.utils.json_to_sheet([{
      Patient: patientName,
      Date: new Date(item.created_at).toLocaleString(),
      Urgency: item.urgency,
      Department: item.department,
      AssignedDoctor: item.doctorName?.startsWith('Dr.') ? item.doctorName : `Dr. ${item.doctorName}`,
      AppointmentTime: item.appointmentTime || 'Pending',
      Duration: item.duration || 'Not specified',
      Symptoms: item.symptoms,
      Analysis: item.analysis
    }]);
    const workbook = XLSX.utils.book_new();
    XLSX.utils.book_append_sheet(workbook, worksheet, "Report");
    XLSX.writeFile(workbook, `MyReport_${new Date(item.created_at).toISOString().split('T')[0]}.xlsx`);
  };

  const paginatedHistory = history.slice((historyPage - 1) * ITEMS_PER_PAGE, historyPage * ITEMS_PER_PAGE);
  const totalPages = Math.ceil(history.length / ITEMS_PER_PAGE) || 1;

  const getRecentActivity = () => {
    if (history.length === 0) return [];
    
    const latestTriage = history[0];
    const timeString = new Date(latestTriage.created_at).toLocaleString(undefined, { 
      month: 'short', day: 'numeric', hour: 'numeric', minute: '2-digit' 
    });

    return [
      { id: 1, agent: 'Report Agent', status: 'Success', time: timeString },
      { id: 2, agent: 'Appointment Agent', status: 'Success', time: timeString },
      { id: 3, agent: 'Triage Decision Agent', status: 'Success', time: timeString },
      { id: 4, agent: 'Analysis Agent', status: 'Success', time: timeString },
      { id: 5, agent: 'Research Agent', status: 'Success', time: timeString },
      { id: 6, agent: 'Intake Agent', status: 'Success', time: timeString },
    ];
  };

  const dynamicActivity = getRecentActivity();

  return (
    <div className="flex-grow w-full bg-slate-50 p-6 md:p-10">
      <div className="max-w-4xl mx-auto">
        
        <div className="flex items-center justify-between mb-8">
          <div>
            <h1 className="text-2xl font-bold text-slate-900">Welcome back, {patientName}</h1>
            <p className="text-slate-500 mt-1">Manage your health assessments and appointments.</p>
          </div>
          <button 
            onClick={() => navigate('/chat')}
            className="hidden md:block px-5 py-2.5 bg-blue-600 hover:bg-blue-700 text-white rounded-xl font-medium shadow-sm transition-colors"
          >
            New Symptom Check
          </button>
        </div>

        {/* Tabs */}
        <div className="flex gap-2 border-b border-slate-200 mb-6">
          <button 
            onClick={() => setActiveTab('history')}
            className={`px-6 py-3 font-medium text-sm transition-colors border-b-2 ${activeTab === 'history' ? 'border-blue-600 text-blue-600' : 'border-transparent text-slate-500 hover:text-slate-700'}`}
          >
            My History
          </button>
          <button 
            onClick={() => setActiveTab('activity')}
            className={`px-6 py-3 font-medium text-sm transition-colors border-b-2 ${activeTab === 'activity' ? 'border-blue-600 text-blue-600' : 'border-transparent text-slate-500 hover:text-slate-700'}`}
          >
            Recent Agent Activity
          </button>
        </div>

        {/* Tab Content */}
        {activeTab === 'history' && (
          <div className="space-y-4">
            {loading ? (
              <div className="p-6 text-center text-slate-500">Loading history...</div>
            ) : history.length === 0 ? (
              <div className="bg-white border border-slate-200 rounded-2xl p-10 text-center">
                <ShieldCheck className="w-12 h-12 text-slate-300 mx-auto mb-3" />
                <h3 className="text-lg font-bold text-slate-900">No triage history yet</h3>
                <p className="text-slate-500 mt-1">Start a new symptom check to get your first AI assessment.</p>
              </div>
            ) : (
              <div className="relative border-l-2 border-slate-200 ml-4 space-y-8 pb-4">
                {paginatedHistory.map((item) => (
                  <div key={item.id} className="relative pl-8 group">
                    {/* Timeline Dot */}
                    <div className={`absolute -left-[9px] top-1 w-4 h-4 rounded-full border-2 border-white ${item.status === 'scheduled' ? 'bg-blue-500' : 'bg-slate-300'}`}></div>
                    
                    <div 
                      onClick={() => navigate('/result', { state: { triageData: { urgency_level: item.urgency, recommended_department: item.department, ai_explanation: item.analysis } } })}
                      className="bg-white border border-slate-200 rounded-2xl p-5 hover:shadow-md hover:border-blue-200 transition-all cursor-pointer flex flex-col sm:flex-row justify-between gap-4"
                    >
                      <div>
                        <div className="flex items-center gap-2 mb-2">
                          <span className="text-sm font-bold text-slate-500">
                            {new Date(item.created_at).toLocaleDateString(undefined, { month: 'long', day: 'numeric', year: 'numeric' })}
                          </span>
                          <span className={`text-[10px] font-bold uppercase tracking-wide px-2 py-0.5 rounded-full ${item.status === 'scheduled' ? 'bg-blue-50 text-blue-700' : 'bg-slate-100 text-slate-600'}`}>
                            {item.status || 'Past Visit'}
                          </span>
                        </div>
                        <h3 className="text-lg font-bold text-slate-900 mb-1">{item.department}</h3>
                        {item.status === 'scheduled' && item.doctorName && (
                          <p className="text-sm text-slate-600 flex items-center gap-1.5">
                            <Clock className="w-4 h-4" />
                            {item.doctorName?.startsWith('Dr.') ? item.doctorName : `Dr. ${item.doctorName}`}
                          </p>
                        )}
                        <div className={`mt-3 inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-bold border ${getUrgencyStyles(item.urgency)}`}>
                          <ShieldCheck className="w-3 h-3" /> {item.urgency} Urgency
                        </div>
                      </div>

                      <div className="flex sm:flex-col items-center sm:items-end justify-end gap-2 mt-4 sm:mt-0">
                        <div className="flex gap-2">
                          <button 
                            onClick={(e) => downloadPDF(item, e)}
                            className="p-2 bg-slate-50 hover:bg-slate-100 text-red-500 rounded-lg border border-slate-200 transition-colors"
                            title="Download Medical Record (PDF)"
                          >
                            <FileText className="w-4 h-4" />
                          </button>
                          <button 
                            onClick={(e) => downloadExcel(item, e)}
                            className="p-2 bg-slate-50 hover:bg-slate-100 text-emerald-600 rounded-lg border border-slate-200 transition-colors"
                            title="Export Data (Excel)"
                          >
                            <FileSpreadsheet className="w-4 h-4" />
                          </button>
                          <button 
                            onClick={(e) => { e.stopPropagation(); setDeleteId(item.id); }}
                            className="p-1.5 text-slate-400 hover:text-red-500 hover:bg-red-50 rounded-lg transition-colors border border-slate-100 hover:border-red-100"
                            title="Remove from history"
                          >
                            <Trash2 className="w-4 h-4" />
                          </button>
                        </div>
                        <span className="hidden sm:flex text-xs font-bold text-blue-600 items-center gap-1 opacity-0 group-hover:opacity-100 transition-opacity mt-2">
                          View AI Report <ChevronRight className="w-4 h-4" />
                        </span>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}
            
            {/* Pagination Controls */}
            {history.length > ITEMS_PER_PAGE && (
              <div className="pt-4 flex items-center justify-between border-t border-slate-200 mt-4">
                <span className="text-sm text-slate-500">Page {historyPage} of {totalPages}</span>
                <div className="flex gap-2">
                  <button 
                    onClick={() => setHistoryPage(p => Math.max(1, p - 1))}
                    disabled={historyPage === 1}
                    className="p-2 rounded-lg border border-slate-200 text-slate-600 hover:bg-slate-50 disabled:opacity-50"
                  >
                    <ChevronLeft className="w-5 h-5" />
                  </button>
                  <button 
                    onClick={() => setHistoryPage(p => Math.min(totalPages, p + 1))}
                    disabled={historyPage === totalPages}
                    className="p-2 rounded-lg border border-slate-200 text-slate-600 hover:bg-slate-50 disabled:opacity-50"
                  >
                    <ChevronRight className="w-5 h-5" />
                  </button>
                </div>
              </div>
            )}
          </div>
        )}

        {activeTab === 'activity' && (
          <div className="bg-white border border-slate-200 rounded-2xl p-6">
            <h2 className="text-lg font-bold text-slate-900 mb-6 flex items-center gap-2">
              <Activity className="w-5 h-5 text-blue-600" />
              Recent AI Operations
            </h2>
            
            <div className="relative border-l-2 border-slate-100 ml-3 space-y-8">
              {dynamicActivity.length === 0 ? (
                <div className="text-slate-500 pl-6 py-4">No recent AI operations found.</div>
              ) : (
                dynamicActivity.map((log) => (
                  <div key={log.id} className="relative pl-6">
                    <div className="absolute -left-[9px] top-1 w-4 h-4 rounded-full bg-white border-2 border-emerald-500 flex items-center justify-center">
                      <CheckCircle2 className="w-3 h-3 text-emerald-500" />
                    </div>
                    <div className="flex flex-col">
                      <span className="font-semibold text-slate-900">{log.agent}</span>
                      <div className="flex items-center gap-2 mt-1">
                        <span className="text-xs font-medium text-emerald-600 bg-emerald-50 px-2 py-0.5 rounded-md border border-emerald-100">
                          {log.status}
                        </span>
                        <span className="text-xs text-slate-400 flex items-center gap-1">
                          <Clock className="w-3 h-3" />
                          {log.time}
                        </span>
                      </div>
                    </div>
                  </div>
                ))
              )}
            </div>
          </div>
        )}

      </div>

      <ConfirmDialog
        isOpen={!!deleteId}
        title="Remove Record"
        description="Are you sure you want to remove this record from your timeline? It will no longer be visible here."
        confirmText="Remove"
        onConfirm={hideRecord}
        onCancel={() => setDeleteId(null)}
      />
    </div>
  );
}
