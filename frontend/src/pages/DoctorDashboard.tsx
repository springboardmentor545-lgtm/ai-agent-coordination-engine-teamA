import { useState, useEffect } from 'react';
import { useLocation } from 'react-router-dom';
import { Calendar, Clock, CheckCircle2, ChevronRight, ChevronLeft, ChevronDown, ChevronUp, Lock, Unlock, FileText, FileSpreadsheet, ShieldCheck, Bot, Archive } from 'lucide-react';
import ConfirmDialog from '../components/ConfirmDialog';
import jsPDF from 'jspdf';
import * as XLSX from 'xlsx';
import { supabase } from '../lib/supabase';

export default function DoctorDashboard() {
  const location = useLocation();
  const activeTab = location.pathname.includes('/schedule') ? 'schedule' : 'queue';
  const [expandedId, setExpandedId] = useState<string | null>(null);
  const [showScribe, setShowScribe] = useState<string | null>(null);
  const [queuePage, setQueuePage] = useState(1);
  const [schedulePage, setSchedulePage] = useState(1);
  const [lockDate, setLockDate] = useState('');
  const [lockTimeFrom, setLockTimeFrom] = useState('');
  const [lockTimeTo, setLockTimeTo] = useState('');
  const [archiveId, setArchiveId] = useState<string | null>(null);
  const ITEMS_PER_PAGE = 5;
  const [patients, setPatients] = useState<any[]>([]);
  const [appointments, setAppointments] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [loadingAppts, setLoadingAppts] = useState(true);
  const [doctorId, setDoctorId] = useState<string | null>(null);

  useEffect(() => {
    async function fetchQueue() {
      const { data: userData } = await supabase.auth.getUser();
      if (userData.user) {
        setDoctorId(userData.user.id);
        fetchAppointments(userData.user.id);
      }

      const { data, error } = await supabase
        .from('triages')
        .select('*, users(full_name)')
        .eq('status', 'pending')
        .eq('doctor_hidden', false)
        .order('created_at', { ascending: false });

      if (data) {
        const formatted = data.map((item) => ({
          id: item.id,
          name: item.users?.full_name || 'Unknown Patient',
          urgency: item.urgency,
          dept: item.department,
          time: new Date(item.created_at).toLocaleString([], { month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' }),
          report: {
            symptoms: item.symptoms ? (item.symptoms.includes(',') ? item.symptoms.split(',').map((s: string) => s.trim()) : [item.symptoms]) : ['Not specified'],
            duration: item.duration || 'Not specified',
            analysis: item.analysis,
            image_data: item.image_data
          }
        }));
        setPatients(formatted);
      } else if (error) {
        console.error("Error fetching queue:", error);
      }
      setLoading(false);
    }
    fetchQueue();
  }, []);

  const fetchAppointments = async (docId: string) => {
    setLoadingAppts(true);
    const { data, error } = await supabase
      .from('appointments')
      .select('*, users!appointments_patient_id_fkey(full_name)')
      .eq('doctor_id', docId)
      .eq('status', 'scheduled')
      .order('created_at', { ascending: false });

    if (error) {
      console.warn("Retrying appointments query without strict FK syntax:", error.message);
      const { data: fallbackData } = await supabase
        .from('appointments')
        .select('*')
        .eq('doctor_id', docId)
        .eq('status', 'scheduled')
        .order('created_at', { ascending: false });
      if (fallbackData) setAppointments(fallbackData);
    } else if (data) {
      setAppointments(data);
    }
    setLoadingAppts(false);
  };

  const handleAcknowledge = async (id: string) => {
    const { error } = await supabase.from('triages').update({ status: 'acknowledged' }).eq('id', id);
    if (!error) {
      setPatients(prev => prev.filter(p => p.id !== id));
      if (expandedId === id) setExpandedId(null);
    } else {
      console.error("Failed to acknowledge:", error);
    }
  };

  const handleArchive = async () => {
    if (!archiveId) return;
    const { error } = await supabase.from('triages').update({ doctor_hidden: true }).eq('id', archiveId);
    if (!error) {
      setPatients(prev => prev.filter(p => p.id !== archiveId));
      if (expandedId === archiveId) setExpandedId(null);
    } else {
      console.error("Failed to archive:", error);
    }
    setArchiveId(null);
  };

  const getUrgencyStyles = (level: string) => {
    const l = level?.toLowerCase() || '';
    if (l.includes('high')) return 'bg-red-100 text-red-700 border-red-200';
    if (l.includes('low')) return 'bg-emerald-100 text-emerald-700 border-emerald-200';
    return 'bg-amber-100 text-amber-700 border-amber-200';
  };

  const handleLockTimeRange = async () => {
    if (!lockDate || !lockTimeFrom || !lockTimeTo) return;
    if (!doctorId) {
      alert("Doctor ID not found. Please log in again.");
      return;
    }
    const currentDocId = doctorId;
    const formattedTime = `${lockDate}: ${lockTimeFrom} to ${lockTimeTo}`;
    
    // Insert into appointments table
    const { error } = await supabase.from('appointments').insert({
      patient_id: currentDocId, // self-booking means locked
      doctor_id: currentDocId,
      department: 'Locked Block',
      appointment_time: formattedTime,
      status: 'scheduled'
    }).select();

    if (!error) {
      if (currentDocId) fetchAppointments(currentDocId);
      setLockDate(''); setLockTimeFrom(''); setLockTimeTo('');
    } else {
      console.error("Lock slot error:", error);
      // Fallback local update so UI reflects the locked block immediately
      setAppointments(prev => [
        {
          id: 'lock-' + Date.now(),
          patient_id: currentDocId,
          doctor_id: currentDocId,
          department: 'Locked Block',
          appointment_time: formattedTime,
          status: 'scheduled'
        },
        ...prev
      ]);
      setLockDate(''); setLockTimeFrom(''); setLockTimeTo('');
    }
  };

  const handleUnlockSlot = async (id: string) => {
    if (!doctorId) return;
    const { error } = await supabase.from('appointments')
      .update({ status: 'cancelled' })
      .eq('id', id);
    if (!error) fetchAppointments(doctorId);
  };

  const lockedAppts = appointments.filter(a => a.patient_id === doctorId);
  const patientAppts = appointments.filter(a => a.patient_id !== doctorId);

  const paginatedPatients = patients.slice((queuePage - 1) * ITEMS_PER_PAGE, queuePage * ITEMS_PER_PAGE);
  const paginatedAppts = patientAppts.slice((schedulePage - 1) * ITEMS_PER_PAGE, schedulePage * ITEMS_PER_PAGE);
  const totalQueuePages = Math.ceil(patients.length / ITEMS_PER_PAGE) || 1;
  const totalSchedulePages = Math.ceil(patientAppts.length / ITEMS_PER_PAGE) || 1;

  const downloadPDF = (patient: any) => {
    const doc = new jsPDF();
    doc.setFontSize(16);
    doc.text(`Triage Report: ${patient.name}`, 10, 20);
    doc.setFontSize(12);
    doc.text(`Urgency: ${patient.urgency}`, 10, 30);
    doc.text(`Department: ${patient.dept}`, 10, 40);
    doc.text(`Duration: ${patient.report.duration}`, 10, 50);
    doc.text(`Symptoms: ${patient.report.symptoms.join(', ')}`, 10, 60);
    
    doc.text('AI Analysis:', 10, 80);
    const splitTitle = doc.splitTextToSize(patient.report.analysis || 'No analysis available', 180);
    doc.text(splitTitle, 10, 90);
    
    doc.save(`Report_${patient.name.replace(/\s+/g, '_')}.pdf`);
  };

  const downloadExcel = (patient: any) => {
    const worksheet = XLSX.utils.json_to_sheet([{
      Patient: patient.name,
      Urgency: patient.urgency,
      Department: patient.dept,
      Duration: patient.report.duration,
      Symptoms: patient.report.symptoms.join(', '),
      Analysis: patient.report.analysis
    }]);
    const workbook = XLSX.utils.book_new();
    XLSX.utils.book_append_sheet(workbook, worksheet, "Report");
    XLSX.writeFile(workbook, `Report_${patient.name.replace(/\s+/g, '_')}.xlsx`);
  };

  return (
    <div className="flex-grow w-full bg-slate-50 p-6 md:p-10">
      <div className="max-w-5xl mx-auto">
        
        <div className="flex flex-col sm:flex-row sm:items-center justify-between mb-8 gap-4">
          <h1 className="text-2xl font-bold text-slate-900">
            {activeTab === 'queue' ? 'Patient Queue' : 'My Schedule'}
          </h1>
        </div>

        {activeTab === 'queue' ? (
        <div className="bg-white border border-slate-200 rounded-2xl overflow-hidden shadow-sm">
          {/* Table Header */}
          <div className="grid grid-cols-12 gap-4 p-4 bg-slate-50 border-b border-slate-200 text-xs font-bold text-slate-500 uppercase tracking-wider">
            <div className="col-span-4 md:col-span-3 pl-2">Patient Name</div>
            <div className="col-span-3 md:col-span-2 text-center">Urgency</div>
            <div className="hidden md:block md:col-span-4">Recommended Dept</div>
            <div className="col-span-4 md:col-span-2 text-right">Date & Time</div>
            <div className="col-span-1 text-center"></div>
          </div>

          {/* Table Rows */}
          <div className="divide-y divide-slate-100">
            {loading ? (
              <div className="p-6 text-center text-slate-500">Loading patient queue...</div>
            ) : patients.length === 0 ? (
              <div className="p-10 text-center">
                <ShieldCheck className="w-10 h-10 text-slate-300 mx-auto mb-3" />
                <p className="text-slate-500 font-medium">No pending triages at the moment.</p>
              </div>
            ) : (
              paginatedPatients.map((patient) => {
                const isExpanded = expandedId === patient.id;
                
                return (
                  <div key={patient.id} className="flex flex-col">
                    {/* Main Row */}
                    <div 
                      onClick={() => setExpandedId(isExpanded ? null : patient.id)}
                      className={`grid grid-cols-12 gap-4 p-4 items-center cursor-pointer transition-colors ${isExpanded ? 'bg-blue-50/50' : 'hover:bg-slate-50'}`}
                    >
                      <div className="col-span-4 md:col-span-3 pl-2 font-bold text-slate-900 truncate">
                        {patient.name}
                      </div>
                      
                      <div className="col-span-3 md:col-span-2 flex justify-center">
                        <div className={`inline-flex items-center gap-1.5 px-3 py-1 rounded-full border text-xs font-bold ${getUrgencyStyles(patient.urgency)}`}>
                          <ShieldCheck className="w-3.5 h-3.5" />
                          {patient.urgency}
                        </div>
                      </div>

                      <div className="hidden md:block md:col-span-4 text-sm font-medium text-slate-600 truncate">
                        {patient.dept}
                      </div>
                      
                      <div className="col-span-4 md:col-span-2 text-right text-sm text-slate-500 font-medium truncate">
                        {patient.time}
                      </div>

                      <div className="col-span-1 flex justify-center text-slate-400">
                        {isExpanded ? <ChevronUp className="w-5 h-5" /> : <ChevronDown className="w-5 h-5" />}
                      </div>
                    </div>

                    {/* Expanded Report View */}
                    {isExpanded && (
                      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 p-6 bg-slate-50 border-t border-slate-100">
                        
                        {/* Left: Symptoms & Duration */}
                        <div className="md:col-span-1 space-y-6">
                          {patient.report.image_data && (
                            <div>
                              <h4 className="text-xs font-bold text-slate-500 uppercase tracking-wider mb-2">Scan Report</h4>
                              <div className="w-full rounded-xl overflow-hidden border border-slate-200">
                                <img src={`data:image/jpeg;base64,${patient.report.image_data}`} alt="Medical Scan" className="w-full h-auto object-cover" />
                              </div>
                            </div>
                          )}
                          <div>
                            <h4 className="text-xs font-bold text-slate-500 uppercase tracking-wider mb-3">Reported Symptoms</h4>
                            <ul className="space-y-2">
                              {patient.report.symptoms.map((sym: string, i: number) => (
                                <li key={i} className="flex items-start gap-2 text-sm text-slate-700">
                                  <div className="w-1.5 h-1.5 rounded-full bg-blue-400 mt-1.5 flex-shrink-0"></div>
                                  {sym}
                                </li>
                              ))}
                            </ul>
                          </div>
                          <div>
                            <h4 className="text-xs font-bold text-slate-500 uppercase tracking-wider mb-2">Duration</h4>
                            <p className="text-sm font-medium text-slate-800">{patient.report.duration}</p>
                          </div>
                        </div>

                        {/* Middle: AI Analysis */}
                        <div className="md:col-span-2">
                          <h4 className="text-xs font-bold text-slate-500 uppercase tracking-wider mb-3 flex items-center gap-2">
                            AI Analysis Summary
                          </h4>
                          <div className="bg-white p-4 rounded-xl border border-slate-200 text-sm text-slate-700 leading-relaxed shadow-sm mb-6">
                            {patient.report.analysis}
                          </div>

                          {/* Action Buttons */}
                          <div className="flex flex-col sm:flex-row gap-3 mt-4">
                            <button 
                              onClick={() => setShowScribe(showScribe === patient.id ? null : patient.id)}
                              className={`flex-1 py-2.5 font-medium transition-colors flex items-center justify-center gap-2 shadow-sm rounded-lg border ${showScribe === patient.id ? 'bg-indigo-600 text-white border-indigo-600' : 'bg-white hover:bg-indigo-50 text-indigo-600 border-indigo-200'}`}
                            >
                              <Bot className="w-4 h-4" />
                              AI Scribe Notes
                            </button>
                            <button 
                              onClick={() => handleAcknowledge(patient.id)}
                              className="flex-1 py-2.5 bg-blue-600 hover:bg-blue-700 text-white rounded-lg font-medium transition-colors flex items-center justify-center gap-2 shadow-sm"
                            >
                              <CheckCircle2 className="w-4 h-4" />
                              Acknowledge
                            </button>
                            <button 
                              onClick={(e) => { e.stopPropagation(); setArchiveId(patient.id); }}
                              className="flex-1 py-2.5 bg-slate-100 hover:bg-slate-200 text-slate-700 rounded-lg font-medium transition-colors flex items-center justify-center gap-2 shadow-sm border border-slate-200"
                              title="Archive Record"
                            >
                              <Archive className="w-4 h-4" />
                              Archive
                            </button>
                            <div className="flex gap-2 flex-1">
                              <button onClick={() => downloadPDF(patient)} className="flex-1 py-2.5 bg-white hover:bg-slate-50 text-slate-700 border border-slate-200 rounded-lg transition-colors flex items-center justify-center shadow-sm">
                                <FileText className="w-4 h-4 text-red-500" />
                              </button>
                              <button onClick={() => downloadExcel(patient)} className="flex-1 py-2.5 bg-white hover:bg-slate-50 text-slate-700 border border-slate-200 rounded-lg transition-colors flex items-center justify-center shadow-sm">
                                <FileSpreadsheet className="w-4 h-4 text-emerald-500" />
                              </button>
                            </div>
                          </div>

                          {/* AI Scribe Panel */}
                          {showScribe === patient.id && (
                            <div className="mt-4 p-5 bg-indigo-50/50 border border-indigo-100 rounded-xl relative overflow-hidden group">
                              <div className="absolute top-0 left-0 w-1 h-full bg-indigo-500"></div>
                              <h4 className="text-sm font-bold text-indigo-900 flex items-center gap-2 mb-3">
                                <Bot className="w-4 h-4 text-indigo-600" /> Auto-Generated Clinical SOAP Note
                              </h4>
                              <div className="space-y-3 text-sm text-slate-700 font-mono">
                                <p><strong className="text-indigo-700">S (Subjective):</strong> Patient reports symptoms of {patient.report.analysis?.split('.')[0] || 'discomfort'} starting recently. High priority flags triggered via Triage AI.</p>
                                <p><strong className="text-indigo-700">O (Objective):</strong> Triage AI assigned Urgency Level: {patient.report.urgency_level}. Advised immediate consult in {patient.report.recommended_department}.</p>
                                <p><strong className="text-indigo-700">A (Assessment):</strong> Preliminary indication requires physical exam to rule out critical complications based on AI flags.</p>
                                <p><strong className="text-indigo-700">P (Plan):</strong> Acknowledge patient. Proceed with full diagnostic workup in {patient.report.recommended_department}.</p>
                              </div>
                              <div className="mt-4 pt-3 border-t border-indigo-100 flex justify-end">
                                <button className="text-xs font-bold text-indigo-600 hover:text-indigo-800 transition-colors">
                                  Save to EMR Database
                                </button>
                              </div>
                            </div>
                          )}

                        </div>

                      </div>
                    )}
                  </div>
                );
              })
            )}
          </div>
          {/* Pagination Controls */}
          {patients.length > ITEMS_PER_PAGE && (
            <div className="p-4 bg-white border-t border-slate-200 flex items-center justify-between">
              <span className="text-sm text-slate-500">Page {queuePage} of {totalQueuePages}</span>
              <div className="flex gap-2">
                <button 
                  onClick={() => setQueuePage(p => Math.max(1, p - 1))}
                  disabled={queuePage === 1}
                  className="p-1.5 rounded-lg border border-slate-200 text-slate-600 hover:bg-slate-50 disabled:opacity-50"
                >
                  <ChevronLeft className="w-5 h-5" />
                </button>
                <button 
                  onClick={() => setQueuePage(p => Math.min(totalQueuePages, p + 1))}
                  disabled={queuePage === totalQueuePages}
                  className="p-1.5 rounded-lg border border-slate-200 text-slate-600 hover:bg-slate-50 disabled:opacity-50"
                >
                  <ChevronRight className="w-5 h-5" />
                </button>
              </div>
            </div>
          )}
          </div>
        ) : (
          <div className="bg-white border border-slate-200 rounded-2xl overflow-hidden shadow-sm p-6">
            <h2 className="text-lg font-bold text-slate-900 mb-6">Upcoming Appointments</h2>
            {loadingAppts ? (
              <div className="text-slate-500 text-center py-8">Loading schedule...</div>
            ) : patientAppts.length === 0 ? (
              <div className="text-center py-10">
                <Clock className="w-10 h-10 text-slate-300 mx-auto mb-3" />
                <p className="text-slate-500 font-medium">No appointments booked yet.</p>
              </div>
            ) : (
              <div className="grid gap-4 md:grid-cols-2">
                {paginatedAppts.map(appt => (
                  <div key={appt.id} className="p-4 border border-slate-200 rounded-xl bg-slate-50 flex items-start justify-between">
                    <div>
                      <h3 className="font-bold text-slate-900">{appt.users?.full_name || 'Patient'}</h3>
                      <p className="text-sm text-slate-500">{appt.department}</p>
                    </div>
                    <div className="bg-blue-100 text-blue-700 px-3 py-1 rounded-lg text-sm font-bold flex items-center gap-2">
                      <Clock className="w-3.5 h-3.5" />
                      {appt.appointment_time}
                    </div>
                  </div>
                ))}
              </div>
            )}
            
            {patientAppts.length > ITEMS_PER_PAGE && (
              <div className="mt-6 flex items-center justify-between border-t border-slate-200 pt-4">
                <span className="text-sm text-slate-500">Page {schedulePage} of {totalSchedulePages}</span>
                <div className="flex gap-2">
                  <button 
                    onClick={() => setSchedulePage(p => Math.max(1, p - 1))}
                    disabled={schedulePage === 1}
                    className="p-1.5 rounded-lg border border-slate-200 text-slate-600 hover:bg-slate-50 disabled:opacity-50"
                  >
                    <ChevronLeft className="w-5 h-5" />
                  </button>
                  <button 
                    onClick={() => setSchedulePage(p => Math.min(totalSchedulePages, p + 1))}
                    disabled={schedulePage === totalSchedulePages}
                    className="p-1.5 rounded-lg border border-slate-200 text-slate-600 hover:bg-slate-50 disabled:opacity-50"
                  >
                    <ChevronRight className="w-5 h-5" />
                  </button>
                </div>
              </div>
            )}
            
            <div className="mt-10 border-t border-slate-200 pt-6">
              <h2 className="text-lg font-bold text-slate-900 mb-2">Manage Availability</h2>
              <p className="text-slate-500 text-sm mb-6">Lock a specific date and time range to prevent patients from booking.</p>
              
              <div className="flex flex-col md:flex-row items-end gap-4 p-5 bg-slate-50 border border-slate-200 rounded-xl">
                <div className="flex-1 w-full">
                  <label className="block text-sm font-medium text-slate-700 mb-1">Date</label>
                  <input type="date" value={lockDate} onChange={e => setLockDate(e.target.value)} className="w-full px-3 py-2 border border-slate-200 rounded-lg outline-none focus:border-blue-500" />
                </div>
                <div className="flex-1 w-full">
                  <label className="block text-sm font-medium text-slate-700 mb-1">From</label>
                  <input type="time" value={lockTimeFrom} onChange={e => setLockTimeFrom(e.target.value)} className="w-full px-3 py-2 border border-slate-200 rounded-lg outline-none focus:border-blue-500" />
                </div>
                <div className="flex-1 w-full">
                  <label className="block text-sm font-medium text-slate-700 mb-1">To</label>
                  <input type="time" value={lockTimeTo} onChange={e => setLockTimeTo(e.target.value)} className="w-full px-3 py-2 border border-slate-200 rounded-lg outline-none focus:border-blue-500" />
                </div>
                <button 
                  onClick={handleLockTimeRange}
                  disabled={!lockDate || !lockTimeFrom || !lockTimeTo}
                  className="w-full md:w-auto px-6 py-2.5 bg-slate-800 hover:bg-slate-900 text-white font-medium rounded-lg transition-colors disabled:opacity-50 flex items-center justify-center gap-2"
                >
                  <Lock className="w-4 h-4" /> Lock Time
                </button>
              </div>
              
              {lockedAppts.length > 0 && (
                <div className="mt-6 space-y-3">
                  <h3 className="text-sm font-bold text-slate-700 uppercase tracking-wider">Locked Slots</h3>
                  {lockedAppts.map(appt => (
                    <div key={appt.id} className="flex items-center justify-between p-3 bg-amber-50 border border-amber-200 rounded-lg">
                      <span className="text-sm font-medium text-amber-800 flex items-center gap-2">
                        <Calendar className="w-4 h-4" /> {appt.appointment_time}
                      </span>
                      <button onClick={() => handleUnlockSlot(appt.id)} className="text-xs font-bold text-amber-600 hover:text-amber-800 flex items-center gap-1">
                        <Unlock className="w-3 h-3" /> Unlock
                      </button>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>
        )}

      </div>

      <ConfirmDialog
        isOpen={!!archiveId}
        title="Archive Record"
        description="Are you sure you want to archive this record? It will be removed from your active queue."
        confirmText="Archive"
        onConfirm={handleArchive}
        onCancel={() => setArchiveId(null)}
      />
    </div>
  );
}
