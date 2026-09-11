import React, { useState } from 'react';
import { Navbar } from '../components/Navbar';
import { predictDeficiencyRisk } from '../services/api';
import { 
  DeficiencyPredictionRequest, 
  DeficiencyPredictionResponse 
} from '../types';
import { 
  Sparkles, 
  AlertTriangle, 
  Loader2, 
  TrendingUp, 
  TrendingDown, 
  ShieldAlert, 
  Activity, 
  Zap,
  Info
} from 'lucide-react';

const INITIAL_FORM_STATE: DeficiencyPredictionRequest = {
  age: 35,
  gender: 'female',
  bmi: 22.5,
  diet_type: 'omnivore',
  smoking_status: 'never',
  alcohol_consumption: 'none',
  exercise_level: 'moderate',
  sun_exposure: 'moderate',
  income_level: 'middle',
  latitude_region: 'moderate',

  vitamin_a_percent_rda: 90,
  vitamin_c_percent_rda: 95,
  vitamin_d_percent_rda: 40,
  vitamin_e_percent_rda: 85,
  vitamin_k_percent_rda: 90,
  thiamin_b1_percent_rda: 100,
  riboflavin_b2_percent_rda: 95,
  niacin_b3_percent_rda: 100,
  vitamin_b6_percent_rda: 90,
  folate_b9_percent_rda: 85,
  vitamin_b12_percent_rda: 80,
  calcium_percent_rda: 85,
  iron_percent_rda: 50,
  magnesium_percent_rda: 80,
  zinc_percent_rda: 85,
  potassium_percent_rda: 80,

  hemoglobin_g_dl: 12.5,
  serum_vitamin_d_ng_ml: 18.0,
  serum_vitamin_b12_pg_ml: 350.0,
  serum_folate_ng_ml: 8.5,

  symptoms_count: 2,
  has_fatigue: true,
  has_weakness: false,
  has_dizziness: false,
  has_hair_loss: false,
  has_brittle_nails: true,
  has_pale_skin: false,
  has_bone_pain: false,
  has_muscle_cramps: false,
  has_numbness_tingling: false,
  has_night_blindness: false,
  has_mouth_sores: false,
  has_slow_wound_healing: false,
};

// Preset scenarios for fast UI testing
const PRESETS = [
  {
    name: 'Healthy Baseline',
    desc: 'Balanced diet, good lab values, no symptoms',
    data: {
      ...INITIAL_FORM_STATE,
      age: 28,
      vitamin_d_percent_rda: 110,
      iron_percent_rda: 105,
      vitamin_b12_percent_rda: 115,
      hemoglobin_g_dl: 14.2,
      serum_vitamin_d_ng_ml: 38.0,
      serum_vitamin_b12_pg_ml: 520.0,
      serum_folate_ng_ml: 12.0,
      symptoms_count: 0,
      has_fatigue: false,
      has_brittle_nails: false,
    }
  },
  {
    name: 'Vitamin D Risk',
    desc: 'Low sun, high latitude, low serum D & bone pain',
    data: {
      ...INITIAL_FORM_STATE,
      age: 45,
      sun_exposure: 'low',
      latitude_region: 'high',
      vitamin_d_percent_rda: 15,
      serum_vitamin_d_ng_ml: 11.2,
      symptoms_count: 3,
      has_fatigue: true,
      has_bone_pain: true,
      has_muscle_cramps: true,
    }
  },
  {
    name: 'Iron Deficiency Risk',
    desc: 'Vegetarian, low iron RDA, low hemoglobin & fatigue',
    data: {
      ...INITIAL_FORM_STATE,
      age: 26,
      diet_type: 'vegetarian',
      iron_percent_rda: 20,
      hemoglobin_g_dl: 9.8,
      symptoms_count: 4,
      has_fatigue: true,
      has_weakness: true,
      has_dizziness: true,
      has_pale_skin: true,
      has_brittle_nails: true,
    }
  },
  {
    name: 'Vitamin B12 Risk',
    desc: 'Vegan, low B12 RDA, low serum B12 & numbness',
    data: {
      ...INITIAL_FORM_STATE,
      age: 50,
      diet_type: 'vegan',
      vitamin_b12_percent_rda: 10,
      serum_vitamin_b12_pg_ml: 145.0,
      symptoms_count: 3,
      has_fatigue: true,
      has_numbness_tingling: true,
      has_mouth_sores: true,
    }
  }
];

