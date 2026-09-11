import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { Heart, Mail, Lock, ArrowRight, AlertCircle } from 'lucide-react';

export const LoginPage: React.FC = () => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const { signIn } = useAuth();
  const navigate = useNavigate();

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    const res = await signIn(email.trim(), password);

    if (res?.error) {
      setError(res.error);
      setLoading(false);
    } else {
      navigate('/');
    }
  };

  return (
    <div style={{
      minHeight: '100vh',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      padding: '1.5rem',
      background: 'var(--bg-page)'
    }}>
      <div className="app-card" style={{
        width: '100%',
        maxWidth: '420px',
        padding: '2.5rem'
      }}>
        {/* Header */}
        <div style={{ textAlign: 'center', marginBottom: '2rem' }}>
          <div style={{
            display: 'inline-flex',
            background: 'var(--bg-mint)',
            padding: '0.75rem',
            borderRadius: '12px',
            color: 'var(--primary-emerald)',
            marginBottom: '1rem'
          }}>
            <Heart size={32} />
          </div>
          <h1 style={{ fontSize: '1.6rem', fontWeight: 700, color: 'var(--text-main)', marginBottom: '0.4rem' }}>
            Welcome Back
          </h1>
          <p style={{ fontSize: '0.9rem', color: 'var(--text-muted)' }}>
            Sign in to access your Health Profile & Food Diary
          </p>
        </div>

        {error && (
          <div className="alert-error" style={{ display: 'flex', flexDirection: 'column', alignItems: 'flex-start', gap: '0.4rem' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', fontWeight: 600 }}>
              <AlertCircle size={18} /> Login Error
            </div>
            <span style={{ fontSize: '0.85rem' }}>{error}</span>
          </div>
        )}

        <form onSubmit={handleLogin}>
          <div className="form-group">
            <label style={{ display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
              <Mail size={14} /> Email Address
            </label>
            <input
              type="email"
              className="input-field"
              placeholder="name@example.com"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
            />
          </div>

          <div className="form-group">
            <label style={{ display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
              <Lock size={14} /> Password
            </label>
            <input
              type="password"
              className="input-field"
              placeholder="••••••••"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
            />
          </div>

          <button
            type="submit"
            className="btn-primary"
            disabled={loading}
            style={{ width: '100%', marginTop: '0.75rem' }}
          >
            {loading ? 'Authenticating...' : (
              <>Sign In <ArrowRight size={18} /></>
            )}
          </button>
        </form>

        <div style={{
          textAlign: 'center',
          marginTop: '1.75rem',
          fontSize: '0.875rem',
          color: 'var(--text-muted)'
        }}>
          Don't have an account?{' '}
          <Link to="/register" style={{ color: 'var(--primary-emerald)', fontWeight: 600, textDecoration: 'none' }}>
            Register Now
          </Link>
        </div>
      </div>
    </div>
  );
};
