import { useState } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import Auth from './pages/Auth';
<<<<<<< HEAD
import UpdatePassword from './pages/UpdatePassword';
=======
>>>>>>> team/main
import PatientDashboard from './pages/PatientDashboard';
import SymptomChecker from './pages/SymptomChecker';
import TriageResult from './pages/TriageResult';
import DoctorDashboard from './pages/DoctorDashboard';
import AdminDashboard from './pages/AdminDashboard';
import AdminReports from './pages/AdminReports';
import AdminCreateDoctor from './pages/AdminCreateDoctor';
<<<<<<< HEAD
import AdminUserList from './pages/AdminUserList';
=======
>>>>>>> team/main
import Settings from './pages/Settings';
import Sidebar from './components/Sidebar';
import { Menu } from 'lucide-react';

function App() {
  const [isSidebarOpen, setIsSidebarOpen] = useState(false);

  return (
    <Router>
      <div className="flex h-screen overflow-hidden bg-slate-50 text-slate-900">
        <Sidebar isOpen={isSidebarOpen} setIsOpen={setIsSidebarOpen} />
        
        <main className="flex-1 flex flex-col h-screen overflow-hidden">
          {/* Mobile Header */}
          <div className="md:hidden flex items-center justify-between p-4 bg-white border-b border-slate-200">
<<<<<<< HEAD
            <h1 className="text-lg font-bold text-blue-600">VitalGate AI</h1>
=======
            <h1 className="text-lg font-bold text-blue-600">CareTaker AI</h1>
>>>>>>> team/main
            <button 
              onClick={() => setIsSidebarOpen(true)}
              className="p-2 text-slate-600 hover:bg-slate-100 rounded-lg"
            >
              <Menu className="w-6 h-6" />
            </button>
          </div>

          <div className="flex-1 overflow-y-auto">
          <Routes>
            <Route path="/" element={<Navigate to="/auth" replace />} />
            <Route path="/auth" element={<Auth />} />
<<<<<<< HEAD
            <Route path="/update-password" element={<UpdatePassword />} />
=======
>>>>>>> team/main
            <Route path="/dashboard" element={<PatientDashboard />} />
            <Route path="/chat" element={<SymptomChecker />} />
            <Route path="/result" element={<TriageResult />} />
            <Route path="/doctor" element={<DoctorDashboard />} />
            <Route path="/doctor/schedule" element={<DoctorDashboard />} />
            <Route path="/admin" element={<AdminDashboard />} />
            <Route path="/admin/reports" element={<AdminReports />} />
            <Route path="/admin/create-doctor" element={<AdminCreateDoctor />} />
<<<<<<< HEAD
            <Route path="/admin/users" element={<AdminUserList />} />
=======
>>>>>>> team/main
            <Route path="/settings" element={<Settings />} />
          </Routes>
          </div>
        </main>
      </div>
    </Router>
  );
}

export default App;
