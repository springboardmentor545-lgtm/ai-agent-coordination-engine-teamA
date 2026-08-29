import { useState, useEffect } from 'react';
import { supabase } from '../lib/supabase';
import { useNavigate } from 'react-router-dom';
import { Download, Search, Filter, FileText, AlertTriangle, UserCircle, Activity, FileDown, Trash2 } from 'lucide-react';
import ConfirmDialog from '../components/ConfirmDialog';
import jsPDF from 'jspdf';
import * as XLSX from 'xlsx';

type TriageData = {
  id: string;
  created_at: string;
  symptoms: string;
  analysis: string;
  urgency: string;
  department: string;
  patient: {
    full_name: string;
  };
  doctorName?: string;
};

export default function AdminReports() {
  const [reports, setReports] = useState<TriageData[]>([]);
  const [loading, setLoading] = useState(true);
  const [urgencyFilter, setUrgencyFilter] = useState('All');
  const [doctorFilter, setDoctorFilter] = useState('All');
  const [diseaseSearch, setDiseaseSearch] = useState('');
  const [currentPage, setCurrentPage] = useState(1);
  const [deleteId, setDeleteId] = useState<string | null>(null);
  const ITEMS_PER_PAGE = 10;
  const navigate = useNavigate();

  useEffect(() => {
    checkAdminAndFetchData();
  }, []);

  const checkAdminAndFetchData = async () => {
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

    await fetchReports();
  };

  const fetchReports = async () => {
    setLoading(true);
    const { data, error } = await supabase
      .from('triages')
      .select(`
        id,
        created_at,
        symptoms,
        analysis,
        urgency,
        department,
        patient:users(full_name)
      `)
      .order('created_at', { ascending: false });

    const { data: apptData } = await supabase
      .from('appointments')
      .select('*, users!appointments_doctor_id_fkey(full_name)');

    if (error) {
      console.error('Error fetching reports:', error);
    } else if (data) {
      const reportsWithDoctors = data.map((triage: any) => {
        const appt = apptData?.find(a => a.triage_report_id === triage.id);
        let docName = appt?.users?.full_name || 'Unassigned';
        docName = docName.replace(/\s*\((Patient|Doctor|Admin|patient|doctor|admin)\)/gi, '');
        return { ...triage, doctorName: docName };
      });
      setReports(reportsWithDoctors as unknown as TriageData[]);
    }
    setLoading(false);
  };

  // Filter logic
  const filteredReports = reports.filter(r => {
    const matchUrgency = urgencyFilter === 'All' || r.urgency === urgencyFilter;
    const matchDoctor = doctorFilter === 'All' || r.doctorName === doctorFilter;
    const matchDisease = r.analysis?.toLowerCase().includes(diseaseSearch.toLowerCase()) || 
                         r.symptoms?.toLowerCase().includes(diseaseSearch.toLowerCase());
    return matchUrgency && matchDoctor && matchDisease;
  });

  const uniqueDoctors = ['All', ...Array.from(new Set(reports.map(r => r.doctorName).filter(Boolean)))];

  const totalPages = Math.ceil(filteredReports.length / ITEMS_PER_PAGE) || 1;
  const paginatedReports = filteredReports.slice((currentPage - 1) * ITEMS_PER_PAGE, currentPage * ITEMS_PER_PAGE);

  const getUrgencyColor = (level: string) => {
    switch(level) {
      case 'Critical': return 'bg-red-100 text-red-700 border-red-200';
      case 'High': return 'bg-orange-100 text-orange-700 border-orange-200';
      case 'Medium': return 'bg-yellow-100 text-yellow-700 border-yellow-200';
      case 'Low': return 'bg-emerald-100 text-emerald-700 border-emerald-200';
      default: return 'bg-slate-100 text-slate-700 border-slate-200';
    }
  };

  const downloadExcel = () => {
    const exportData = filteredReports.map(r => ({
      Date: new Date(r.created_at).toLocaleDateString(),
      'Patient Name': (r.patient?.full_name || 'Unknown').replace(/\s*\((Patient|Doctor|Admin|patient|doctor|admin)\)/gi, ''),
      'Assigned Doctor': r.doctorName || 'Unassigned',
      Urgency: r.urgency,
      Department: r.department,
      Symptoms: r.symptoms,
      'AI Analysis/Disease': r.analysis || ''
    }));

    const worksheet = XLSX.utils.json_to_sheet(exportData);
    
    // Set column widths
    const colWidths = [
      { wch: 15 }, // Date
      { wch: 25 }, // Patient Name
      { wch: 15 }, // Urgency
      { wch: 20 }, // Department
      { wch: 50 }, // Symptoms
      { wch: 100 } // AI Analysis/Disease
    ];
    worksheet['!cols'] = colWidths;

    const workbook = XLSX.utils.book_new();
    XLSX.utils.book_append_sheet(workbook, worksheet, "Hospital Report");
    XLSX.writeFile(workbook, `hospital_report_${new Date().toISOString().split('T')[0]}.xlsx`);
  };

  const downloadPDF = () => {
    const doc = new jsPDF();
    doc.setFontSize(16);
    doc.text('Hospital Triage Report', 14, 20);
    
    doc.setFontSize(10);
    doc.text(`Generated on: ${new Date().toLocaleDateString()}`, 14, 30);
    doc.text(`Filters - Urgency: ${urgencyFilter}, Search: ${diseaseSearch || 'None'}`, 14, 36);

    let yPos = 50;
    filteredReports.forEach((report, index) => {
      if (yPos > 270) {
        doc.addPage();
        yPos = 20;
      }
      doc.setFontSize(11);
      doc.setFont('helvetica', 'bold');
      const patName = (report.patient?.full_name || 'Unknown').replace(/\s*\((Patient|Doctor|Admin|patient|doctor|admin)\)/gi, '');
      doc.text(`${index + 1}. Patient: ${patName} - Date: ${new Date(report.created_at).toLocaleDateString()}`, 14, yPos);
      yPos += 7;
      
      doc.setFontSize(10);
      doc.setFont('helvetica', 'normal');
      doc.text(`Urgency: ${report.urgency} | Department: ${report.department} | Doctor: ${report.doctorName}`, 14, yPos);
      yPos += 7;

      doc.text('Symptoms:', 14, yPos);
      const splitSymptoms = doc.splitTextToSize(report.symptoms, 170);
      doc.text(splitSymptoms, 35, yPos);
      yPos += (splitSymptoms.length * 5) + 2;

      doc.text('Analysis:', 14, yPos);
      const splitAnalysis = doc.splitTextToSize(report.analysis || 'None', 170);
      doc.text(splitAnalysis, 35, yPos);
      yPos += (splitAnalysis.length * 5) + 10;
    });

    doc.save(`hospital_report_${new Date().toISOString().split('T')[0]}.pdf`);
  };

  const downloadIndividualPDF = (report: TriageData) => {
    const doc = new jsPDF();
    doc.setFontSize(16);
    doc.text('Individual Triage Report', 14, 20);
    doc.setFontSize(10);
    doc.text(`Generated on: ${new Date().toLocaleDateString()}`, 14, 30);
    
    let yPos = 45;
    doc.setFontSize(12);
    doc.setFont('helvetica', 'bold');
    const patName = (report.patient?.full_name || 'Unknown').replace(/\s*\((Patient|Doctor|Admin|patient|doctor|admin)\)/gi, '');
    doc.text(`Patient: ${patName}`, 14, yPos);
    yPos += 7;
    doc.setFontSize(10);
    doc.setFont('helvetica', 'normal');
    doc.text(`Date: ${new Date(report.created_at).toLocaleString()}`, 14, yPos);
    yPos += 7;
    doc.text(`Assigned Doctor: ${report.doctorName}`, 14, yPos);
    yPos += 7;
    doc.text(`Urgency: ${report.urgency} | Department: ${report.department}`, 14, yPos);
    yPos += 12;

    doc.setFont('helvetica', 'bold');
    doc.text('Symptoms:', 14, yPos);
    doc.setFont('helvetica', 'normal');
    const splitSymptoms = doc.splitTextToSize(report.symptoms, 170);
    doc.text(splitSymptoms, 35, yPos);
    yPos += (splitSymptoms.length * 5) + 5;

    doc.setFont('helvetica', 'bold');
    doc.text('Analysis:', 14, yPos);
    doc.setFont('helvetica', 'normal');
    const splitAnalysis = doc.splitTextToSize(report.analysis || 'None', 170);
    doc.text(splitAnalysis, 35, yPos);

    doc.save(`patient_report_${patName.replace(/\s/g, '_')}_${new Date(report.created_at).toISOString().split('T')[0]}.pdf`);
  };

  const handleDelete = async () => {
    if (!deleteId) return;
    const { error } = await supabase.from('triages').delete().eq('id', deleteId);
    if (!error) {
      setReports(prev => prev.filter(r => r.id !== deleteId));
    }
    setDeleteId(null);
  };

  return (
    <div className="p-6 md:p-8 max-w-7xl mx-auto flex-grow h-screen overflow-y-auto">
      <div className="flex flex-col md:flex-row items-start md:items-center justify-between mb-8 gap-4">
        <div>
          <h1 className="text-2xl font-bold text-slate-900 flex items-center gap-2">
            <FileText className="w-7 h-7 text-blue-600" />
            Hospital Reports
          </h1>
          <p className="text-slate-500 mt-1">Filter and export triage data for analytics.</p>
        </div>
        
        <div className="flex items-center gap-3">
          <button 
            onClick={downloadExcel}
            className="bg-emerald-600 hover:bg-emerald-700 text-white px-4 py-2.5 rounded-xl font-medium shadow-sm transition-colors flex items-center gap-2"
          >
            <Download className="w-5 h-5" />
            Excel
          </button>
          <button 
            onClick={downloadPDF}
            className="bg-red-600 hover:bg-red-700 text-white px-4 py-2.5 rounded-xl font-medium shadow-sm transition-colors flex items-center gap-2"
          >
            <FileDown className="w-5 h-5" />
            PDF Report
          </button>
        </div>
      </div>

      {/* Filters */}
      <div className="bg-white p-4 rounded-2xl border border-slate-200 shadow-sm mb-8 flex flex-col md:flex-row gap-4 items-center">
        
        <div className="relative flex-grow w-full">
          <Search className="w-5 h-5 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2" />
          <input 
            type="text" 
            placeholder="Search by Disease, Condition or Symptom (e.g. Flu, Cardiac)..." 
            value={diseaseSearch}
            onChange={(e) => setDiseaseSearch(e.target.value)}
            className="w-full pl-10 pr-4 py-2.5 bg-slate-50 border border-slate-200 rounded-xl focus:outline-none focus:border-blue-500 focus:ring-2 focus:ring-blue-500/20"
          />
        </div>

        <div className="flex items-center gap-2 w-full md:w-auto">
          <Filter className="w-5 h-5 text-slate-400" />
          <select 
            value={doctorFilter} 
            onChange={e => { setDoctorFilter(e.target.value); setCurrentPage(1); }}
            className="px-4 py-2.5 border border-slate-200 rounded-xl outline-none focus:border-blue-500 focus:ring-2 focus:ring-blue-500/20 bg-white w-full md:w-48 appearance-none"
          >
            {uniqueDoctors.map(doc => (
              <option key={doc} value={doc}>{doc === 'All' ? 'All Doctors' : doc}</option>
            ))}
          </select>
        </div>
        <div className="flex items-center gap-2 w-full md:w-auto">
          <Filter className="w-5 h-5 text-slate-400" />
          <select 
            value={urgencyFilter} 
            onChange={e => { setUrgencyFilter(e.target.value); setCurrentPage(1); }}
            className="px-4 py-2.5 border border-slate-200 rounded-xl outline-none focus:border-blue-500 focus:ring-2 focus:ring-blue-500/20 bg-white w-full md:w-48 appearance-none"
          >
            <option value="All">All Urgency Levels</option>
            <option value="Critical">Critical</option>
            <option value="High">High</option>
            <option value="Medium">Medium</option>
            <option value="Low">Low</option>
          </select>
        </div>
      </div>

      {/* Data Table */}
      <div className="bg-white rounded-2xl border border-slate-200 shadow-sm overflow-hidden">
        {loading ? (
          <div className="p-12 flex justify-center items-center">
            <div className="animate-spin w-8 h-8 border-4 border-blue-600 border-t-transparent rounded-full"></div>
          </div>
        ) : filteredReports.length === 0 ? (
          <div className="p-12 text-center flex flex-col items-center justify-center">
            <FileText className="w-12 h-12 text-slate-300 mb-4" />
            <h3 className="text-lg font-bold text-slate-900">No Reports Found</h3>
            <p className="text-slate-500 mt-1">Try adjusting your filters to see more results.</p>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left border-collapse">
              <thead>
                <tr className="bg-slate-50 border-b border-slate-200">
                  <th className="px-6 py-4 text-xs font-bold text-slate-500 uppercase tracking-wider">Date</th>
                  <th className="px-6 py-4 text-xs font-bold text-slate-500 uppercase tracking-wider">Patient</th>
                  <th className="px-6 py-4 text-xs font-bold text-slate-500 uppercase tracking-wider">Doctor</th>
                  <th className="px-6 py-4 text-xs font-bold text-slate-500 uppercase tracking-wider">Urgency</th>
                  <th className="px-6 py-4 text-xs font-bold text-slate-500 uppercase tracking-wider">Department</th>
                  <th className="px-6 py-4 text-xs font-bold text-slate-500 uppercase tracking-wider">Suspected Disease / Analysis</th>
                  <th className="px-6 py-4 text-xs font-bold text-slate-500 uppercase tracking-wider text-right">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {paginatedReports.map((report) => (
                  <tr key={report.id} className="hover:bg-slate-50/50 transition-colors">
                    <td className="px-6 py-4 text-sm font-medium text-slate-600 whitespace-nowrap">
                      {new Date(report.created_at).toLocaleDateString()}
                    </td>
                    <td className="px-6 py-4 text-sm whitespace-nowrap">
                      <div className="flex items-center gap-2">
                        <UserCircle className="w-5 h-5 text-slate-400" />
                        <span className="font-semibold text-slate-700">{(report.patient?.full_name || 'Unknown Patient').replace(/\s*\((Patient|Doctor|Admin|patient|doctor|admin)\)/gi, '')}</span>
                      </div>
                    </td>
                    <td className="px-6 py-4 text-sm whitespace-nowrap">
                      <span className="text-slate-600 font-medium">{report.doctorName}</span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className={`px-3 py-1 rounded-full text-xs font-bold border ${getUrgencyColor(report.urgency)} flex items-center gap-1 w-max`}>
                        <AlertTriangle className="w-3.5 h-3.5" />
                        {report.urgency}
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="flex items-center gap-1.5 text-sm font-medium text-slate-700">
                        <Activity className="w-4 h-4 text-blue-500" />
                        {report.department}
                      </div>
                    </td>
                    <td className="px-6 py-4 text-sm text-slate-600 max-w-md truncate">
                      {report.analysis || 'Analysis pending...'}
                    </td>
                    <td className="px-6 py-4 text-sm text-right whitespace-nowrap">
                      <button 
                        onClick={() => downloadIndividualPDF(report)}
                        className="p-2 text-slate-400 hover:text-red-600 hover:bg-red-50 rounded-lg transition-colors"
                        title="Download PDF"
                      >
                        <FileDown className="w-5 h-5" />
                      </button>
                      <button 
                        onClick={() => setDeleteId(report.id)}
                        className="p-2 text-slate-400 hover:text-red-600 hover:bg-red-50 rounded-lg transition-colors ml-1"
                        title="Delete Record"
                      >
                        <Trash2 className="w-5 h-5" />
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
        
        {/* Pagination Controls */}
        {totalPages > 1 && (
          <div className="bg-slate-50 px-6 py-4 border-t border-slate-100 flex items-center justify-between">
            <span className="text-sm text-slate-500">
              Showing <span className="font-medium">{(currentPage - 1) * ITEMS_PER_PAGE + 1}</span> to <span className="font-medium">{Math.min(currentPage * ITEMS_PER_PAGE, filteredReports.length)}</span> of <span className="font-medium">{filteredReports.length}</span> results
            </span>
            <div className="flex gap-2">
              <button 
                onClick={() => setCurrentPage(p => Math.max(1, p - 1))}
                disabled={currentPage === 1}
                className="px-3 py-1 text-sm font-medium border border-slate-200 rounded-lg hover:bg-white disabled:opacity-50 transition-colors bg-slate-100"
              >
                Previous
              </button>
              <button 
                onClick={() => setCurrentPage(p => Math.min(totalPages, p + 1))}
                disabled={currentPage === totalPages}
                className="px-3 py-1 text-sm font-medium border border-slate-200 rounded-lg hover:bg-white disabled:opacity-50 transition-colors bg-slate-100"
              >
                Next
              </button>
            </div>
          </div>
        )}
      </div>

      <ConfirmDialog
        isOpen={!!deleteId}
        title="Delete Triage Record"
        description="Are you sure you want to delete this triage record? This action cannot be undone and it will be permanently removed from the system."
        confirmText="Delete"
        onConfirm={handleDelete}
        onCancel={() => setDeleteId(null)}
      />
    </div>
  );
}
