import React, { useEffect, useState, useCallback } from 'react';
import { getPredictionProgress } from '../../services/api';
import { PredictionProgress } from '../../types';
import {
  TrendingUp,
  TrendingDown,
  Activity,
  Info,
  AlertCircle,
  Clock,
  RefreshCw,
  FileText
} from 'lucide-react';

interface Props {
  className?: string;
}

export const LongitudinalProgressTracker: React.FC<Props> = ({ className = '' }) => {
  const [selectedWeeks, setSelectedWeeks] = useState<number>(4);
  const [progress, setProgress] = useState<PredictionProgress | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  const fetchProgress = useCallback(async (weeks: number) => {
    setLoading(true);
    setError(null);
    try {
      const data = await getPredictionProgress(weeks);
      setProgress(data);
    } catch {
      setError('Unable to load longitudinal health progress.');
      setProgress(null);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchProgress(selectedWeeks);
  }, [selectedWeeks, fetchProgress]);

  const handleWindowChange = (weeks: number) => {
    if (weeks === selectedWeeks) return;
    setSelectedWeeks(weeks);
  };

  const formatDate = (dateStr: string) => {
    if (!dateStr) return '';
    try {
      const d = new Date(dateStr);
      return d.toLocaleDateString(undefined, { month: 'short', day: 'numeric' });
    } catch {
      return dateStr;
    }
  };

  const getRiskColor = (level?: string | null) => {
    if (!level) return 'var(--text-muted)';
    const l = level.toLowerCase();
    if (l.includes('high')) return '#e11d48';
    if (l.includes('moderate')) return '#d97706';
    if (l.includes('low')) return '#10b981';
    return 'var(--primary-emerald)';
  };

  return (
    <div className={`app-card ${className}`} style={{ padding: '1.5rem', marginBottom: '1.5rem' }}>
      {/* Header & Window Segment Selector */}
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '1.25rem', flexWrap: 'wrap', gap: '1rem' }}>
        <div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            <Activity size={22} style={{ color: 'var(--primary-emerald)' }} />
            <h3 style={{ fontSize: '1.15rem', fontWeight: 700, color: 'var(--text-main)', margin: 0 }}>
              Longitudinal Health Progress
            </h3>
          </div>
          <p style={{ fontSize: '0.85rem', color: 'var(--text-muted)', marginTop: '0.2rem', margin: 0 }}>
            Track your deficiency-risk history over 4, 8, and 12 weeks.
          </p>
        </div>

        {/* 4 / 8 / 12 Week Segmented Controls */}
        <div style={{ display: 'flex', alignItems: 'center', background: '#f1f5f9', borderRadius: 'var(--radius-md)', padding: '0.25rem', border: '1px solid var(--border-subtle)' }}>
          {[4, 8, 12].map((weeks) => (
            <button
              key={weeks}
              onClick={() => handleWindowChange(weeks)}
              style={{
                padding: '0.45rem 0.85rem',
                fontSize: '0.8rem',
                fontWeight: selectedWeeks === weeks ? 700 : 500,
                color: selectedWeeks === weeks ? 'var(--primary-emerald)' : 'var(--text-muted)',
                background: selectedWeeks === weeks ? '#ffffff' : 'transparent',
                border: 'none',
                borderRadius: 'var(--radius-sm)',
                cursor: 'pointer',
                boxShadow: selectedWeeks === weeks ? '0 1px 3px rgba(0,0,0,0.08)' : 'none',
                transition: 'all 0.2s ease'
              }}
            >
              {weeks} Weeks
            </button>
          ))}
          <button
            onClick={() => fetchProgress(selectedWeeks)}
            style={{ padding: '0.45rem 0.6rem', background: 'transparent', border: 'none', cursor: 'pointer', color: 'var(--text-muted)', display: 'flex', alignItems: 'center' }}
            title="Refresh Progress"
          >
            <RefreshCw size={14} className={loading ? 'spin' : ''} />
          </button>
        </div>
      </div>

      {/* Loading State */}
      {loading ? (
        <div style={{ padding: '2.5rem', textAlign: 'center', color: 'var(--text-muted)' }}>
          <div style={{
            display: 'inline-block',
            width: '32px',
            height: '32px',
            border: '3px solid var(--border-mint)',
            borderTopColor: 'var(--primary-emerald)',
            borderRadius: '50%',
            animation: 'spin 0.8s linear infinite'
          }} />
          <p style={{ marginTop: '0.75rem', fontSize: '0.875rem' }}>Loading longitudinal health history...</p>
        </div>
      ) : error ? (
        <div className="alert-error" style={{ fontSize: '0.875rem', margin: 0 }}>
          <AlertCircle size={18} />
          <span>{error}</span>
        </div>
      ) : !progress || progress.status === 'insufficient_history' || progress.total_snapshots === 0 ? (
        /* Empty / Insufficient History State */
        <div style={{ background: '#f8fafc', borderRadius: 'var(--radius-md)', padding: '2rem 1.5rem', textAlign: 'center', border: '1px border-subtle' }}>
          <Clock size={36} style={{ color: 'var(--text-light)', marginBottom: '0.5rem' }} />
          <h4 style={{ fontSize: '1rem', fontWeight: 600, color: 'var(--text-main)', marginBottom: '0.35rem' }}>
            Insufficient History for {selectedWeeks}-Week Tracking
          </h4>
          <p style={{ fontSize: '0.875rem', color: 'var(--text-muted)', maxWidth: '520px', margin: '0 auto 1rem auto', lineHeight: 1.5 }}>
            {progress?.message || 'No historical deficiency-risk snapshots are available yet. Continue using the app and complete periodic health assessments to build your progress history.'}
          </p>
          <div style={{ display: 'inline-flex', alignItems: 'center', gap: '0.4rem', fontSize: '0.75rem', color: 'var(--text-muted)', background: '#ffffff', padding: '0.4rem 0.75rem', borderRadius: 'var(--radius-sm)', border: '1px solid var(--border-subtle)' }}>
            <Info size={14} style={{ color: 'var(--primary-emerald)' }} />
            <span>Snapshots are saved automatically when performing health risk predictions.</span>
          </div>
        </div>
      ) : (
        /* Complete History View */
        <div>
          {/* Summary Metric Cards */}
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '1rem', marginBottom: '1.5rem' }}>
            {/* Latest Risk Score Card */}
            <div style={{ background: '#f8fafc', padding: '1rem', borderRadius: 'var(--radius-md)', border: '1px solid var(--border-subtle)' }}>
              <div style={{ fontSize: '0.75rem', fontWeight: 600, color: 'var(--text-muted)', textTransform: 'uppercase' }}>
                LATEST RISK SCORE
              </div>
              <div style={{ fontSize: '1.5rem', fontWeight: 700, color: getRiskColor(progress.latest_risk_level), marginTop: '0.2rem' }}>
                {progress.latest_risk_score} <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>/ 100</span>
              </div>
              <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginTop: '0.2rem' }}>
                {progress.latest_risk_level} • {formatDate(progress.chronological_history[progress.chronological_history.length - 1]?.recorded_at)}
              </div>
            </div>

            {/* Window Trajectory Change Card */}
            <div style={{ background: '#f8fafc', padding: '1rem', borderRadius: 'var(--radius-md)', border: '1px solid var(--border-subtle)' }}>
              <div style={{ fontSize: '0.75rem', fontWeight: 600, color: 'var(--text-muted)', textTransform: 'uppercase' }}>
                {selectedWeeks}-WEEK SCORE CHANGE
              </div>
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem', marginTop: '0.2rem' }}>
                <span style={{
                  fontSize: '1.5rem',
                  fontWeight: 700,
                  color: (progress.risk_score_change || 0) < 0 ? '#10b981' : (progress.risk_score_change || 0) > 0 ? '#e11d48' : 'var(--text-main)'
                }}>
                  {(progress.risk_score_change || 0) > 0 ? `+${progress.risk_score_change}` : progress.risk_score_change}
                </span>
                {(progress.risk_score_change || 0) < 0 ? (
                  <TrendingDown size={20} style={{ color: '#10b981' }} />
                ) : (progress.risk_score_change || 0) > 0 ? (
                  <TrendingUp size={20} style={{ color: '#e11d48' }} />
                ) : null}
              </div>
              <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginTop: '0.2rem' }}>
                Baseline: {progress.first_risk_score} ({formatDate(progress.chronological_history[0]?.recorded_at)})
              </div>
            </div>

            {/* Risk Level Transition Card */}
            <div style={{ background: '#f8fafc', padding: '1rem', borderRadius: 'var(--radius-md)', border: '1px solid var(--border-subtle)' }}>
              <div style={{ fontSize: '0.75rem', fontWeight: 600, color: 'var(--text-muted)', textTransform: 'uppercase' }}>
                RISK LEVEL TRANSITION
              </div>
              <div style={{ fontSize: '0.95rem', fontWeight: 700, color: 'var(--text-main)', marginTop: '0.4rem' }}>
                {progress.transition_text}
              </div>
              <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginTop: '0.25rem' }}>
                Based on {progress.total_snapshots} recorded snapshot{progress.total_snapshots !== 1 ? 's' : ''}
              </div>
            </div>
          </div>

          {/* Risk Score Trajectory Chart */}
          <div style={{ marginBottom: '1.5rem', padding: '1.25rem', background: '#ffffff', borderRadius: 'var(--radius-md)', border: '1px solid var(--border-subtle)' }}>
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '1rem' }}>
              <h4 style={{ fontSize: '0.95rem', fontWeight: 700, color: 'var(--text-main)', margin: 0 }}>
                Deficiency Risk Score Trajectory
              </h4>
              <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>
                Lower score indicates lower deficiency risk
              </span>
            </div>

            {/* Clean SVG Line / Scatter Plot for Risk History */}
            <div style={{ height: '180px', width: '100%', position: 'relative' }}>
              <svg width="100%" height="100%" viewBox="0 0 500 160" preserveAspectRatio="none" style={{ overflow: 'visible' }}>
                {/* Horizontal reference grid lines */}
                <line x1="0" y1="20" x2="500" y2="20" stroke="#f1f5f9" strokeDasharray="4 4" />
                <line x1="0" y1="70" x2="500" y2="70" stroke="#f1f5f9" strokeDasharray="4 4" />
                <line x1="0" y1="120" x2="500" y2="120" stroke="#f1f5f9" strokeDasharray="4 4" />

                {/* Plot Data Line & Points */}
                {(() => {
                  const points = progress.chronological_history.map((entry, idx) => {
                    const total = progress.chronological_history.length;
                    const x = total === 1 ? 250 : 30 + (idx / (total - 1)) * 440;
                    // Risk score scale 0 to 100 mapped to Y 140 to 10
                    const y = 140 - (Math.min(Math.max(entry.risk_score, 0), 100) / 100) * 130;
                    return { x, y, score: entry.risk_score, date: entry.recorded_at, level: entry.risk_level, cls: entry.predicted_class };
                  });

                  const pathD = points.length > 1
                    ? points.reduce((acc, p, i) => i === 0 ? `M ${p.x} ${p.y}` : `${acc} L ${p.x} ${p.y}`, '')
                    : '';

                  return (
                    <g>
                      {pathD && (
                        <path d={pathD} fill="none" stroke="var(--primary-emerald)" strokeWidth="3" strokeLinecap="round" strokeLinejoin="round" />
                      )}
                      {points.map((p, idx) => (
                        <g key={idx}>
                          <circle cx={p.x} cy={p.y} r="6" fill="#ffffff" stroke={getRiskColor(p.level)} strokeWidth="3" />
                          <text x={p.x} y={p.y - 12} textAnchor="middle" fontSize="10" fontWeight="700" fill="var(--text-main)">
                            {p.score}
                          </text>
                          <text x={p.x} y="156" textAnchor="middle" fontSize="9" fill="var(--text-muted)">
                            {formatDate(p.date)}
                          </text>
                        </g>
                      ))}
                    </g>
                  );
                })()}
              </svg>
            </div>
          </div>

          {/* Dual Grid: Symptom Trend + Biomarker Evolution */}
          <div className="grid-2" style={{ gap: '1.25rem', marginBottom: '1rem' }}>
            {/* Symptom Trend Section */}
            <div style={{ background: '#ffffff', padding: '1.25rem', borderRadius: 'var(--radius-md)', border: '1px solid var(--border-subtle)' }}>
              <h4 style={{ fontSize: '0.9rem', fontWeight: 700, color: 'var(--text-main)', marginBottom: '0.75rem', display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
                <Activity size={16} style={{ color: 'var(--primary-emerald)' }} />
                Symptom Count Evolution
              </h4>

              {progress.symptom_trend.length === 0 ? (
                <div style={{ padding: '1.25rem', textAlign: 'center', background: '#f8fafc', borderRadius: 'var(--radius-sm)', color: 'var(--text-muted)', fontSize: '0.8rem' }}>
                  Not enough historical symptom records for this window.
                </div>
              ) : (
                <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
                  {progress.symptom_trend.slice(-5).map((pt, idx) => (
                    <div key={idx} style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', padding: '0.4rem 0.75rem', background: '#f8fafc', borderRadius: 'var(--radius-sm)', fontSize: '0.8rem' }}>
                      <span style={{ color: 'var(--text-muted)' }}>{formatDate(pt.date)}</span>
                      <span style={{ fontWeight: 600, color: pt.symptoms_count > 0 ? '#d97706' : '#10b981' }}>
                        {pt.symptoms_count} symptom{pt.symptoms_count !== 1 ? 's' : ''} recorded
                      </span>
                    </div>
                  ))}
                </div>
              )}
            </div>

            {/* Biomarker Trend Section */}
            <div style={{ background: '#ffffff', padding: '1.25rem', borderRadius: 'var(--radius-md)', border: '1px solid var(--border-subtle)' }}>
              <h4 style={{ fontSize: '0.9rem', fontWeight: 700, color: 'var(--text-main)', marginBottom: '0.75rem', display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
                <FileText size={16} style={{ color: '#0284c7' }} />
                Biomarker Measurements
              </h4>

              {progress.biomarker_trend.length === 0 || progress.available_biomarkers.length === 0 ? (
                <div style={{ padding: '1.25rem', textAlign: 'center', background: '#f8fafc', borderRadius: 'var(--radius-sm)', color: 'var(--text-muted)', fontSize: '0.8rem' }}>
                  Not enough historical laboratory data for this window.
                </div>
              ) : (
                <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
                  {progress.biomarker_trend.slice(-3).map((bt, idx) => (
                    <div key={idx} style={{ padding: '0.5rem 0.75rem', background: '#f8fafc', borderRadius: 'var(--radius-sm)', fontSize: '0.775rem' }}>
                      <div style={{ fontWeight: 600, color: 'var(--text-main)', marginBottom: '0.2rem' }}>
                        Test Date: {formatDate(bt.date)}
                      </div>
                      <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.6rem', color: 'var(--text-muted)' }}>
                        {bt.hemoglobin !== null && <span>Hb: <strong style={{ color: 'var(--text-main)' }}>{bt.hemoglobin} g/dL</strong></span>}
                        {bt.vitamin_d !== null && <span>Vit D: <strong style={{ color: 'var(--text-main)' }}>{bt.vitamin_d} ng/mL</strong></span>}
                        {bt.vitamin_b12 !== null && <span>Vit B12: <strong style={{ color: 'var(--text-main)' }}>{bt.vitamin_b12} pg/mL</strong></span>}
                        {bt.folate !== null && <span>Folate: <strong style={{ color: 'var(--text-main)' }}>{bt.folate} ng/mL</strong></span>}
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>

          {/* Mandatory Research/Educational Disclaimer Footer */}
          <div style={{ display: 'flex', alignItems: 'flex-start', gap: '0.5rem', background: '#fffbeb', border: '1px solid #fef3c7', padding: '0.75rem 1rem', borderRadius: 'var(--radius-sm)', fontSize: '0.75rem', color: '#b45309' }}>
            <Info size={16} style={{ flexShrink: 0, marginTop: '0.1rem' }} />
            <span>
              <strong>Research Disclaimer:</strong> Historical risk scores and progress trends are model-generated estimates for research and educational purposes. They are not medical diagnoses and should not replace clinical evaluation by a qualified healthcare professional.
            </span>
          </div>
        </div>
      )}
    </div>
  );
};
