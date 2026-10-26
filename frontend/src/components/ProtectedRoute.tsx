import { Navigate, Outlet } from 'react-router-dom';
import { useAuth } from '../hooks/useAuth';
import { Spinner } from '@/components/ui/spinner';

export default function ProtectedRoute({ hrOnly = false, seekerOnly = false }: { hrOnly?: boolean; seekerOnly?: boolean }) {
  const { isAuthenticated, isHR, loading } = useAuth();

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <Spinner className="size-8 text-primary" />
      </div>
    );
  }

  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }

  if ((hrOnly && !isHR) || (seekerOnly && isHR)) {
    return <Navigate to="/" replace />;
  }

  return <Outlet />;
}
