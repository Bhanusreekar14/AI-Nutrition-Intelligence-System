import React, { useState } from 'react';
import { Link, useNavigate, useLocation } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { 
  Home, 
  User as UserIcon, 
  BookOpen, 
  Activity, 
  FileText, 
  Sparkles,
  LogOut, 
  Menu, 
  X,
  Heart
} from 'lucide-react';

export const Navbar: React.FC = () => {
  const { user, signOut } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  const handleSignOut = async () => {
    await signOut();
    navigate('/login');
  };

  if (!user) return null;

  const isActive = (path: string) => {
    if (path === '/' && location.pathname === '/') return true;
    if (path !== '/' && location.pathname.startsWith(path)) return true;
    return false;
  };

  const navItems = [
    { label: 'Home', path: '/', icon: <Home size={18} /> },
    { label: 'Profile', path: '/profile', icon: <UserIcon size={18} /> },
    { label: 'Food Diary', path: '/diary', icon: <BookOpen size={18} /> },
    { label: 'Symptoms', path: '/symptoms', icon: <Activity size={18} /> },
    { label: 'Blood Test', path: '/blood-tests', icon: <FileText size={18} /> },
    { label: 'AI Predictor', path: '/predict', icon: <Sparkles size={18} /> },
  ];

  return (
    <header style={{
      background: '#ffffff',
      borderBottom: '1px solid var(--border-subtle)',
      position: 'sticky',
      top: 0,
      zIndex: 50,
      boxShadow: '0 1px 3px rgba(0,0,0,0.03)'
    }}>
      <div className="app-container" style={{
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        paddingTop: '0.75rem',
        paddingBottom: '0.75rem'
      }}>
        {/* Brand Logo */}
        <Link to="/" style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', textDecoration: 'none' }}>
          <div style={{
            background: 'var(--bg-mint)',
            padding: '0.4rem',
            borderRadius: '8px',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            color: 'var(--primary-emerald)'
          }}>
            <Heart size={22} />
          </div>
          <div>
            <span style={{ fontSize: '1.15rem', fontWeight: 700, color: 'var(--text-main)' }}>
              Nutri<span style={{ color: 'var(--primary-emerald)' }}>Health</span>
            </span>
          </div>
        </Link>

        {/* Desktop Navigation Links */}
        <nav className="desktop-nav" style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
          {navItems.map((item) => {
            const active = isActive(item.path);
            return (
              <Link
                key={item.path}
                to={item.path}
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: '0.4rem',
                  textDecoration: 'none',
                  fontSize: '0.9rem',
                  fontWeight: active ? 600 : 500,
                  color: active ? 'var(--primary-emerald)' : 'var(--text-muted)',
                  padding: '0.5rem 0.85rem',
                  borderRadius: 'var(--radius-sm)',
                  background: active ? 'var(--bg-mint)' : 'transparent',
                  transition: 'all 0.2s ease'
                }}
              >
                {item.icon} {item.label}
              </Link>
            );
          })}
        </nav>

        {/* User Info & Actions */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
          <span style={{ fontSize: '0.85rem', color: 'var(--text-muted)', display: 'none' }} className="desktop-email">
            {user.email}
          </span>
          <button
            onClick={handleSignOut}
            className="btn-secondary"
            style={{ padding: '0.4rem 0.75rem', fontSize: '0.85rem' }}
          >
            <LogOut size={16} /> Logout
          </button>

          {/* Mobile Menu Toggle Button */}
          <button
            onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
            style={{
              background: 'transparent',
              border: 'none',
              cursor: 'pointer',
              color: 'var(--text-main)',
              display: 'none'
            }}
            className="mobile-toggle"
          >
            {mobileMenuOpen ? <X size={24} /> : <Menu size={24} />}
          </button>
        </div>
      </div>

      {/* Mobile Navigation Dropdown */}
      {mobileMenuOpen && (
        <div style={{
          background: '#ffffff',
          borderTop: '1px solid var(--border-subtle)',
          padding: '1rem 1.5rem',
          display: 'flex',
          flexDirection: 'column',
          gap: '0.5rem'
        }}>
          {navItems.map((item) => (
            <Link
              key={item.path}
              to={item.path}
              onClick={() => setMobileMenuOpen(false)}
              style={{
                display: 'flex',
                alignItems: 'center',
                gap: '0.6rem',
                textDecoration: 'none',
                fontSize: '0.95rem',
                fontWeight: 500,
                color: isActive(item.path) ? 'var(--primary-emerald)' : 'var(--text-main)',
                padding: '0.6rem',
                borderRadius: 'var(--radius-sm)',
                background: isActive(item.path) ? 'var(--bg-mint)' : 'transparent'
              }}
            >
              {item.icon} {item.label}
            </Link>
          ))}
        </div>
      )}

      <style>{`
        @media (max-width: 768px) {
          .desktop-nav { display: none !important; }
          .mobile-toggle { display: block !important; }
        }
      `}</style>
    </header>
  );
};
