import React, { useEffect, useState } from 'react';
import { Navbar } from '../components/Navbar';
import { getBloodTests, createBloodTest, updateBloodTest } from '../services/api';
import { BloodTestEntry } from '../types';
import { FileText, Save, CheckCircle, AlertCircle, Calendar, Plus, Edit2 } from 'lucide-react';

export const BloodTestPage: React.FC = () => {
  const [testDate, setTestDate] = useState<string>(new Date().toISOString().split('T')[0]);
  const [hemoglobin, setHemoglobin] = useState<string>('');
  const [vitaminD, setVitaminD] = useState<string>('');
  const [vitaminB12, setVitaminB12] = useState<string>('');
  const [iron, setIron] = useState<string>('');
  const [calcium, setCalcium] = useState<string>('');

  const [history, setHistory] = useState<BloodTestEntry[]>([]);
  const [editingId, setEditingId] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [message, setMessage] = useState<{ type: 'success' | 'error'; text: string } | null>(null);

  useEffect(() => {
    fetchBloodTests();
  }, []);

  const fetchBloodTests = async () => {
    try {
      setLoading(true);
      const data = await getBloodTests();
      setHistory(data);
    } catch (err) {
      console.error('Error loading blood test results:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleEditEntry = (entry: BloodTestEntry) => {
    setEditingId(entry.id || null);
    setTestDate(entry.test_date);
    setHemoglobin(entry.hemoglobin !== undefined && entry.hemoglobin !== null ? String(entry.hemoglobin) : '');
    setVitaminD(entry.vitamin_d !== undefined && entry.vitamin_d !== null ? String(entry.vitamin_d) : '');
    setVitaminB12(entry.vitamin_b12 !== undefined && entry.vitamin_b12 !== null ? String(entry.vitamin_b12) : '');
    setIron(entry.iron !== undefined && entry.iron !== null ? String(entry.iron) : '');
    setCalcium(entry.calcium !== undefined && entry.calcium !== null ? String(entry.calcium) : '');
    setMessage(null);
  };

  const resetForm = () => {
    setEditingId(null);
    setTestDate(new Date().toISOString().split('T')[0]);
    setHemoglobin('');
    setVitaminD('');
    setVitaminB12('');
    setIron('');
    setCalcium('');
  };

  const handleSaveResults = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      setSaving(true);
      setMessage(null);

      const payload: BloodTestEntry = {
        test_date: testDate,
        hemoglobin: hemoglobin ? parseFloat(hemoglobin) : undefined,
        vitamin_d: vitaminD ? parseFloat(vitaminD) : undefined,
        vitamin_b12: vitaminB12 ? parseFloat(vitaminB12) : undefined,
        iron: iron ? parseFloat(iron) : undefined,
        calcium: calcium ? parseFloat(calcium) : undefined,
      };

      if (editingId) {
        await updateBloodTest(editingId, payload);
        setMessage({ type: 'success', text: 'Blood test results updated successfully!' });
      } else {
        await createBloodTest(payload);
        setMessage({ type: 'success', text: 'Blood test results saved successfully!' });
      }

      resetForm();
      await fetchBloodTests();
    } catch (err: any) {
      setMessage({ type: 'error', text: err.response?.data?.detail || 'Failed to save blood test results.' });
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
            <FileText size={26} color="var(--primary-emerald)" /> Blood Test Results
          </h1>
          <p style={{ color: 'var(--text-muted)', fontSize: '0.95rem' }}>
            Enter your recent blood test values. All values are stored securely for future health analysis.
          </p>
        </div>

        {message && (
          <div className={message.type === 'success' ? 'alert-success' : 'alert-error'}>
            {message.type === 'success' ? <CheckCircle size={20} /> : <AlertCircle size={20} />}
            <span>{message.text}</span>
          </div>
        )}

        <form onSubmit={handleSaveResults} className="app-card" style={{ padding: '2rem', marginBottom: '2.5rem' }}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '1.5rem', flexWrap: 'wrap', gap: '1rem', borderBottom: '1px solid var(--border-subtle)', paddingBottom: '1rem' }}>
            <h2 style={{ fontSize: '1.25rem', fontWeight: 700, color: 'var(--text-main)' }}>
              {editingId ? 'Edit Blood Test Entry' : 'Enter New Blood Test Values'}
            </h2>

            {editingId && (
              <button type="button" className="btn-secondary" style={{ padding: '0.35rem 0.75rem', fontSize: '0.85rem' }} onClick={resetForm}>
                <Plus size={14} /> New Entry
              </button>
            )}
          </div>

          <div className="form-group" style={{ maxWidth: '300px', marginBottom: '1.5rem' }}>
            <label style={{ display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
              <Calendar size={16} /> Test Date
            </label>
            <input
              type="date"
              className="input-field"
              value={testDate}
              onChange={(e) => setTestDate(e.target.value)}
              required
            />
          </div>

          <div className="grid-2">
            <div className="form-group">
              <label>Hemoglobin (g/dL)</label>
              <input
                type="number"
                step="0.1"
                className="input-field"
                placeholder="e.g. 13.5"
                value={hemoglobin}
                onChange={(e) => setHemoglobin(e.target.value)}
              />
            </div>

            <div className="form-group">
              <label>Vitamin D (ng/mL)</label>
              <input
                type="number"
                step="0.1"
                className="input-field"
                placeholder="e.g. 18"
                value={vitaminD}
                onChange={(e) => setVitaminD(e.target.value)}
              />
            </div>
          </div>

          <div className="grid-3">
            <div className="form-group">
              <label>Vitamin B12 (pg/mL)</label>
              <input
                type="number"
                step="1"
                className="input-field"
                placeholder="e.g. 320"
                value={vitaminB12}
                onChange={(e) => setVitaminB12(e.target.value)}
              />
            </div>

            <div className="form-group">
              <label>Serum Iron (mcg/dL)</label>
              <input
                type="number"
                step="0.1"
                className="input-field"
                placeholder="e.g. 75"
                value={iron}
                onChange={(e) => setIron(e.target.value)}
              />
            </div>

            <div className="form-group">
              <label>Calcium (mg/dL)</label>
              <input
                type="number"
                step="0.1"
                className="input-field"
                placeholder="e.g. 9.2"
                value={calcium}
                onChange={(e) => setCalcium(e.target.value)}
              />
            </div>
          </div>

          <div style={{ display: 'flex', justifyContent: 'flex-end', marginTop: '1.75rem' }}>
            <button type="submit" className="btn-primary" disabled={saving}>
              <Save size={18} /> {saving ? 'Saving...' : editingId ? 'Update Results' : 'Save Results'}
            </button>
          </div>
        </form>

        {/* History Table */}
        <div style={{ marginBottom: '2rem' }}>
          <h2 style={{ fontSize: '1.2rem', fontWeight: 700, color: 'var(--text-main)', marginBottom: '1rem' }}>
            Saved Blood Test History
          </h2>

          {loading ? (
            <div className="app-card" style={{ padding: '2rem', textAlign: 'center', color: 'var(--text-muted)' }}>
              Loading blood test history...
            </div>
          ) : history.length === 0 ? (
            <div className="app-card" style={{ padding: '2rem', textAlign: 'center', color: 'var(--text-muted)' }}>
              No blood test results recorded yet.
            </div>
          ) : (
            <div className="app-card" style={{ overflowX: 'auto' }}>
              <table style={{ width: '100%', borderCollapse: 'collapse', textAlign: 'left', fontSize: '0.9rem' }}>
                <thead>
                  <tr style={{ background: '#f8fafc', borderBottom: '1px solid var(--border-subtle)' }}>
                    <th style={{ padding: '0.75rem 1rem', fontWeight: 600 }}>Test Date</th>
                    <th style={{ padding: '0.75rem 1rem', fontWeight: 600 }}>Hemoglobin</th>
                    <th style={{ padding: '0.75rem 1rem', fontWeight: 600 }}>Vitamin D</th>
                    <th style={{ padding: '0.75rem 1rem', fontWeight: 600 }}>Vitamin B12</th>
                    <th style={{ padding: '0.75rem 1rem', fontWeight: 600 }}>Iron</th>
                    <th style={{ padding: '0.75rem 1rem', fontWeight: 600 }}>Calcium</th>
                    <th style={{ padding: '0.75rem 1rem', fontWeight: 600 }}>Action</th>
                  </tr>
                </thead>
                <tbody>
                  {history.map((row) => (
                    <tr key={row.id} style={{ borderBottom: '1px solid var(--border-subtle)' }}>
                      <td style={{ padding: '0.75rem 1rem', fontWeight: 600 }}>{row.test_date}</td>
                      <td style={{ padding: '0.75rem 1rem' }}>{row.hemoglobin != null ? `${row.hemoglobin} g/dL` : '—'}</td>
                      <td style={{ padding: '0.75rem 1rem' }}>{row.vitamin_d != null ? `${row.vitamin_d} ng/mL` : '—'}</td>
                      <td style={{ padding: '0.75rem 1rem' }}>{row.vitamin_b12 != null ? `${row.vitamin_b12} pg/mL` : '—'}</td>
                      <td style={{ padding: '0.75rem 1rem' }}>{row.iron != null ? `${row.iron} mcg/dL` : '—'}</td>
                      <td style={{ padding: '0.75rem 1rem' }}>{row.calcium != null ? `${row.calcium} mg/dL` : '—'}</td>
                      <td style={{ padding: '0.75rem 1rem' }}>
                        <button
                          className="btn-secondary"
                          style={{ padding: '0.3rem 0.6rem', fontSize: '0.8rem' }}
                          onClick={() => handleEditEntry(row)}
                        >
                          <Edit2 size={14} /> Edit
                        </button>
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
