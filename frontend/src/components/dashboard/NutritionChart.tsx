import React from 'react';
import { DailyNutritionSummary } from '../../types';
import { BarChart2 } from 'lucide-react';

interface DailySummaryItem {
  date: string;
  summary: DailyNutritionSummary | null;
}

interface Props {
  data: DailySummaryItem[];
  tdeeTarget?: number;
}

export const NutritionChart: React.FC<Props> = ({ data, tdeeTarget = 2000 }) => {
  const maxCal = Math.max(tdeeTarget * 1.15, ...data.map(d => d.summary?.total_calories || 0), 1500);

  return (
    <div className="app-card" style={{ padding: '1.5rem', marginBottom: '1.5rem' }}>
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '1rem' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
          <BarChart2 size={20} style={{ color: 'var(--primary-emerald)' }} />
          <h3 style={{ fontSize: '1.05rem', fontWeight: 700, color: 'var(--text-main)' }}>
            7-Day Calorie Intake Trend
          </h3>
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: '1rem', fontSize: '0.75rem', color: 'var(--text-muted)' }}>
          <span style={{ display: 'inline-flex', alignItems: 'center', gap: '0.3rem' }}>
            <span style={{ width: '10px', height: '10px', background: 'var(--primary-emerald)', borderRadius: '2px' }} /> Logged Intake
          </span>
          <span style={{ display: 'inline-flex', alignItems: 'center', gap: '0.3rem' }}>
            <span style={{ width: '10px', height: '10px', background: '#cbd5e1', borderRadius: '2px' }} /> No Logged Data
          </span>
        </div>
      </div>

      {/* Responsive Bar Chart Container */}
      <div style={{ display: 'flex', alignItems: 'flex-end', justifyContent: 'space-between', gap: '0.5rem', height: '180px', paddingTop: '1.5rem', borderBottom: '1px solid var(--border-subtle)' }}>
        {data.map((item) => {
          const hasData = item.summary !== null && item.summary.entry_count > 0;
          const calories = item.summary?.total_calories || 0;
          const heightPercent = hasData ? Math.min(Math.round((calories / maxCal) * 100), 100) : 6;

          // Format short date e.g. "Mon 24"
          const dateObj = new Date(item.date + 'T00:00:00');
          const dayName = isNaN(dateObj.getTime()) ? item.date.slice(5) : dateObj.toLocaleDateString('en-US', { weekday: 'short', day: 'numeric' });

          return (
            <div
              key={item.date}
              style={{
                flex: 1,
                display: 'flex',
                flexDirection: 'column',
                alignItems: 'center',
                height: '100%',
                justifyContent: 'flex-end'
              }}
            >
              {/* Value Tooltip Label */}
              <span style={{ fontSize: '0.675rem', fontWeight: 600, color: hasData ? 'var(--text-main)' : 'var(--text-light)', marginBottom: '0.3rem' }}>
                {hasData ? `${Math.round(calories)}` : '—'}
              </span>

              {/* Bar element */}
              <div
                style={{
                  width: '80%',
                  maxWidth: '36px',
                  height: `${heightPercent}%`,
                  background: hasData ? 'linear-gradient(180deg, var(--primary-mint) 0%, var(--primary-emerald) 100%)' : '#e2e8f0',
                  borderRadius: '4px 4px 0 0',
                  transition: 'height 0.4s ease',
                  boxShadow: hasData ? '0 2px 4px rgba(22, 163, 74, 0.15)' : 'none'
                }}
                title={hasData ? `${item.date}: ${calories} kcal (${item.summary?.entry_count} entries)` : `${item.date}: No logged data`}
              />

              {/* Date X-axis label */}
              <span style={{ fontSize: '0.7rem', color: 'var(--text-muted)', marginTop: '0.5rem', textTransform: 'uppercase' }}>
                {dayName}
              </span>
            </div>
          );
        })}
      </div>
    </div>
  );
};
