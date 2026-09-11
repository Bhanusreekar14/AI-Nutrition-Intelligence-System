import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Navbar } from '../components/Navbar';
import { getMyHealthProfile, saveHealthProfile } from '../services/api';
import { HealthProfile } from '../types';
import { 
  UserCheck, 
  Save, 
  CheckCircle, 
  AlertCircle, 
  Edit3, 
  ArrowRight, 
  Home, 
  Eye
} from 'lucide-react';

export const HealthProfilePage: React.FC = () => {
  const navigate = useNavigate();
  const [step, setStep] = useState<'form' | 'review' | 'confirmation'>('form');

  const [profile, setProfile] = useState<HealthProfile>({
    age: 21,
    gender: 'female',
    height_cm: 165,
    weight_kg: 58,
    activity_level: 'moderately_active',
    dietary_preference: 'vegetarian',
    health_goals: ['Improve Nutrition'],
    allergies_intolerances: [],
    medical_conditions: [],
    health_goal: 'Improve Nutrition',
    target_value: 'Improve daily nutrition',
    target_unit: '',
    target_period: 'This Month',
  });

  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  const dietaryOptions = ['Vegetarian', 'Vegan', 'Gluten-free', 'Lactose-free', 'Nut-free', 'Other'];

  useEffect(() => {
    let isMounted = true;
    const timer = setTimeout(() => {
      if (isMounted) setLoading(false);
    }, 1500);

    fetchProfile().finally(() => {
      if (isMounted) setLoading(false);
    });

    return () => {
      isMounted = false;
      clearTimeout(timer);
    };
  }, []);

  const fetchProfile = async () => {
    try {
      const data = await getMyHealthProfile();
      if (data) {
        setProfile({
          ...data,
          medical_conditions: data.medical_conditions || [],
          allergies_intolerances: data.allergies_intolerances || [],
          health_goals: data.health_goals || [],
        });
      }
    } catch (err: any) {
      console.log('No existing health profile found, using default form');
    }
  };

  const handleCheckboxToggle = (restriction: string) => {
    const list = profile.allergies_intolerances || [];
    if (list.includes(restriction)) {
      setProfile({ ...profile, allergies_intolerances: list.filter(r => r !== restriction) });
    } else {
      setProfile({ ...profile, allergies_intolerances: [...list, restriction] });
    }
  };

  const handleGoToReview = (e: React.FormEvent) => {
    e.preventDefault();
    setErrorMessage(null);

    // Validation
    if (!profile.age || profile.age <= 0) {
      setErrorMessage('Please enter your age.');
      return;
    }
    if (!profile.height_cm || profile.height_cm <= 0) {
      setErrorMessage('Please enter a valid height.');
      return;
    }
    if (!profile.weight_kg || profile.weight_kg <= 0) {
      setErrorMessage('Please enter a valid weight.');
      return;
    }

    setStep('review');
  };

  const handleSubmitProfile = async () => {
    try {
      setSaving(true);
      setErrorMessage(null);
      const saved = await saveHealthProfile(profile);
      setProfile(saved);
      setStep('confirmation');
    } catch (err: any) {
      setErrorMessage(err.response?.data?.detail || 'Failed to save health profile.');
    } finally {
      setSaving(false);
    }
  };

  return (
    <div style={{ minHeight: '100vh', background: 'var(--bg-page)' }}>
      <Navbar />

      <main className="app-container">
        {/* Header */}
        <div style={{ marginBottom: '1.75rem' }}>
          <h1 style={{ fontSize: '1.75rem', fontWeight: 700, color: 'var(--text-main)', display: 'flex', alignItems: 'center', gap: '0.6rem' }}>
            <UserCheck size={26} color="var(--primary-emerald)" /> User Health Profile
          </h1>
          <p style={{ color: 'var(--text-muted)', fontSize: '0.95rem' }}>
            Set up your biometrics, dietary preferences, and personal health goals.
          </p>
        </div>

        {errorMessage && (
          <div className="alert-error">
            <AlertCircle size={20} />
            <span>{errorMessage}</span>
          </div>
        )}

        {loading ? (
          <div className="app-card" style={{ padding: '3rem', textAlign: 'center', color: 'var(--text-muted)' }}>
            Loading health profile...
          </div>
        ) : (
          <>
            {/* STEP 1: FORM INPUT */}
            {step === 'form' && (
              <form onSubmit={handleGoToReview} className="app-card" style={{ padding: '2rem' }}>
                <h2 style={{ fontSize: '1.2rem', fontWeight: 700, marginBottom: '1.5rem', color: 'var(--text-main)', borderBottom: '1px solid var(--border-subtle)', paddingBottom: '0.5rem' }}>
                  Basic & Personal Details
                </h2>

                <div className="grid-2">
                  <div className="form-group">
                    <label>Age (years)</label>
                    <input
                      type="number"
                      className="input-field"
                      placeholder="e.g. 21"
                      value={profile.age || ''}
                      onChange={(e) => setProfile({ ...profile, age: parseInt(e.target.value) || 0 })}
                      min={1}
                      max={120}
                      required
                    />
                  </div>

                  <div className="form-group">
                    <label>Gender</label>
                    <select
                      className="input-field"
                      value={profile.gender}
                      onChange={(e) => setProfile({ ...profile, gender: e.target.value as any })}
                    >
                      <option value="female">Female</option>
                      <option value="male">Male</option>
                      <option value="other">Other</option>
                      <option value="prefer_not_to_say">Prefer not to say</option>
                    </select>
                  </div>
                </div>

                <div className="grid-2">
                  <div className="form-group">
                    <label>Height (cm)</label>
                    <input
                      type="number"
                      step="0.1"
                      className="input-field"
                      placeholder="e.g. 165"
                      value={profile.height_cm || ''}
                      onChange={(e) => setProfile({ ...profile, height_cm: parseFloat(e.target.value) || 0 })}
                      required
                    />
                  </div>

                  <div className="form-group">
                    <label>Weight (kg)</label>
                    <input
                      type="number"
                      step="0.1"
                      className="input-field"
                      placeholder="e.g. 58"
                      value={profile.weight_kg || ''}
                      onChange={(e) => setProfile({ ...profile, weight_kg: parseFloat(e.target.value) || 0 })}
                      required
                    />
                  </div>
                </div>

                <div className="form-group">
                  <label>Medical Conditions</label>
                  <textarea
                    className="input-field"
                    placeholder="Enter any existing medical conditions or notes (e.g. Diabetes, Anemia, Hypertension)..."
                    value={profile.medical_conditions ? profile.medical_conditions.join(', ') : ''}
                    onChange={(e) => setProfile({
                      ...profile,
                      medical_conditions: e.target.value.split(',').map(s => s.trim()).filter(Boolean)
                    })}
                  />
                </div>

                <div className="form-group" style={{ marginTop: '1.25rem' }}>
                  <label style={{ marginBottom: '0.6rem' }}>Dietary Restrictions</label>
                  <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(140px, 1fr))', gap: '0.75rem' }}>
                    {dietaryOptions.map((option) => {
                      const checked = (profile.allergies_intolerances || []).includes(option);
                      return (
                        <label
                          key={option}
                          style={{
                            display: 'flex',
                            alignItems: 'center',
                            gap: '0.5rem',
                            padding: '0.6rem 0.85rem',
                            background: checked ? 'var(--bg-mint)' : '#f8fafc',
                            border: `1px solid ${checked ? 'var(--border-mint)' : 'var(--border-subtle)'}`,
                            borderRadius: 'var(--radius-sm)',
                            cursor: 'pointer',
                            fontSize: '0.9rem',
                            fontWeight: checked ? 600 : 400
                          }}
                        >
                          <input
                            type="checkbox"
                            checked={checked}
                            onChange={() => handleCheckboxToggle(option)}
                          />
                          {option}
                        </label>
                      );
                    })}
                  </div>
                </div>

                <h2 style={{ fontSize: '1.2rem', fontWeight: 700, marginTop: '2rem', marginBottom: '1.5rem', color: 'var(--text-main)', borderBottom: '1px solid var(--border-subtle)', paddingBottom: '0.5rem' }}>
                  Health Goal & Target
                </h2>

                <div className="grid-3">
                  <div className="form-group">
                    <label>Your Health Goal</label>
                    <select
                      className="input-field"
                      value={profile.health_goal || 'Improve Nutrition'}
                      onChange={(e) => setProfile({ ...profile, health_goal: e.target.value })}
                    >
                      <option value="Improve Nutrition">Improve Nutrition</option>
                      <option value="General Health">General Health</option>
                      <option value="Weight Management">Weight Management</option>
                      <option value="Increase Energy">Increase Energy</option>
                      <option value="Other">Other</option>
                    </select>
                  </div>

                  <div className="form-group">
                    <label>Target</label>
                    <input
                      type="text"
                      className="input-field"
                      placeholder="e.g. Improve my daily nutrition or 60 kg"
                      value={profile.target_value || ''}
                      onChange={(e) => setProfile({ ...profile, target_value: e.target.value })}
                    />
                  </div>

                  <div className="form-group">
                    <label>Target Period</label>
                    <select
                      className="input-field"
                      value={profile.target_period || 'This Month'}
                      onChange={(e) => setProfile({ ...profile, target_period: e.target.value })}
                    >
                      <option value="This Month">This Month</option>
                      <option value="3 Months">3 Months</option>
                      <option value="6 Months">6 Months</option>
                    </select>
                  </div>
                </div>

                <div style={{ display: 'flex', justifyContent: 'flex-end', marginTop: '2rem' }}>
                  <button type="submit" className="btn-primary">
                    Review Information <ArrowRight size={18} />
                  </button>
                </div>
              </form>
            )}

            {/* STEP 2: REVIEW SCREEN */}
            {step === 'review' && (
              <div className="app-card" style={{ padding: '2rem', maxWidth: '700px', margin: '0 auto' }}>
                <h2 style={{ fontSize: '1.4rem', fontWeight: 700, color: 'var(--text-main)', marginBottom: '0.4rem' }}>
                  Review Your Information
                </h2>
                <p style={{ color: 'var(--text-muted)', fontSize: '0.9rem', marginBottom: '1.5rem' }}>
                  Please confirm your health profile details before saving.
                </p>

                <div style={{ background: '#f8fafc', padding: '1.25rem', borderRadius: 'var(--radius-md)', border: '1px solid var(--border-subtle)', marginBottom: '1.25rem' }}>
                  <h3 style={{ fontSize: '1rem', fontWeight: 700, color: 'var(--primary-emerald)', marginBottom: '0.75rem' }}>
                    Basic Information
                  </h3>
                  <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '0.6rem', fontSize: '0.95rem' }}>
                    <div><strong>Age:</strong> {profile.age}</div>
                    <div><strong>Gender:</strong> {profile.gender.charAt(0).toUpperCase() + profile.gender.slice(1)}</div>
                    <div><strong>Height:</strong> {profile.height_cm} cm</div>
                    <div><strong>Weight:</strong> {profile.weight_kg} kg</div>
                  </div>
                </div>

                <div style={{ background: '#f8fafc', padding: '1.25rem', borderRadius: 'var(--radius-md)', border: '1px solid var(--border-subtle)', marginBottom: '1.25rem' }}>
                  <h3 style={{ fontSize: '1rem', fontWeight: 700, color: 'var(--primary-emerald)', marginBottom: '0.75rem' }}>
                    Dietary Preferences & Medical
                  </h3>
                  <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem', fontSize: '0.95rem' }}>
                    <div><strong>Dietary Restrictions:</strong> {(profile.allergies_intolerances || []).length > 0 ? profile.allergies_intolerances.join(', ') : 'None'}</div>
                    <div><strong>Medical Conditions:</strong> {(profile.medical_conditions || []).length > 0 ? profile.medical_conditions.join(', ') : 'None'}</div>
                  </div>
                </div>

                <div style={{ background: '#f8fafc', padding: '1.25rem', borderRadius: 'var(--radius-md)', border: '1px solid var(--border-subtle)', marginBottom: '2rem' }}>
                  <h3 style={{ fontSize: '1rem', fontWeight: 700, color: 'var(--primary-emerald)', marginBottom: '0.75rem' }}>
                    Health Goal & Target
                  </h3>
                  <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem', fontSize: '0.95rem' }}>
                    <div><strong>Health Goal:</strong> {profile.health_goal}</div>
                    <div><strong>Target:</strong> {profile.target_value}</div>
                    <div><strong>Target Period:</strong> {profile.target_period}</div>
                  </div>
                </div>

                <div style={{ display: 'flex', gap: '1rem', justifyContent: 'flex-end' }}>
                  <button className="btn-secondary" onClick={() => setStep('form')}>
                    <Edit3 size={18} /> Edit
                  </button>
                  <button className="btn-primary" onClick={handleSubmitProfile} disabled={saving}>
                    <Save size={18} /> {saving ? 'Saving...' : 'Submit Profile'}
                  </button>
                </div>
              </div>
            )}

            {/* STEP 3: CONFIRMATION SCREEN */}
            {step === 'confirmation' && (
              <div className="app-card" style={{ padding: '3rem 2rem', textAlign: 'center', maxWidth: '600px', margin: '0 auto' }}>
                <div style={{ background: 'var(--bg-mint)', width: '64px', height: '64px', borderRadius: '50%', display: 'inline-flex', alignItems: 'center', justifyContent: 'center', color: 'var(--primary-emerald)', marginBottom: '1.25rem' }}>
                  <CheckCircle size={36} />
                </div>

                <h2 style={{ fontSize: '1.5rem', fontWeight: 700, color: 'var(--text-main)', marginBottom: '0.5rem' }}>
                  Your health profile has been saved successfully.
                </h2>
                <p style={{ color: 'var(--text-muted)', fontSize: '0.95rem', marginBottom: '2rem' }}>
                  Your profile and goal parameters are safely stored in your isolated database account.
                </p>

                <div style={{ display: 'flex', gap: '1rem', justifyContent: 'center', flexWrap: 'wrap' }}>
                  <button className="btn-secondary" onClick={() => setStep('form')}>
                    <Edit3 size={18} /> Edit Profile
                  </button>
                  <button className="btn-secondary" onClick={() => setStep('review')}>
                    <Eye size={18} /> View Profile
                  </button>
                  <button className="btn-primary" onClick={() => navigate('/')}>
                    <Home size={18} /> Go to Home
                  </button>
                </div>
              </div>
            )}
          </>
        )}
      </main>
    </div>
  );
};
