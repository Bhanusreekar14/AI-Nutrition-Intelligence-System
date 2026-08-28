import React, { useEffect, useState } from 'react';
import { Navbar } from '../components/Navbar';
import { getMyHealthProfile, saveHealthProfile } from '../services/api';
import { HealthProfile } from '../types';
import { Activity, Save, CheckCircle, AlertCircle, Zap, Flame, UserCheck } from 'lucide-react';

export const HealthProfilePage: React.FC = () => {
  const [profile, setProfile] = useState<HealthProfile>({
    age: 25,
    gender: 'male',
    height_cm: 175,
    weight_kg: 70,
    activity_level: 'moderately_active',
    dietary_preference: 'omnivore',
    health_goals: ['Deficiency Prevention', 'Energy Boost'],
    allergies_intolerances: [],
    medical_conditions: [],
  });

  const [goalInput, setGoalInput] = useState('');
  const [allergyInput, setAllergyInput] = useState('');
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [message, setMessage] = useState<{ type: 'success' | 'error'; text: string } | null>(null);

  useEffect(() => {
    fetchProfile();
  }, []);

  const fetchProfile = async () => {
    try {
      setLoading(true);
      const data = await getMyHealthProfile();
      if (data) {
        setProfile(data);
      }
    } catch (err: any) {
      // If 404, user hasn't created profile yet, default template is kept
      console.log('No existing health profile found, initializing new form');
    } finally {
      setLoading(false);
    }
  };

  const handleSave = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      setSaving(true);
      setMessage(null);
      const updated = await saveHealthProfile(profile);
      setProfile(updated);
      setMessage({ type: 'success', text: 'Health Profile saved & BMR/TDEE recalculated successfully!' });
    } catch (err: any) {
      setMessage({ type: 'error', text: err.response?.data?.detail || 'Failed to save health profile.' });
    } finally {
      setSaving(false);
    }
  };

  const addTag = (type: 'goals' | 'allergies', value: string) => {
    if (!value.trim()) return;
    if (type === 'goals') {
      if (!profile.health_goals.includes(value.trim())) {
        setProfile({ ...profile, health_goals: [...profile.health_goals, value.trim()] });
      }
      setGoalInput('');
    } else {
      if (!profile.allergies_intolerances.includes(value.trim())) {
        setProfile({ ...profile, allergies_intolerances: [...profile.allergies_intolerances, value.trim()] });
      }
      setAllergyInput('');
    }
  };

  const removeTag = (type: 'goals' | 'allergies', tag: string) => {
    if (type === 'goals') {
      setProfile({ ...profile, health_goals: profile.health_goals.filter(g => g !== tag) });
    } else {
      setProfile({ ...profile, allergies_intolerances: profile.allergies_intolerances.filter(a => a !== tag) });
    }
  };

  return (
    <div style={{ minHeight: '100vh' }}>
      <Navbar />

      <main className="app-container" style={{ marginTop: '1rem' }}>
        {/* Header Section */}
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '2rem' }}>
          <div>
            <h1 style={{ fontSize: '1.8rem', fontWeight: 800, color: '#fff', display: 'flex', alignItems: 'center', gap: '0.6rem' }}>
              <UserCheck size={28} color="var(--primary-emerald)" /> Health & Biological Profile
            </h1>
            <p style={{ color: 'var(--text-muted)', fontSize: '0.95rem' }}>
              Configure your baseline metrics to enable personalized nutritional targets and deficiency tracking.
            </p>
          </div>

          {/* Quick Metrics Badge */}
          {profile.bmr && (
            <div style={{ display: 'flex', gap: '1rem' }}>
              <div className="glass-card" style={{ padding: '0.75rem 1.25rem', display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
                <Flame size={24} color="var(--accent-amber)" />
                <div>
                  <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>BMR</div>
                  <div style={{ fontSize: '1.1rem', fontWeight: 700, color: '#fff' }}>{profile.bmr} <span style={{ fontSize: '0.75rem' }}>kcal</span></div>
                </div>
              </div>
              <div className="glass-card" style={{ padding: '0.75rem 1.25rem', display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
                <Zap size={24} color="var(--primary-emerald)" />
                <div>
                  <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>TDEE Target</div>
                  <div style={{ fontSize: '1.1rem', fontWeight: 700, color: '#fff' }}>{profile.tdee} <span style={{ fontSize: '0.75rem' }}>kcal</span></div>
                </div>
              </div>
            </div>
          )}
        </div>

        {message && (
          <div style={{
            background: message.type === 'success' ? 'rgba(16, 185, 129, 0.15)' : 'rgba(244, 63, 94, 0.15)',
            border: `1px solid ${message.type === 'success' ? 'rgba(16, 185, 129, 0.3)' : 'rgba(244, 63, 94, 0.3)'}`,
            borderRadius: 'var(--radius-md)',
            padding: '1rem',
            marginBottom: '1.5rem',
            display: 'flex',
            alignItems: 'center',
            gap: '0.75rem',
            color: message.type === 'success' ? '#6ee7b7' : '#fda4af'
          }}>
            {message.type === 'success' ? <CheckCircle size={20} /> : <AlertCircle size={20} />}
            <span>{message.text}</span>
          </div>
        )}

        {loading ? (
          <div style={{ padding: '3rem', textAlign: 'center', color: 'var(--text-muted)' }}>
            Loading profile parameters...
          </div>
        ) : (
          <form onSubmit={handleSave} className="grid-2">
            {/* Left Card: Biometrics */}
            <div className="glass-card" style={{ padding: '2rem' }}>
              <h2 style={{ fontSize: '1.2rem', fontWeight: 700, marginBottom: '1.5rem', color: '#fff', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                <Activity size={20} color="var(--primary-teal)" /> Physical Metrics
              </h2>

              <div className="grid-2">
                <div className="form-group">
                  <label>Age (years)</label>
                  <input
                    type="number"
                    className="input-field"
                    value={profile.age}
                    onChange={(e) => setProfile({ ...profile, age: parseInt(e.target.value) || 0 })}
                    min={1}
                    max={120}
                    required
                  />
                </div>

                <div className="form-group">
                  <label>Biological Gender</label>
                  <select
                    className="input-field"
                    value={profile.gender}
                    onChange={(e) => setProfile({ ...profile, gender: e.target.value as any })}
                  >
                    <option value="male">Male</option>
                    <option value="female">Female</option>
                    <option value="other">Other</option>
                    <option value="prefer_not_to_say">Prefer Not to Say</option>
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
                    value={profile.height_cm}
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
                    value={profile.weight_kg}
                    onChange={(e) => setProfile({ ...profile, weight_kg: parseFloat(e.target.value) || 0 })}
                    required
                  />
                </div>
              </div>

              <div className="form-group">
                <label>Physical Activity Level</label>
                <select
                  className="input-field"
                  value={profile.activity_level}
                  onChange={(e) => setProfile({ ...profile, activity_level: e.target.value as any })}
                >
                  <option value="sedentary">Sedentary (Little or no exercise)</option>
                  <option value="lightly_active">Lightly Active (Exercise 1-3 days/week)</option>
                  <option value="moderately_active">Moderately Active (Exercise 3-5 days/week)</option>
                  <option value="very_active">Very Active (Hard exercise 6-7 days/week)</option>
                  <option value="extra_active">Extra Active (Very hard exercise & physical job)</option>
                </select>
              </div>

              <div className="form-group">
                <label>Dietary Preference Pattern</label>
                <select
                  className="input-field"
                  value={profile.dietary_preference}
                  onChange={(e) => setProfile({ ...profile, dietary_preference: e.target.value as any })}
                >
                  <option value="omnivore">Omnivore (Standard Unrestricted)</option>
                  <option value="vegetarian">Vegetarian</option>
                  <option value="vegan">Vegan</option>
                  <option value="keto">Ketogenic</option>
                  <option value="paleo">Paleo</option>
                  <option value="mediterranean">Mediterranean</option>
                  <option value="other">Other</option>
                </select>
              </div>
            </div>

            {/* Right Card: Preferences & Goals */}
            <div className="glass-card" style={{ padding: '2rem', display: 'flex', flexDirection: 'column', justifyContent: 'space-between' }}>
              <div>
                <h2 style={{ fontSize: '1.2rem', fontWeight: 700, marginBottom: '1.5rem', color: '#fff' }}>
                  Goals & Dietary Restrictions
                </h2>

                {/* Health Goals Tagging */}
                <div className="form-group">
                  <label>Health & Dietary Goals</label>
                  <div style={{ display: 'flex', gap: '0.5rem', marginBottom: '0.6rem' }}>
                    <input
                      type="text"
                      className="input-field"
                      placeholder="Add goal (e.g. Muscle Gain, Vitamin D Focus)"
                      value={goalInput}
                      onChange={(e) => setGoalInput(e.target.value)}
                      onKeyDown={(e) => e.key === 'Enter' && (e.preventDefault(), addTag('goals', goalInput))}
                      style={{ flex: 1 }}
                    />
                    <button type="button" className="btn-secondary" onClick={() => addTag('goals', goalInput)}>Add</button>
                  </div>
                  <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.5rem' }}>
                    {profile.health_goals.map((g) => (
                      <span key={g} className="badge badge-emerald" style={{ cursor: 'pointer' }} onClick={() => removeTag('goals', g)}>
                        {g} ×
                      </span>
                    ))}
                  </div>
                </div>

                {/* Allergies & Intolerances */}
                <div className="form-group" style={{ marginTop: '1.5rem' }}>
                  <label>Allergies & Intolerances</label>
                  <div style={{ display: 'flex', gap: '0.5rem', marginBottom: '0.6rem' }}>
                    <input
                      type="text"
                      className="input-field"
                      placeholder="Add allergy (e.g. Lactose, Peanut, Gluten)"
                      value={allergyInput}
                      onChange={(e) => setAllergyInput(e.target.value)}
                      onKeyDown={(e) => e.key === 'Enter' && (e.preventDefault(), addTag('allergies', allergyInput))}
                      style={{ flex: 1 }}
                    />
                    <button type="button" className="btn-secondary" onClick={() => addTag('allergies', allergyInput)}>Add</button>
                  </div>
                  <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.5rem' }}>
                    {profile.allergies_intolerances.map((a) => (
                      <span key={a} className="badge badge-amber" style={{ cursor: 'pointer' }} onClick={() => removeTag('allergies', a)}>
                        {a} ×
                      </span>
                    ))}
                  </div>
                </div>
              </div>

              <div style={{ marginTop: '2rem' }}>
                <button
                  type="submit"
                  className="btn-primary"
                  disabled={saving}
                  style={{ width: '100%', padding: '0.9rem' }}
                >
                  <Save size={20} /> {saving ? 'Saving Metrics...' : 'Save Health Profile'}
                </button>
              </div>
            </div>
          </form>
        )}
      </main>
    </div>
  );
};
