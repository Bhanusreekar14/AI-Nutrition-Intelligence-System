import React from 'react';
import { Navigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { Activity } from 'lucide-react';

export const ProtectedRoute: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const { user, loading } = useAuth();

  console.log('[OAuth-Debug 7] ProtectedRoute evaluation - loading:', loading, 'user:', user?.email, 'URL:', window.location.href);

  if (loading) {
    return (
      <div style={{
        minHeight: '100vh',
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'center',
        gap: '1rem',
        color: 'var(--text-muted)'
      }}>
        <Activity size={36} className="animate-fade-in" style={{ color: 'var(--primary-emerald)' }} />
        <p>Loading NutriIntelligence...</p>
      </div>
    );
  }

  if (!user) {
    console.log('[OAuth-Debug 9] ProtectedRoute redirecting to /login because user is null. Current URL:', window.location.href);
    return <Navigate to="/login" replace />;
  }

  return <>{children}</>;
};
