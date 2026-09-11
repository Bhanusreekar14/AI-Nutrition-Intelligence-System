import React, { useEffect, useState } from 'react';
import { Navbar } from '../components/Navbar';
import { getSymptomAssessments, saveSymptomAssessment } from '../services/api';
import { SymptomAssessmentRecord, SymptomItem } from '../types';
import { Activity, CheckCircle, AlertCircle, Save } from 'lucide-react';

export const SymptomsPage: React.FC = () => {
  const [assessmentDate, setAssessmentDate] = useState<string>(new Date().toISOString().split('T')[0]);
  const [symptomsState, setSymptomsState] = useState<Record<string, 'Never' | 'Sometimes' | 'Often' | 'Very Often'>>({
    'Fatigue': 'Never',
    'Hair Loss': 'Never',
    'Skin Conditions': 'Never',
    'Muscle Weakness': 'Never',
    'Mood-related Symptoms': 'Never'
  });

  const [pastRecords, setPastRecords] = useState<SymptomAssessmentRecord[]>([]);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [message, setMessage] = useState<{ type: 'success' | 'error'; text: string } | null>(null);

  const symptomList = [
    { key: 'Fatigue', title: 'Fatigue & Low Energy', desc: 'Feeling unusually tired, sluggish, or lacking physical stamina.' },
    { key: 'Hair Loss', title: 'Hair Loss & Thinning', desc: 'Excessive hair shedding or noticeable thinning.' },
    { key: 'Skin Conditions', title: 'Skin Conditions & Dryness', desc: 'Dry skin, rashes, slow wound healing, or easy bruising.' },
    { key: 'Muscle Weakness', title: 'Muscle Weakness & Cramps', desc: 'Muscle soreness, cramps, or reduced strength.' },
    { key: 'Mood-related Symptoms', title: 'Mood-related Symptoms', desc: 'Irritability, mood swings, anxiety, or brain fog.' },
  ];

  const options: ('Never' | 'Sometimes' | 'Often' | 'Very Often')[] = ['Never', 'Sometimes', 'Often', 'Very Often'];

  useEffect(() => {
    fetchHistory();
  }, []);

  const fetchHistory = async () => {
    try {
      setLoading(true);
      const data = await getSymptomAssessments();
      setPastRecords(data);
    } catch (err) {
      console.error('Error fetching symptom history:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleRadioChange = (symptomKey: string, val: 'Never' | 'Sometimes' | 'Often' | 'Very Often') => {
    setSymptomsState(prev => ({ ...prev, [symptomKey]: val }));
  };

  const handleSaveAssessment = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      setSaving(true);
      setMessage(null);

      const assessmentsPayload: SymptomItem[] = Object.entries(symptomsState).map(([symptom, severity]) => ({
        symptom,
        severity
      }));

      await saveSymptomAssessment({
        assessment_date: assessmentDate,
        assessments: assessmentsPayload
      });

      setMessage({ type: 'success', text: 'Symptom assessment saved successfully!' });
      await fetchHistory();
    } catch (err: any) {
      setMessage({ type: 'error', text: err.response?.data?.detail || 'Failed to save symptom assessment.' });
    } finally {
      setSaving(false);
    }
  };

  return (
    <div style={{ minHeight: '100vh', background: 'var(--bg-page)' }}>
      <Navbar />

      <main className="app-container">
        <div style={{ marginBottom: '1.75rem' }}>
          <h1 style={{ fontSize: '1.75rem', fontWeight: 700, color: 'var(--text-main)', display: 'flex', alignItems: 'center', gap: '0.6rem' }}>
            <Activity size={26} color="var(--primary-emerald)" /> Symptom Assessment
          </h1>
          <p style={{ color: 'var(--text-muted)', fontSize: '0.95rem' }}>
            Record physical symptoms for data collection. This information will be used for future deficiency analysis.
          </p>
        </div>

        {message && (
          <div className={message.type === 'success' ? 'alert-success' : 'alert-error'}>
            {message.type === 'success' ? <CheckCircle size={20} /> : <AlertCircle size={20} />}
            <span>{message.text}</span>
          </div>
        )}

        <form onSubmit={handleSaveAssessment} className="app-card" style={{ padding: '2rem', marginBottom: '2.5rem' }}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '1.5rem', flexWrap: 'wrap', gap: '1rem', borderBottom: '1px solid var(--border-subtle)', paddingBottom: '1rem' }}>
            <h2 style={{ fontSize: '1.25rem', fontWeight: 700, color: 'var(--text-main)' }}>
              Symptom Questionnaire
            </h2>

            <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
              <label style={{ fontSize: '0.875rem', fontWeight: 600, color: 'var(--text-muted)' }}>Assessment Date:</label>
              <input
                type="date"
                className="input-field"
                value={assessmentDate}
                onChange={(e) => setAssessmentDate(e.target.value)}
                style={{ padding: '0.4rem 0.75rem', fontSize: '0.9rem' }}
                required
              />
            </div>
          </div>

          <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
            {symptomList.map((item) => (
              <div
                key={item.key}
                style={{
                  background: '#f8fafc',
                  border: '1px solid var(--border-subtle)',
                  borderRadius: 'var(--radius-md)',
                  padding: '1.25rem'
                }}
              >
                <div style={{ fontWeight: 700, fontSize: '1rem', color: 'var(--text-main)', marginBottom: '0.2rem' }}>
                  {item.title}
                </div>
                <div style={{ fontSize: '0.85rem', color: 'var(--text-muted)', marginBottom: '1rem' }}>
                  {item.desc}
                </div>

                <div style={{ display: 'flex', gap: '1.25rem', flexWrap: 'wrap' }}>
                  {options.map((opt) => (
                    <label
                      key={opt}
                      style={{
                        display: 'flex',
                        alignItems: 'center',
                        gap: '0.4rem',
                        cursor: 'pointer',
                        fontSize: '0.9rem',
                        fontWeight: symptomsState[item.key] === opt ? 600 : 400,
                        color: symptomsState[item.key] === opt ? 'var(--primary-emerald)' : 'var(--text-main)'
                      }}
                    >
                      <input
                        type="radio"
                        name={`symptom_${item.key}`}
                        value={opt}
                        checked={symptomsState[item.key] === opt}
                        onChange={() => handleRadioChange(item.key, opt)}
                      />
                      {opt}
                    </label>
                  ))}
                </div>
              </div>
            ))}
          </div>

          <div style={{ display: 'flex', justifyContent: 'flex-end', marginTop: '2rem' }}>
            <button type="submit" className="btn-primary" disabled={saving}>
              <Save size={18} /> {saving ? 'Saving...' : 'Save Assessment'}
            </button>
          </div>
        </form>

        {/* Past Assessments Log */}
        <div style={{ marginBottom: '2rem' }}>
          <h2 style={{ fontSize: '1.2rem', fontWeight: 700, color: 'var(--text-main)', marginBottom: '1rem' }}>
            Recent Symptom History
          </h2>

          {loading ? (
            <div className="app-card" style={{ padding: '2rem', textAlign: 'center', color: 'var(--text-muted)' }}>
              Loading symptom records...
            </div>
          ) : pastRecords.length === 0 ? (
            <div className="app-card" style={{ padding: '2rem', textAlign: 'center', color: 'var(--text-muted)' }}>
              No symptom assessments recorded yet.
            </div>
          ) : (
            <div className="app-card" style={{ overflowX: 'auto' }}>
              <table style={{ width: '100%', borderCollapse: 'collapse', textAlign: 'left', fontSize: '0.9rem' }}>
                <thead>
                  <tr style={{ background: '#f8fafc', borderBottom: '1px solid var(--border-subtle)' }}>
                    <th style={{ padding: '0.75rem 1rem', fontWeight: 600 }}>Date</th>
                    <th style={{ padding: '0.75rem 1rem', fontWeight: 600 }}>Symptom</th>
                    <th style={{ padding: '0.75rem 1rem', fontWeight: 600 }}>Severity Response</th>
                  </tr>
                </thead>
                <tbody>
                  {pastRecords.map((rec) => (
                    <tr key={rec.id} style={{ borderBottom: '1px solid var(--border-subtle)' }}>
                      <td style={{ padding: '0.75rem 1rem', color: 'var(--text-muted)' }}>{rec.assessment_date}</td>
                      <td style={{ padding: '0.75rem 1rem', fontWeight: 600, color: 'var(--text-main)' }}>{rec.symptom}</td>
                      <td style={{ padding: '0.75rem 1rem' }}>
                        <span className={`badge ${rec.severity === 'Never' ? 'badge-mint' : rec.severity === 'Sometimes' ? 'badge-blue' : 'badge-amber'}`}>
                          {rec.severity}
                        </span>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      </main>
    </div>
  );
};
