import { useState, useEffect } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import { AlertTriangle, ShieldCheck, CheckCircle2, ChevronRight, Activity, Calendar, Clock, UserRound } from 'lucide-react';
import { supabase } from '../lib/supabase';

export default function TriageResult() {
  const location = useLocation();
  const navigate = useNavigate();
  const [showToast, setShowToast] = useState(false);
  const [isBooking, setIsBooking] = useState(false);
  const [doctors, setDoctors] = useState<any[]>([]);
  const [selectedDoctor, setSelectedDoctor] = useState<string>('');
  const [bookingDate, setBookingDate] = useState('');
  const [bookingTime, setBookingTime] = useState('');
  const [patientId, setPatientId] = useState<string | null>(null);

  const triageData = location.state?.triageData || {
    triage_id: null,
    urgency_level: "Medium",
    recommended_department: "General Practice",
    ai_explanation: "No specific triage data found. Please complete the symptom checker for personalized results."
  };

  useEffect(() => {
    supabase.auth.getUser().then(({ data: { user } }) => {
      if (user) setPatientId(user.id);
    });
  }, []);

  const handleStartBooking = async () => {
    setIsBooking(true);
    // Fetch available doctors
    const { data } = await supabase.from('users').select('id, full_name').eq('role', 'doctor');
    const docList = data || [];
    setDoctors(docList);
    if (docList.length > 0) {
      setSelectedDoctor(docList[0].id);
    }
  };

  const handleConfirmBooking = async () => {
    if (!selectedDoctor || !bookingDate || !bookingTime || !patientId) return;

    // Create appointment
    const formattedSlot = `${bookingDate}: ${bookingTime}`;
    const { error: apptError } = await supabase.from('appointments').insert({
      patient_id: patientId,
      doctor_id: selectedDoctor,
      triage_report_id: triageData.triage_id || null,
      department: triageData.recommended_department || 'General Practice',
      appointment_time: formattedSlot,
      status: 'scheduled'
    });

    if (!apptError) {
      // Update triage status if triage_id exists
      if (triageData.triage_id) {
        await supabase.from('triages').update({ status: 'scheduled' }).eq('id', triageData.triage_id);
      }

      setIsBooking(false);
      setShowToast(true);
      setTimeout(() => {
        setShowToast(false);
        navigate('/dashboard');
      }, 2500);
    } else {
      console.error("Booking error:", apptError);
      alert("Failed to book appointment: " + apptError.message);
    }
  };

  const getUrgencyStyles = (level: string) => {
    const l = level?.toLowerCase() || '';
    if (l.includes('high')) return 'bg-red-100 text-red-700 border-red-200';
    if (l.includes('low')) return 'bg-emerald-100 text-emerald-700 border-emerald-200';
    return 'bg-amber-100 text-amber-700 border-amber-200';
  };

  return (
    <div className="flex-grow flex items-center justify-center p-6 bg-slate-50">

      {showToast && (
        <div className="fixed top-24 right-6 bg-emerald-500 text-white px-6 py-4 rounded-xl shadow-lg flex items-center gap-3 animate-in slide-in-from-top-4 z-50">
          <CheckCircle2 className="w-5 h-5" />
          <span className="font-medium">Success: Appointment Requested!</span>
        </div>
      )}

      <div className="w-full max-w-2xl bg-white rounded-3xl shadow-sm border border-slate-200 p-8 md:p-12 text-center">

        <div className="flex justify-center mb-6">
          <div className={`inline-flex items-center gap-2 px-5 py-2.5 rounded-full border ${getUrgencyStyles(triageData.urgency_level)}`}>
            <AlertTriangle className="w-5 h-5" />
            <span className="font-bold tracking-wide">{triageData.urgency_level} Urgency</span>
          </div>
        </div>

        <h1 className="text-3xl md:text-4xl font-bold text-slate-900 mb-2">
          {triageData.suspected_condition || "Assessment Complete"}
        </h1>
        <p className="text-slate-500 font-medium mb-10 flex items-center justify-center gap-2">
          <ShieldCheck className="w-4 h-4" />
          Recommended Department: {triageData.recommended_department}
        </p>

        <div className="bg-slate-50 rounded-2xl p-6 md:p-8 text-left border border-slate-100 mb-10">
          <div className="flex items-center gap-2 mb-3">
            <Activity className="w-5 h-5 text-blue-600" />
            <h3 className="font-semibold text-slate-900">Clinical Reasoning</h3>
          </div>
          <p className="text-slate-600 leading-relaxed whitespace-pre-wrap">
            {triageData.ai_explanation}
          </p>
        </div>

        {isBooking ? (
          <div className="bg-white border border-slate-200 rounded-2xl p-6 mb-8 text-left animate-in slide-in-from-bottom-4">
            <h3 className="font-bold text-slate-900 mb-4 flex items-center gap-2">
              <Calendar className="w-5 h-5 text-blue-600" />
              Schedule Appointment
            </h3>

            <div className="space-y-4 mb-6">
              <div>
                <label className="block text-sm font-medium text-slate-700 mb-1">Available Doctors</label>
                <div className="relative">
                  <UserRound className="absolute left-3 top-3 w-5 h-5 text-slate-400" />
                  <select
                    value={selectedDoctor}
                    onChange={(e) => setSelectedDoctor(e.target.value)}
                    className="w-full pl-10 pr-4 py-3 bg-slate-50 border border-slate-200 rounded-xl outline-none focus:ring-2 focus:ring-blue-500"
                  >
                    {doctors.map(doc => (
                      <option key={doc.id} value={doc.id}>
                        {doc.full_name?.startsWith('Dr.') ? doc.full_name : `Dr. ${doc.full_name || doc.email?.split('@')[0] || 'Available Doctor'}`}
                      </option>
                    ))}
                  </select>
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium text-slate-700 mb-2">Select Date & Time</label>
                <div className="flex flex-col sm:flex-row gap-3">
                  <div className="relative flex-1">
                    <Calendar className="absolute left-3 top-3.5 w-5 h-5 text-slate-400 pointer-events-none" />
                    <input 
                      type="date" 
                      value={bookingDate} 
                      onChange={(e) => setBookingDate(e.target.value)} 
                      className="w-full pl-10 pr-4 py-3 bg-slate-50 border border-slate-200 rounded-xl outline-none focus:ring-2 focus:ring-blue-500 font-medium text-slate-700" 
                    />
                  </div>
                  <div className="relative flex-1">
                    <Clock className="absolute left-3 top-3.5 w-5 h-5 text-slate-400 pointer-events-none" />
                    <input 
                      type="time" 
                      value={bookingTime} 
                      onChange={(e) => setBookingTime(e.target.value)} 
                      className="w-full pl-10 pr-4 py-3 bg-slate-50 border border-slate-200 rounded-xl outline-none focus:ring-2 focus:ring-blue-500 font-medium text-slate-700" 
                    />
                  </div>
                </div>
              </div>
            </div>

            <div className="flex items-center gap-3">
              <button
                onClick={() => setIsBooking(false)}
                className="flex-1 py-3 bg-white border border-slate-200 text-slate-700 rounded-xl font-medium"
              >
                Cancel
              </button>
              <button
                onClick={handleConfirmBooking}
                disabled={!bookingDate || !bookingTime}
                className="flex-1 py-3 bg-blue-600 hover:bg-blue-700 text-white rounded-xl font-medium disabled:opacity-50 transition-colors"
              >
                Confirm Booking
              </button>
            </div>
          </div>
        ) : (
          <div className="flex flex-col sm:flex-row items-center justify-center gap-4">
            <button
              onClick={handleStartBooking}
              className="w-full sm:w-auto px-8 py-4 bg-blue-600 hover:bg-blue-700 text-white rounded-xl font-semibold shadow-md shadow-blue-500/20 transition-all flex items-center justify-center gap-2"
            >
              Book Appointment
              <ChevronRight className="w-5 h-5" />
            </button>

            <button
              onClick={() => navigate('/dashboard')}
              className="w-full sm:w-auto px-8 py-4 bg-white hover:bg-slate-50 text-slate-700 border border-slate-200 rounded-xl font-semibold transition-all"
            >
              Return to Dashboard
            </button>
          </div>
        )}
      </div>
    </div>
  );
}