export const PredictionPage: React.FC = () => {
  const [formData, setFormData] = useState<DeficiencyPredictionRequest>(INITIAL_FORM_STATE);
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<DeficiencyPredictionResponse | null>(null);
  const [activeTab, setActiveTab] = useState<'demographics' | 'nutrients' | 'biomarkers' | 'symptoms'>('demographics');

  const handleInputChange = (field: keyof DeficiencyPredictionRequest, value: any) => {
    setFormData(prev => {
      const updated = { ...prev, [field]: value };
      
      // Auto-update symptoms_count if toggling a symptom boolean
      if (typeof value === 'boolean' && field.startsWith('has_')) {
        const symptomKeys: (keyof DeficiencyPredictionRequest)[] = [
          'has_fatigue', 'has_weakness', 'has_dizziness', 'has_hair_loss', 
          'has_brittle_nails', 'has_pale_skin', 'has_bone_pain', 'has_muscle_cramps', 
          'has_numbness_tingling', 'has_night_blindness', 'has_mouth_sores', 'has_slow_wound_healing'
        ];
        const count = symptomKeys.reduce((acc, k) => acc + (k === field ? (value ? 1 : 0) : (updated[k] ? 1 : 0)), 0);
        updated.symptoms_count = count;
      }
      return updated;
    });
  };

  const handleApplyPreset = (presetData: DeficiencyPredictionRequest) => {
    setFormData(presetData);
    setResult(null);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    try {
      const res = await predictDeficiencyRisk(formData);
      setResult(res);
    } catch (err: any) {
      console.error('Prediction error:', err);
      setError(err?.response?.data?.detail || err?.message || 'Failed to generate prediction. Please check backend status.');
    } finally {
      setLoading(false);
    }
  };

  const getRiskBadgeColor = (level: string) => {
    switch (level.toLowerCase()) {
      case 'low': return { bg: '#dcfce7', text: '#15803d', border: '#86efac' };
      case 'moderate': return { bg: '#fef9c3', text: '#a16207', border: '#fde047' };
      case 'high': return { bg: '#ffedd5', text: '#c2410c', border: '#fdba74' };
      case 'severe': return { bg: '#fee2e2', text: '#b91c1c', border: '#fca5a5' };
      default: return { bg: '#e2e8f0', text: '#475569', border: '#cbd5e1' };
    }
  };

  return (
    <div style={{ minHeight: '100vh', background: 'var(--bg-page)', paddingBottom: '3rem' }}>
      <Navbar />

      <main className="app-container" style={{ paddingTop: '1.5rem' }}>
        {/* Header Hero Banner */}
        <div className="mint-card" style={{ marginBottom: '2rem', borderRadius: 'var(--radius-lg)' }}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: '1rem' }}>
            <div>
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.5rem' }}>
                <span className="badge badge-mint" style={{ display: 'inline-flex', alignItems: 'center', gap: '0.3rem' }}>
                  <Sparkles size={14} /> AI XGBoost + SHAP Engine
                </span>
                <span className="badge badge-blue">POST /api/v1/predict</span>
              </div>
              <h1 style={{ fontSize: '1.75rem', fontWeight: 700, color: 'var(--text-main)', marginBottom: '0.4rem' }}>
                Nutritional Deficiency Risk Predictor
              </h1>
              <p style={{ color: 'var(--text-muted)', fontSize: '0.95rem', maxWidth: '700px' }}>
                Enter your health biometrics, daily nutrient intakes (% RDA), lab biomarkers, and physical symptoms to get real-time machine learning risk scores and SHAP explainability.
              </p>
            </div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
              <div style={{ textAlign: 'right', background: '#ffffff', padding: '0.75rem 1.25rem', borderRadius: 'var(--radius-md)', border: '1px solid var(--border-mint)' }}>
                <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', fontWeight: 600 }}>MODEL ACCURACY</div>
                <div style={{ fontSize: '1.25rem', fontWeight: 700, color: 'var(--primary-emerald)' }}>94.2% ROC-AUC</div>
              </div>
            </div>
          </div>
        </div>

        {/* Quick Test Presets */}
        <div style={{ marginBottom: '1.75rem' }}>
          <div style={{ fontSize: '0.875rem', fontWeight: 600, color: 'var(--text-main)', marginBottom: '0.6rem', display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
            <Zap size={16} color="var(--primary-emerald)" /> Quick Test Profiles (Click to Load):
          </div>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))', gap: '0.75rem' }}>
            {PRESETS.map((p, idx) => (
              <button
                key={idx}
                type="button"
                onClick={() => handleApplyPreset(p.data)}
                style={{
                  background: '#ffffff',
                  border: '1px solid var(--border-subtle)',
                  borderRadius: 'var(--radius-md)',
                  padding: '0.75rem 1rem',
                  textAlign: 'left',
                  cursor: 'pointer',
                  transition: 'all 0.2s ease',
                  boxShadow: 'var(--shadow-sm)'
                }}
                onMouseEnter={(e) => (e.currentTarget.style.borderColor = 'var(--primary-emerald)')}
                onMouseLeave={(e) => (e.currentTarget.style.borderColor = 'var(--border-subtle)')}
              >
                <div style={{ fontWeight: 600, fontSize: '0.9rem', color: 'var(--text-main)' }}>{p.name}</div>
                <div style={{ fontSize: '0.78rem', color: 'var(--text-muted)', marginTop: '0.25rem' }}>{p.desc}</div>
              </button>
            ))}
          </div>
        </div>

        {/* Main Content Grid: Form (Left) & Results (Right) */}
        <div style={{ display: 'grid', gridTemplateColumns: result ? '1fr 1fr' : '1fr', gap: '1.5rem' }}>
          
          {/* Input Form Card */}
          <div className="app-card" style={{ padding: '1.5rem' }}>
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '1rem', borderBottom: '1px solid var(--border-subtle)', paddingBottom: '0.75rem' }}>
              <h2 style={{ fontSize: '1.15rem', fontWeight: 700, color: 'var(--text-main)' }}>
                Input Health & Nutrition Data
              </h2>
              <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>
                {formData.symptoms_count} symptoms selected
              </span>
            </div>

            {/* Form Section Navigation Tabs */}
            <div style={{ display: 'flex', gap: '0.5rem', marginBottom: '1.25rem', overflowX: 'auto', paddingBottom: '0.25rem' }}>
              {[
                { id: 'demographics', label: '1. Demographics' },
                { id: 'nutrients', label: '2. Nutrient % RDA' },
                { id: 'biomarkers', label: '3. Lab Biomarkers' },
                { id: 'symptoms', label: '4. Symptoms' },
              ].map(tab => (
                <button
                  key={tab.id}
                  type="button"
                  onClick={() => setActiveTab(tab.id as any)}
                  style={{
                    padding: '0.4rem 0.85rem',
                    fontSize: '0.85rem',
                    fontWeight: activeTab === tab.id ? 600 : 500,
                    borderRadius: 'var(--radius-sm)',
                    border: 'none',
                    background: activeTab === tab.id ? 'var(--primary-emerald)' : '#f1f5f9',
                    color: activeTab === tab.id ? '#ffffff' : 'var(--text-main)',
                    cursor: 'pointer',
                    whiteSpace: 'nowrap',
                    transition: 'all 0.15s ease'
                  }}
                >
                  {tab.label}
                </button>
              ))}
            </div>

            <form onSubmit={handleSubmit}>
              {/* TAB 1: Demographics & Lifestyle */}
              {activeTab === 'demographics' && (
                <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
                  <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem' }}>
                    <div>
                      <label className="form-label">Age (Years)</label>
                      <input
                        type="number"
                        className="form-input"
                        value={formData.age || ''}
                        onChange={(e) => handleInputChange('age', Number(e.target.value))}
                        min={1}
                        max={120}
                        required
                      />
                    </div>
                    <div>
                      <label className="form-label">Gender</label>
                      <select
                        className="form-select"
                        value={formData.gender || 'female'}
                        onChange={(e) => handleInputChange('gender', e.target.value)}
                      >
                        <option value="female">Female</option>
                        <option value="male">Male</option>
                        <option value="other">Other</option>
                      </select>
                    </div>
                  </div>

                  <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem' }}>
                    <div>
                      <label className="form-label">BMI (kg/m²)</label>
                      <input
                        type="number"
                        step="0.1"
                        className="form-input"
                        value={formData.bmi || ''}
                        onChange={(e) => handleInputChange('bmi', Number(e.target.value))}
                        required
                      />
                    </div>
                    <div>
                      <label className="form-label">Diet Type</label>
                      <select
                        className="form-select"
                        value={formData.diet_type || 'omnivore'}
                        onChange={(e) => handleInputChange('diet_type', e.target.value)}
                      >
                        <option value="omnivore">Omnivore</option>
                        <option value="vegetarian">Vegetarian</option>
                        <option value="vegan">Vegan</option>
                        <option value="keto">Keto</option>
                        <option value="paleo">Paleo</option>
                      </select>
                    </div>
                  </div>

                  <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem' }}>
                    <div>
                      <label className="form-label">Sun Exposure</label>
                      <select
                        className="form-select"
                        value={formData.sun_exposure || 'moderate'}
                        onChange={(e) => handleInputChange('sun_exposure', e.target.value)}
                      >
                        <option value="low">Low (&lt; 15 mins/day)</option>
                        <option value="moderate">Moderate (15–45 mins/day)</option>
                        <option value="high">High (&gt; 45 mins/day)</option>
                      </select>
                    </div>
                    <div>
                      <label className="form-label">Latitude Region</label>
                      <select
                        className="form-select"
                        value={formData.latitude_region || 'moderate'}
                        onChange={(e) => handleInputChange('latitude_region', e.target.value)}
                      >
                        <option value="low">Low (Equatorial / Tropical)</option>
                        <option value="moderate">Moderate (Subtropical / Mid-latitude)</option>
                        <option value="high">High (Northern / High Latitude)</option>
                      </select>
                    </div>
                  </div>

                  <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem' }}>
                    <div>
                      <label className="form-label">Exercise Level</label>
                      <select
                        className="form-select"
                        value={formData.exercise_level || 'moderate'}
                        onChange={(e) => handleInputChange('exercise_level', e.target.value)}
                      >
                        <option value="low">Low</option>
                        <option value="moderate">Moderate</option>
                        <option value="high">High</option>
                      </select>
                    </div>
                    <div>
                      <label className="form-label">Smoking Status</label>
                      <select
                        className="form-select"
                        value={formData.smoking_status || 'never'}
                        onChange={(e) => handleInputChange('smoking_status', e.target.value)}
                      >
                        <option value="never">Never</option>
                        <option value="former">Former</option>
                        <option value="current">Current</option>
                      </select>
                    </div>
                  </div>
                </div>
              )}

              {/* TAB 2: Nutrient Intake (% RDA) */}
              {activeTab === 'nutrients' && (
                <div>
                  <p style={{ fontSize: '0.82rem', color: 'var(--text-muted)', marginBottom: '1rem' }}>
                    Enter estimated intake as percentage of Recommended Daily Allowance (% RDA). Values &lt; 70% indicate inadequate intake.
                  </p>
                  <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '0.85rem' }}>
                    {[
                      { key: 'vitamin_d_percent_rda', label: 'Vitamin D (% RDA)' },
                      { key: 'iron_percent_rda', label: 'Iron (% RDA)' },
                      { key: 'vitamin_b12_percent_rda', label: 'Vitamin B12 (% RDA)' },
                      { key: 'folate_b9_percent_rda', label: 'Folate B9 (% RDA)' },
                      { key: 'vitamin_a_percent_rda', label: 'Vitamin A (% RDA)' },
                      { key: 'vitamin_c_percent_rda', label: 'Vitamin C (% RDA)' },
                      { key: 'calcium_percent_rda', label: 'Calcium (% RDA)' },
                      { key: 'magnesium_percent_rda', label: 'Magnesium (% RDA)' },
                    ].map(item => (
                      <div key={item.key}>
                        <label className="form-label" style={{ fontSize: '0.8rem' }}>{item.label}</label>
                        <input
                          type="number"
                          className="form-input"
                          value={(formData as any)[item.key] ?? ''}
                          onChange={(e) => handleInputChange(item.key as any, Number(e.target.value))}
                          min={0}
                          max={500}
                        />
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* TAB 3: Lab Biomarkers */}
              {activeTab === 'biomarkers' && (
                <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
                  <p style={{ fontSize: '0.82rem', color: 'var(--text-muted)' }}>
                    Serum blood test biomarker concentrations. Key diagnostic metrics evaluated by XGBoost:
                  </p>

                  <div>
                    <label className="form-label">Hemoglobin (g/dL)</label>
                    <input
                      type="number"
                      step="0.1"
                      className="form-input"
                      value={formData.hemoglobin_g_dl ?? ''}
                      onChange={(e) => handleInputChange('hemoglobin_g_dl', Number(e.target.value))}
                      placeholder="Normal: 12.0 - 15.5 g/dL"
                    />
                  </div>

                  <div>
                    <label className="form-label">Serum Vitamin D (ng/mL)</label>
                    <input
                      type="number"
                      step="0.1"
                      className="form-input"
                      value={formData.serum_vitamin_d_ng_ml ?? ''}
                      onChange={(e) => handleInputChange('serum_vitamin_d_ng_ml', Number(e.target.value))}
                      placeholder="Deficient: < 20 ng/mL"
                    />
                  </div>

                  <div>
                    <label className="form-label">Serum Vitamin B12 (pg/mL)</label>
                    <input
                      type="number"
                      step="1"
                      className="form-input"
                      value={formData.serum_vitamin_b12_pg_ml ?? ''}
                      onChange={(e) => handleInputChange('serum_vitamin_b12_pg_ml', Number(e.target.value))}
                      placeholder="Deficient: < 200 pg/mL"
                    />
                  </div>

                  <div>
                    <label className="form-label">Serum Folate (ng/mL)</label>
                    <input
                      type="number"
                      step="0.1"
                      className="form-input"
                      value={formData.serum_folate_ng_ml ?? ''}
                      onChange={(e) => handleInputChange('serum_folate_ng_ml', Number(e.target.value))}
                      placeholder="Deficient: < 4.0 ng/mL"
                    />
                  </div>
                </div>
              )}

              {/* TAB 4: Symptoms Checklist */}
              {activeTab === 'symptoms' && (
                <div>
                  <p style={{ fontSize: '0.82rem', color: 'var(--text-muted)', marginBottom: '1rem' }}>
                    Check all clinical symptoms currently present:
                  </p>
                  <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '0.6rem' }}>
                    {[
                      { key: 'has_fatigue', label: 'Fatigue / Tiredness' },
                      { key: 'has_weakness', label: 'Muscle Weakness' },
                      { key: 'has_dizziness', label: 'Dizziness / Lightheadedness' },
                      { key: 'has_pale_skin', label: 'Pale Skin' },
                      { key: 'has_bone_pain', label: 'Bone / Joint Pain' },
                      { key: 'has_muscle_cramps', label: 'Muscle Cramps' },
                      { key: 'has_numbness_tingling', label: 'Numbness / Tingling' },
                      { key: 'has_brittle_nails', label: 'Brittle Nails' },
                      { key: 'has_hair_loss', label: 'Hair Loss' },
                      { key: 'has_mouth_sores', label: 'Mouth Sores / Glossitis' },
                      { key: 'has_night_blindness', label: 'Night Blindness' },
                      { key: 'has_slow_wound_healing', label: 'Slow Wound Healing' },
                    ].map(symptom => (
                      <label
                        key={symptom.key}
                        style={{
                          display: 'flex',
                          alignItems: 'center',
                          gap: '0.5rem',
                          fontSize: '0.85rem',
                          color: 'var(--text-main)',
                          padding: '0.5rem 0.65rem',
                          borderRadius: 'var(--radius-sm)',
                          background: (formData as any)[symptom.key] ? 'var(--bg-mint)' : '#f8fafc',
                          border: `1px solid ${(formData as any)[symptom.key] ? 'var(--border-mint)' : '#e2e8f0'}`,
                          cursor: 'pointer',
                          userSelect: 'none'
                        }}
                      >
                        <input
                          type="checkbox"
                          checked={Boolean((formData as any)[symptom.key])}
                          onChange={(e) => handleInputChange(symptom.key as any, e.target.checked)}
                          style={{ accentColor: 'var(--primary-emerald)' }}
                        />
                        {symptom.label}
                      </label>
                    ))}
                  </div>
                </div>
              )}

              {/* Submit Error Alert */}
              {error && (
                <div style={{ marginTop: '1rem', padding: '0.75rem 1rem', borderRadius: 'var(--radius-md)', background: '#fee2e2', border: '1px solid #fca5a5', color: '#991b1b', fontSize: '0.85rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                  <AlertTriangle size={18} />
                  <span>{error}</span>
                </div>
              )}

              {/* Form Action Controls */}
              <div style={{ display: 'flex', gap: '0.75rem', marginTop: '1.5rem', borderTop: '1px solid var(--border-subtle)', paddingTop: '1rem' }}>
                <button
                  type="submit"
                  disabled={loading}
                  className="btn-primary"
                  style={{ flex: 1, display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '0.5rem', padding: '0.75rem' }}
                >
                  {loading ? (
                    <>
                      <Loader2 size={18} className="spin-icon" /> Evaluating XGBoost + SHAP...
                    </>
                  ) : (
                    <>
                      <Sparkles size={18} /> Predict Deficiency Risk
                    </>
                  )}
                </button>
              </div>
            </form>
          </div>

          {/* Results Output Card */}
          {result && (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>
              
              {/* Primary Prediction Banner */}
              <div 
                className="app-card" 
                style={{ 
                  padding: '1.5rem',
                  borderLeft: `6px solid ${getRiskBadgeColor(result.risk_level).text}`,
                  background: '#ffffff'
                }}
              >
                <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '0.75rem' }}>
                  <span style={{ fontSize: '0.78rem', fontWeight: 600, color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
                    PRIMARY PREDICTED TARGET
                  </span>
                  <span 
                    style={{ 
                      background: getRiskBadgeColor(result.risk_level).bg, 
                      color: getRiskBadgeColor(result.risk_level).text,
                      border: `1px solid ${getRiskBadgeColor(result.risk_level).border}`,
                      padding: '0.25rem 0.75rem',
                      borderRadius: '9999px',
                      fontSize: '0.8rem',
                      fontWeight: 700,
                      display: 'inline-flex',
                      alignItems: 'center',
                      gap: '0.3rem'
                    }}
                  >
                    <ShieldAlert size={14} /> {result.risk_level.toUpperCase()} RISK
                  </span>
                </div>

                <h3 style={{ fontSize: '1.5rem', fontWeight: 800, color: 'var(--text-main)', marginBottom: '0.5rem' }}>
                  {result.predicted_class}
                </h3>

                {/* Key Metrics Row */}
                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem', marginTop: '1rem', background: '#f8fafc', padding: '1rem', borderRadius: 'var(--radius-md)' }}>
                  <div>
                    <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', fontWeight: 600 }}>CONFIDENCE PROBABILITY</div>
                    <div style={{ fontSize: '1.35rem', fontWeight: 700, color: 'var(--primary-emerald)' }}>
                      {(result.predicted_probability * 100).toFixed(1)}%
                    </div>
                  </div>
                  <div>
                    <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', fontWeight: 600 }}>RISK SCORE (0–100)</div>
                    <div style={{ fontSize: '1.35rem', fontWeight: 700, color: getRiskBadgeColor(result.risk_level).text }}>
                      {result.risk_score} / 100
                    </div>
                  </div>
                </div>

                {/* Risk Score Progress Bar */}
                <div style={{ marginTop: '1rem' }}>
                  <div style={{ height: '8px', width: '100%', background: '#e2e8f0', borderRadius: '4px', overflow: 'hidden' }}>
                    <div 
                      style={{ 
                        height: '100%', 
                        width: `${Math.min(100, Math.max(0, result.risk_score))}%`, 
                        background: getRiskBadgeColor(result.risk_level).text,
                        transition: 'width 0.5s ease-in-out'
                      }} 
                    />
                  </div>
                </div>
              </div>

              {/* Multi-Class Probability Distribution */}
              <div className="app-card" style={{ padding: '1.5rem' }}>
                <h4 style={{ fontSize: '1rem', fontWeight: 700, color: 'var(--text-main)', marginBottom: '1rem', display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
                  <Activity size={18} color="var(--primary-emerald)" /> Class Probabilities Distribution
                </h4>

                <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
                  {Object.entries(result.class_probabilities).map(([className, prob]) => {
                    const pct = (prob * 100).toFixed(1);
                    const isSelected = className === result.predicted_class;
                    return (
                      <div key={className}>
                        <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.85rem', marginBottom: '0.25rem' }}>
                          <span style={{ fontWeight: isSelected ? 700 : 500, color: isSelected ? 'var(--text-main)' : 'var(--text-muted)' }}>
                            {className} {isSelected && ' (Predicted)'}
                          </span>
                          <span style={{ fontWeight: 600, color: isSelected ? 'var(--primary-emerald)' : 'var(--text-muted)' }}>
                            {pct}%
                          </span>
                        </div>
                        <div style={{ height: '6px', background: '#f1f5f9', borderRadius: '3px', overflow: 'hidden' }}>
                          <div 
                            style={{ 
                              height: '100%', 
                              width: `${pct}%`, 
                              background: isSelected ? 'var(--primary-emerald)' : '#cbd5e1',
                              transition: 'width 0.4s ease'
                            }} 
                          />
                        </div>
                      </div>
                    );
                  })}
                </div>
              </div>

              {/* SHAP Feature Explanations Card */}
              <div className="app-card" style={{ padding: '1.5rem' }}>
                <h4 style={{ fontSize: '1rem', fontWeight: 700, color: 'var(--text-main)', marginBottom: '0.4rem', display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
                  <Sparkles size={18} color="#d97706" /> SHAP Feature Explanations
                </h4>
                <p style={{ fontSize: '0.8rem', color: 'var(--text-muted)', marginBottom: '1.25rem' }}>
                  Exact features driving the model prediction up (risk factors) or down (protective factors).
                </p>

                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem' }}>
                  {/* Positive SHAP Features (Increases Risk) */}
                  <div style={{ background: '#fff5f5', border: '1px solid #fed7d7', padding: '1rem', borderRadius: 'var(--radius-md)' }}>
                    <div style={{ fontSize: '0.82rem', fontWeight: 700, color: '#c53030', marginBottom: '0.75rem', display: 'flex', alignItems: 'center', gap: '0.3rem' }}>
                      <TrendingUp size={16} /> Top Risk Factors (+SHAP)
                    </div>
                    {result.explanation.top_positive_features.length === 0 ? (
                      <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>None identified</div>
                    ) : (
                      <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
                        {result.explanation.top_positive_features.map((item, i) => (
                          <div key={i} style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', fontSize: '0.8rem' }}>
                            <span style={{ color: '#742a2a', fontWeight: 500 }}>{item.feature}</span>
                            <span style={{ fontWeight: 700, color: '#e53e3e' }}>+{item.shap_value.toFixed(3)}</span>
                          </div>
                        ))}
                      </div>
                    )}
                  </div>

                  {/* Negative SHAP Features (Decreases Risk / Protective) */}
                  <div style={{ background: '#f0fdf4', border: '1px solid #bbf7d0', padding: '1rem', borderRadius: 'var(--radius-md)' }}>
                    <div style={{ fontSize: '0.82rem', fontWeight: 700, color: '#166534', marginBottom: '0.75rem', display: 'flex', alignItems: 'center', gap: '0.3rem' }}>
                      <TrendingDown size={16} /> Protective Factors (-SHAP)
                    </div>
                    {result.explanation.top_negative_features.length === 0 ? (
                      <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>None identified</div>
                    ) : (
                      <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
                        {result.explanation.top_negative_features.map((item, i) => (
                          <div key={i} style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', fontSize: '0.8rem' }}>
                            <span style={{ color: '#14532d', fontWeight: 500 }}>{item.feature}</span>
                            <span style={{ fontWeight: 700, color: '#16a34a' }}>{item.shap_value.toFixed(3)}</span>
                          </div>
                        ))}
                      </div>
                    )}
                  </div>
                </div>
              </div>

              {/* Medical Disclaimer Banner */}
              <div style={{ background: '#eff6ff', border: '1px solid #bfdbfe', borderRadius: 'var(--radius-md)', padding: '1rem', color: '#1e40af', fontSize: '0.82rem', display: 'flex', gap: '0.75rem', alignItems: 'flex-start' }}>
                <Info size={20} style={{ flexShrink: 0, marginTop: '0.1rem' }} />
                <div>
                  <div style={{ fontWeight: 700, marginBottom: '0.2rem' }}>Medical Disclaimer</div>
                  <div>{result.medical_disclaimer}</div>
                </div>
              </div>

            </div>
          )}

        </div>
      </main>
    </div>
  );
};

export default PredictionPage;
