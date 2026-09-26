import React from 'react';
import { Link } from 'react-router-dom';
import { DeficiencyPredictionResponse } from '../../types';
import { Sparkles, Info, ShieldAlert, Activity, FileText } from 'lucide-react';

interface Props {
  prediction: DeficiencyPredictionResponse | null;
  hasEnoughData: boolean;
}

export const DeficiencyRiskCard: React.FC<Props> = ({ prediction, hasEnoughData }) => {
  if (!hasEnoughData || !prediction) {
    return (
      <div className="app-card" style={{ padding: '1.5rem', marginBottom: '1.5rem' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.75rem' }}>
          <Sparkles size={20} style={{ color: 'var(--primary-emerald)' }} />
          <h3 style={{ fontSize: '1.05rem', fontWeight: 700, color: 'var(--text-main)' }}>
            AI Deficiency Risk Assessment
          </h3>
        </div>

        <div style={{ background: '#fffbeb', border: '1px solid #fef3c7', borderRadius: 'var(--radius-md)', padding: '1.25rem', textAlign: 'center' }}>
          <ShieldAlert size={36} style={{ color: 'var(--accent-amber)', marginBottom: '0.5rem' }} />
          <h4 style={{ fontSize: '0.95rem', fontWeight: 600, color: 'var(--text-main)', marginBottom: '0.3rem' }}>
            Insufficient Data for Deficiency Risk Assessment
          </h4>
          <p style={{ fontSize: '0.85rem', color: 'var(--text-muted)', maxWidth: '450px', margin: '0 auto 1rem auto', lineHeight: '1.5' }}>
            To generate accurate XGBoost deficiency risk predictions and SHAP feature attributions, please record your physical symptoms or enter blood test lab values.
          </p>

          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '0.75rem', flexWrap: 'wrap' }}>
            <Link to="/symptoms" className="btn-secondary" style={{ fontSize: '0.825rem', padding: '0.4rem 0.85rem' }}>
              <Activity size={16} /> Record Symptoms
            </Link>
            <Link to="/blood-tests" className="btn-secondary" style={{ fontSize: '0.825rem', padding: '0.4rem 0.85rem' }}>
              <FileText size={16} /> Enter Lab Values
            </Link>
          </div>
        </div>
      </div>
    );
  }

  const { predicted_class, risk_score, risk_level, explanation, medical_disclaimer } = prediction;
  const isHealthy = predicted_class === 'Healthy';
  const scorePercent = Math.min(Math.round(risk_score), 100);

  return (
    <div className="app-card" style={{ padding: '1.5rem', marginBottom: '1.5rem' }}>
      {/* Card Header */}
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '1rem', flexWrap: 'wrap', gap: '0.5rem' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
          <Sparkles size={20} style={{ color: 'var(--primary-emerald)' }} />
          <h3 style={{ fontSize: '1.05rem', fontWeight: 700, color: 'var(--text-main)' }}>
            AI Deficiency Risk Assessment
          </h3>
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
          <span className={`badge ${isHealthy ? 'badge-mint' : 'badge-amber'}`}>
            {predicted_class.replace('_', ' ')}
          </span>
          <span className="badge badge-blue">
            {risk_level}
          </span>
        </div>
      </div>

      {/* Risk Score Progress Bar */}
      <div style={{ marginBottom: '1rem', background: '#f8fafc', padding: '1rem', borderRadius: 'var(--radius-md)', border: '1px solid var(--border-subtle)' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.85rem', marginBottom: '0.4rem' }}>
          <span style={{ fontWeight: 600, color: 'var(--text-main)' }}>Overall Risk Score</span>
          <span style={{ fontWeight: 700, color: isHealthy ? 'var(--primary-emerald)' : 'var(--accent-amber)' }}>
            {scorePercent} / 100
          </span>
        </div>
        <div style={{ background: '#e2e8f0', height: '8px', borderRadius: '9999px', overflow: 'hidden' }}>
          <div style={{
            width: `${scorePercent}%`,
            background: isHealthy ? 'var(--primary-emerald)' : 'var(--accent-amber)',
            height: '100%',
            borderRadius: '9999px',
            transition: 'width 0.4s ease'
          }} />
        </div>
      </div>

      {/* SHAP Key Drivers */}
      {explanation && (explanation.top_positive_features.length > 0 || explanation.top_negative_features.length > 0) && (
        <div style={{ marginBottom: '1rem' }}>
          <div style={{ fontSize: '0.8rem', fontWeight: 600, color: 'var(--text-muted)', marginBottom: '0.4rem' }}>
            Key AI Feature Drivers (SHAP)
          </div>
          <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.4rem' }}>
            {explanation.top_positive_features.map((feat) => (
              <span key={feat.feature} className="badge badge-amber" style={{ fontSize: '0.725rem' }}>
                ⚠️ {feat.feature.replace(/_/g, ' ')} (+{feat.shap_value.toFixed(2)})
              </span>
            ))}
            {explanation.top_negative_features.map((feat) => (
              <span key={feat.feature} className="badge badge-mint" style={{ fontSize: '0.725rem' }}>
                ✅ {feat.feature.replace(/_/g, ' ')} ({feat.shap_value.toFixed(2)})
              </span>
            ))}
          </div>
        </div>
      )}

      {/* Medical Disclaimer */}
      <div style={{
        fontSize: '0.75rem',
        color: 'var(--text-muted)',
        background: '#f8fafc',
        padding: '0.6rem 0.85rem',
        borderRadius: 'var(--radius-sm)',
        display: 'flex',
        alignItems: 'center',
        gap: '0.4rem'
      }}>
        <Info size={14} style={{ color: 'var(--primary-emerald)', flexShrink: 0 }} />
        <span>{medical_disclaimer}</span>
      </div>
    </div>
  );
};
