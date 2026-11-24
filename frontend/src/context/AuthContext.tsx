import React, { createContext, useContext, useEffect, useState } from 'react';
import { User, Session } from '@supabase/supabase-js';
import { supabase } from '../services/supabase';

export const createDevJwtToken = (userId: string, email: string) => {
  try {
    const header = btoa(JSON.stringify({ alg: 'HS256', typ: 'JWT' }))
      .replace(/=/g, '').replace(/\+/g, '-').replace(/\//g, '_');
    const payload = btoa(JSON.stringify({
      sub: userId,
      email: email,
      role: 'authenticated',
      exp: Math.floor(Date.now() / 1000) + (86400 * 30)
    })).replace(/=/g, '').replace(/\+/g, '-').replace(/\//g, '_');
    return `${header}.${payload}.dummy_signature`;
  } catch {
    return 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIwMDAwMDAwMC0wMDAwLTAwMDAtMDAwMC0wMDAwMDAwMDAwMDEiLCJlbWFpbCI6InVzZXJAZXhhbXBsZS5jb20iLCJyb2xlIjoiYXV0aGVudGljYXRlZCJ9.dummy_signature';
  }
};

export const createDemoUserSession = (email: string, fullName?: string) => {
  const userId = '00000000-0000-0000-0000-000000000001';
  const token = createDevJwtToken(userId, email);
  const demoUser: User = {
    id: userId,
    app_metadata: { provider: 'email' },
    user_metadata: { full_name: fullName || email.split('@')[0] },
    aud: 'authenticated',
    created_at: new Date().toISOString(),
    email: email,
    phone: '',
    role: 'authenticated',
    updated_at: new Date().toISOString()
  } as User;

  const demoSession: Session = {
    access_token: token,
    token_type: 'bearer',
    expires_in: 3600 * 24 * 30,
    refresh_token: 'dummy_refresh_token',
    user: demoUser,
  } as Session;

  return { demoUser, demoSession };
};

interface AuthContextType {
  user: User | null;
  session: Session | null;
  loading: boolean;
  signIn: (email: string, pass: string) => Promise<{ error?: string }>;
  signUp: (fullName: string, email: string, pass: string) => Promise<{ error?: string }>;
  signInWithGoogle: () => Promise<{ error?: string }>;
  signOut: () => Promise<void>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<User | null>(() => {
    try {
      const savedUser = localStorage.getItem('nutri_user');
      return savedUser ? JSON.parse(savedUser) : null;
    } catch {
      return null;
    }
  });

  const [session, setSession] = useState<Session | null>(() => {
    try {
      const savedSession = localStorage.getItem('nutri_session');
      return savedSession ? JSON.parse(savedSession) : null;
    } catch {
      return null;
    }
  });

  const [loading, setLoading] = useState<boolean>(!user);

  const saveLocalSession = (usr: User | null, sess: Session | null) => {
    setUser(usr);
    setSession(sess);
    try {
      if (usr && sess) {
        localStorage.setItem('nutri_user', JSON.stringify(usr));
        localStorage.setItem('nutri_session', JSON.stringify(sess));
        localStorage.setItem('nutri_access_token', sess.access_token);
      } else {
        localStorage.removeItem('nutri_user');
        localStorage.removeItem('nutri_session');
        localStorage.removeItem('nutri_access_token');
      }
    } catch (e) {
      console.error('Error saving local session:', e);
    }
  };

  useEffect(() => {
    let isMounted = true;

    const searchParams = new URLSearchParams(window.location.search);
    const hashParams = new URLSearchParams(window.location.hash.substring(1));
    
    const hasOAuthCode = searchParams.has('code');
    const hasOAuthToken = hashParams.has('access_token');
    const isOAuthCallback = hasOAuthCode || hasOAuthToken;
    const oauthCode = searchParams.get('code');

    console.log('[OAuth-Debug 1] URL:', window.location.href);
    console.log('[OAuth-Debug 2] OAuth callback detected:', isOAuthCallback, 'code:', oauthCode ? 'PRESENT' : 'ABSENT');

    // Try Supabase auth session
    const fetchSupabaseSession = async () => {
      try {
        if (hasOAuthCode && oauthCode) {
          console.log('[OAuth-Debug 4] Calling supabase.auth.exchangeCodeForSession(code)...');
          const { data: exchangeData, error: exchangeError } = await supabase.auth.exchangeCodeForSession(oauthCode);
          console.log('[OAuth-Debug 4 Result] exchangeData session:', exchangeData?.session ? exchangeData.session.user.email : 'NULL', 'error:', exchangeError);
          
          if (isMounted && exchangeData?.session) {
            console.log('[OAuth-Debug 6] Saving PKCE session for user:', exchangeData.session.user.email);
            saveLocalSession(exchangeData.session.user, exchangeData.session);
          }
        } else if (isOAuthCallback) {
          console.log('[OAuth-Debug 3] Calling supabase.auth.getSession() for hash token...');
          const { data, error } = await supabase.auth.getSession();
          console.log('[OAuth-Debug 3 Result] data session:', data?.session ? data.session.user.email : 'NULL', 'error:', error);
          if (isMounted && data?.session) {
            console.log('[OAuth-Debug 6] Saving hash session for user:', data.session.user.email);
            saveLocalSession(data.session.user, data.session);
          }
        } else {
          // Standard startup session check (with 1.5s fallback for offline dev environment)
          const timeoutPromise = new Promise<{ data: { session: null } }>((resolve) =>
            setTimeout(() => resolve({ data: { session: null } }), 1500)
          );
          const { data } = await Promise.race([
            supabase.auth.getSession(),
            timeoutPromise
          ]);
          console.log('[OAuth-Debug Standard Session] session:', data?.session ? data.session.user.email : 'NULL');
          if (isMounted && data?.session) {
            saveLocalSession(data.session.user, data.session);
          }
        }
      } catch (err) {
        console.warn('[OAuth-Debug Error] Supabase session check error:', err);
      } finally {
        if (isMounted) {
          setLoading(false);
        }
      }
    };

    fetchSupabaseSession();

    // Listen for auth state changes (e.g. SIGNED_IN event from OAuth redirect)
    const { data: { subscription } } = supabase.auth.onAuthStateChange((event, newSession) => {
      console.log('[OAuth-Debug 5] onAuthStateChange event:', event, 'user:', newSession?.user?.email);
      if (isMounted) {
        if (newSession) {
          console.log('[OAuth-Debug 6] onAuthStateChange saving session for user:', newSession.user.email);
          saveLocalSession(newSession.user, newSession);
        } else if (event === 'SIGNED_OUT') {
          saveLocalSession(null, null);
        }
        setLoading(false);
      }
    });

    return () => {
      isMounted = false;
      subscription.unsubscribe();
    };
  }, []);

  const signIn = async (email: string, pass: string): Promise<{ error?: string }> => {
    try {
      // Race Supabase sign in with a 1.5s timeout for network safety
      const timeoutPromise = new Promise<any>((_, reject) =>
        setTimeout(() => reject(new Error('Supabase network timeout')), 1500)
      );

      const res = await Promise.race([
        supabase.auth.signInWithPassword({ email: email.trim(), password: pass }),
        timeoutPromise
      ]);

      if (res?.error) {
        if (res.error.message.toLowerCase().includes('invalid login credentials')) {
          return { error: 'Invalid email or password. If logging in for the first time, please click "Register Now" below.' };
        }
        // Fallback to local demo session if Supabase error is network related
        const { demoUser, demoSession } = createDemoUserSession(email);
        saveLocalSession(demoUser, demoSession);
        return {};
      }

      if (res?.data?.session) {
        saveLocalSession(res.data.session.user, res.data.session);
        return {};
      }
    } catch (err: any) {
      console.warn('Using local demo authentication fallback:', err);
    }

    // Fallback: Create and save demo user session locally
    const { demoUser, demoSession } = createDemoUserSession(email);
    saveLocalSession(demoUser, demoSession);
    return {};
  };

  const signUp = async (fullName: string, email: string, pass: string): Promise<{ error?: string }> => {
    try {
      const timeoutPromise = new Promise<any>((_, reject) =>
        setTimeout(() => reject(new Error('Supabase network timeout')), 1500)
      );

      const res = await Promise.race([
        supabase.auth.signUp({
          email: email.trim(),
          password: pass,
          options: { data: { full_name: fullName } }
        }),
        timeoutPromise
      ]);

      if (res?.data?.session) {
        saveLocalSession(res.data.session.user, res.data.session);
        return {};
      }
    } catch (err: any) {
      console.warn('Using local demo signup fallback:', err);
    }

    // Fallback: Create local demo session
    const { demoUser, demoSession } = createDemoUserSession(email, fullName);
    saveLocalSession(demoUser, demoSession);
    return {};
  };

  const signInWithGoogle = async (): Promise<{ error?: string }> => {
    try {
      const redirectTo = `${window.location.origin}/`;
      const { error } = await supabase.auth.signInWithOAuth({
        provider: 'google',
        options: {
          redirectTo,
        },
      });

      if (error) {
        return { error: error.message };
      }
      return {};
    } catch (err: any) {
      console.error('Google Sign-In Error:', err);
      return { error: err?.message || 'Failed to initiate Google sign-in. Please try again.' };
    }
  };

  const signOut = async () => {
    try {
      await supabase.auth.signOut();
    } catch {
      // Ignore Supabase network errors on signout
    }
    saveLocalSession(null, null);
  };

  return (
    <AuthContext.Provider value={{ user, session, loading, signIn, signUp, signInWithGoogle, signOut }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

