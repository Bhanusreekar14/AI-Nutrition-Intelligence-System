import React from 'react';
import { DailyNutritionSummary, HealthProfile } from '../../types';
import { Flame, Activity, Zap, ShieldCheck } from 'lucide-react';

interface Props {
  summary: DailyNutritionSummary | null;
  profile: HealthProfile | null;
}

export const NutritionSummaryCards: React.FC<Props> = ({ summary, profile }) => {
  const tdee = profile?.tdee || 2000;
  const targetProteinG = Math.round((tdee * 0.25) / 4); // 25% of calories from protein (4 kcal/g)
  const targetCarbsG = Math.round((tdee * 0.50) / 4);   // 50% of calories from carbs (4 kcal/g)
  const targetFatG = Math.round((tdee * 0.25) / 9);     // 25% of calories from fat (9 kcal/g)

  const consumedCalories = summary?.total_calories || 0;
  const consumedProtein = summary?.total_protein_g || 0;
  const consumedCarbs = summary?.total_carbs_g || 0;
  const consumedFat = summary?.total_fat_g || 0;

  const calPercent = Math.min(Math.round((consumedCalories / tdee) * 100), 100);
  const proteinPercent = Math.min(Math.round((consumedProtein / targetProteinG) * 100), 100);
  const carbsPercent = Math.min(Math.round((consumedCarbs / targetCarbsG) * 100), 100);
  const fatPercent = Math.min(Math.round((consumedFat / targetFatG) * 100), 100);

  return (
    <div className="grid-4" style={{ marginBottom: '1.5rem', gap: '1rem' }}>
      {/* Calories Card */}
      <div className="app-card" style={{ padding: '1.25rem', position: 'relative' }}>
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '0.4rem' }}>
          <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)', fontWeight: 600, textTransform: 'uppercase' }}>
            Calories Intake
          </span>
          <Flame size={18} style={{ color: 'var(--primary-emerald)' }} />
        </div>
        <div style={{ fontSize: '1.5rem', fontWeight: 700, color: 'var(--text-main)' }}>
          {consumedCalories.toLocaleString()} <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>/ {tdee} kcal</span>
        </div>
        <div style={{ marginTop: '0.6rem', background: '#e2e8f0', borderRadius: '9999px', height: '6px', overflow: 'hidden' }}>
          <div style={{ width: `${calPercent}%`, background: 'var(--primary-emerald)', height: '100%', borderRadius: '9999px', transition: 'width 0.4s ease' }} />
        </div>
        <div style={{ fontSize: '0.7rem', color: 'var(--text-muted)', marginTop: '0.3rem', textAlign: 'right' }}>
          {calPercent}% of Daily TDEE
        </div>
      </div>

      {/* Protein Card */}
      <div className="app-card" style={{ padding: '1.25rem' }}>
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '0.4rem' }}>
          <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)', fontWeight: 600, textTransform: 'uppercase' }}>
            Protein Target
          </span>
          <Activity size={18} style={{ color: '#16a34a' }} />
        </div>
        <div style={{ fontSize: '1.5rem', fontWeight: 700, color: 'var(--primary-emerald)' }}>
          {consumedProtein} <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>/ {targetProteinG} g</span>
        </div>
        <div style={{ marginTop: '0.6rem', background: '#e2e8f0', borderRadius: '9999px', height: '6px', overflow: 'hidden' }}>
          <div style={{ width: `${proteinPercent}%`, background: '#16a34a', height: '100%', borderRadius: '9999px', transition: 'width 0.4s ease' }} />
        </div>
        <div style={{ fontSize: '0.7rem', color: 'var(--text-muted)', marginTop: '0.3rem', textAlign: 'right' }}>
          {proteinPercent}% Goal
        </div>
      </div>

      {/* Carbs Card */}
      <div className="app-card" style={{ padding: '1.25rem' }}>
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '0.4rem' }}>
          <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)', fontWeight: 600, textTransform: 'uppercase' }}>
            Carbohydrates
          </span>
          <Zap size={18} style={{ color: '#0284c7' }} />
        </div>
        <div style={{ fontSize: '1.5rem', fontWeight: 700, color: '#0284c7' }}>
          {consumedCarbs} <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>/ {targetCarbsG} g</span>
        </div>
        <div style={{ marginTop: '0.6rem', background: '#e2e8f0', borderRadius: '9999px', height: '6px', overflow: 'hidden' }}>
          <div style={{ width: `${carbsPercent}%`, background: '#0284c7', height: '100%', borderRadius: '9999px', transition: 'width 0.4s ease' }} />
        </div>
        <div style={{ fontSize: '0.7rem', color: 'var(--text-muted)', marginTop: '0.3rem', textAlign: 'right' }}>
          {carbsPercent}% Goal
        </div>
      </div>

      {/* Fat Card */}
      <div className="app-card" style={{ padding: '1.25rem' }}>
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '0.4rem' }}>
          <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)', fontWeight: 600, textTransform: 'uppercase' }}>
            Total Fat
          </span>
          <ShieldCheck size={18} style={{ color: '#d97706' }} />
        </div>
        <div style={{ fontSize: '1.5rem', fontWeight: 700, color: '#d97706' }}>
          {consumedFat} <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>/ {targetFatG} g</span>
        </div>
        <div style={{ marginTop: '0.6rem', background: '#e2e8f0', borderRadius: '9999px', height: '6px', overflow: 'hidden' }}>
          <div style={{ width: `${fatPercent}%`, background: '#d97706', height: '100%', borderRadius: '9999px', transition: 'width 0.4s ease' }} />
        </div>
        <div style={{ fontSize: '0.7rem', color: 'var(--text-muted)', marginTop: '0.3rem', textAlign: 'right' }}>
          {fatPercent}% Limit
        </div>
      </div>
    </div>
  );
};
