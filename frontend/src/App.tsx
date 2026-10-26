import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { AuthProvider } from './hooks/useAuth';
import ProtectedRoute from './components/ProtectedRoute';
import Layout from './components/Layout';
import Login from './pages/Login';
import Register from './pages/Register';
import Dashboard from './pages/Dashboard';
import Resumes from './pages/Resumes';
import ResumeDetail from './pages/ResumeDetail';
import Jobs from './pages/Jobs';
import JobDetail from './pages/JobDetail';
import Matches from './pages/Matches';
import MatchDetail from './pages/MatchDetail';
import CareerJobs from './pages/CareerJobs';
import CareerJobDetail from './pages/CareerJobDetail';
import Career from './pages/Career';
import { Toaster } from '@/components/ui/sonner';

export default function App() {
  return (
    <BrowserRouter>
      <AuthProvider>
        <Routes>
          <Route path="/login" element={<Login />} />
          <Route path="/register" element={<Register />} />
          <Route element={<ProtectedRoute />}>
            <Route element={<Layout />}>
              <Route path="/" element={<Dashboard />} />
              <Route path="/resumes" element={<Resumes />} />
              <Route path="/resumes/:id" element={<ResumeDetail />} />
              <Route element={<ProtectedRoute seekerOnly />}>
                <Route path="/opportunities" element={<CareerJobs />} />
                <Route path="/opportunities/:id" element={<CareerJobDetail />} />
                <Route path="/career" element={<Career />} />
              </Route>
              <Route element={<ProtectedRoute hrOnly />}>
                <Route path="/jobs" element={<Jobs />} />
                <Route path="/jobs/:id" element={<JobDetail />} />
                <Route path="/matches" element={<Matches />} />
                <Route path="/matches/:id" element={<MatchDetail />} />
              </Route>
            </Route>
          </Route>
        </Routes>
        <Toaster />
      </AuthProvider>
    </BrowserRouter>
  );
}
