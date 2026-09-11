import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { Navbar } from '../components/Navbar';
import { getMyHealthProfile, getDailyNutritionSummary } from '../services/api';
import { HealthProfile, DailyNutritionSummary } from '../types';
import { 
  UserCheck, 
  BookOpen, 
  Activity, 
  FileText, 
  Sparkles,
  ArrowRight, 
  Apple
} from 'lucide-react';

export const HomePage: React.FC = () => {
  const [profile, setProfile] = useState<HealthProfile | null>(null);
  const [todaySummary, setTodaySummary] = useState<DailyNutritionSummary | null>(null);

  useEffect(() => {
    loadDashboardData();
  }, []);

  const loadDashboardData = async () => {
    try {
      const today = new Date().toISOString().split('T')[0];
      const [profData, summaryData] = await Promise.allSettled([
        getMyHealthProfile(),
        getDailyNutritionSummary(today)
      ]);

      if (profData.status === 'fulfilled') setProfile(profData.value);
      if (summaryData.status === 'fulfilled') setTodaySummary(summaryData.value);
    } catch (err) {
      console.log('Dashboard data fetch error:', err);
    }
  };

  return (
    <div style={{ minHeight: '100vh', background: 'var(--bg-page)' }}>
      <Navbar />

      <main className="app-container">
        {/* Welcome Section */}
        <div className="mint-card" style={{ marginBottom: '2rem', borderRadius: 'var(--radius-lg)' }}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: '1.5rem' }}>
            <div>
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.4rem' }}>
                <span className="badge badge-mint">AI Nutrition Intelligence System</span>
                <span className="badge badge-blue">Week 1 & 2 Completed</span>
              </div>
              <h1 style={{ fontSize: '1.75rem', fontWeight: 700, color: 'var(--text-main)', marginBottom: '0.5rem' }}>
                Welcome to Your Health Dashboard
              </h1>
              <p style={{ color: 'var(--text-muted)', fontSize: '0.95rem', maxWidth: '600px' }}>
                Track your daily food intake, record physical symptoms, and manage structured blood test lab values in one simple, calm interface.
              </p>
            </div>
            {profile?.tdee && (
              <div style={{ background: '#ffffff', padding: '1rem 1.5rem', borderRadius: 'var(--radius-md)', border: '1px solid var(--border-mint)', boxShadow: 'var(--shadow-sm)' }}>
                <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)', fontWeight: 600 }}>DAILY TDEE TARGET</div>
                <div style={{ fontSize: '1.5rem', fontWeight: 700, color: 'var(--primary-emerald)' }}>
                  {profile.tdee} <span style={{ fontSize: '0.85rem', color: 'var(--text-muted)' }}>kcal</span>
                </div>
              </div>
            )}
          </div>
        </div>

        {/* Today's Overview Bar */}
        <h2 style={{ fontSize: '1.2rem', fontWeight: 700, marginBottom: '1rem', color: 'var(--text-main)', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
          <Apple size={20} color="var(--primary-emerald)" /> Today's Nutrition Summary
        </h2>

        <div className="grid-4" style={{ marginBottom: '2.5rem' }}>
          <div className="app-card" style={{ padding: '1.25rem' }}>
            <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)', fontWeight: 600 }}>CALORIES</div>
            <div style={{ fontSize: '1.5rem', fontWeight: 700, color: 'var(--text-main)', marginTop: '0.2rem' }}>
              {todaySummary?.total_calories || 0} <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>kcal</span>
            </div>
          </div>
          <div className="app-card" style={{ padding: '1.25rem' }}>
            <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)', fontWeight: 600 }}>PROTEIN</div>
            <div style={{ fontSize: '1.5rem', fontWeight: 700, color: 'var(--primary-emerald)', marginTop: '0.2rem' }}>
              {todaySummary?.total_protein_g || 0} <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>g</span>
            </div>
          </div>
          <div className="app-card" style={{ padding: '1.25rem' }}>
            <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)', fontWeight: 600 }}>CARBS</div>
            <div style={{ fontSize: '1.5rem', fontWeight: 700, color: '#0284c7', marginTop: '0.2rem' }}>
              {todaySummary?.total_carbs_g || 0} <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>g</span>
            </div>
          </div>
          <div className="app-card" style={{ padding: '1.25rem' }}>
            <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)', fontWeight: 600 }}>FAT</div>
            <div style={{ fontSize: '1.5rem', fontWeight: 700, color: '#d97706', marginTop: '0.2rem' }}>
              {todaySummary?.total_fat_g || 0} <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>g</span>
            </div>
          </div>
        </div>

        {/* Quick Feature Action Cards */}
        <h2 style={{ fontSize: '1.2rem', fontWeight: 700, marginBottom: '1rem', color: 'var(--text-main)' }}>
          Quick Actions
        </h2>

        <div className="grid-2" style={{ gap: '1.25rem' }}>
          {/* Profile Card */}
          <Link to="/profile" style={{ textDecoration: 'none' }}>
            <div className="app-card" style={{ padding: '1.5rem', display: 'flex', alignItems: 'flex-start', gap: '1rem', height: '100%' }}>
              <div style={{ background: 'var(--bg-mint)', padding: '0.75rem', borderRadius: '12px', color: 'var(--primary-emerald)' }}>
                <UserCheck size={24} />
              </div>
              <div style={{ flex: 1 }}>
                <h3 style={{ fontSize: '1.1rem', fontWeight: 700, color: 'var(--text-main)', marginBottom: '0.25rem' }}>
                  Health Profile & Goals
                </h3>
                <p style={{ fontSize: '0.875rem', color: 'var(--text-muted)', marginBottom: '0.75rem' }}>
                  Manage biometrics, dietary restrictions, health goals, and target period.
                </p>
                <span style={{ fontSize: '0.875rem', fontWeight: 600, color: 'var(--primary-emerald)', display: 'inline-flex', alignItems: 'center', gap: '0.3rem' }}>
                  Manage Profile <ArrowRight size={16} />
                </span>
              </div>
            </div>
          </Link>

          {/* Food Diary Card */}
          <Link to="/diary" style={{ textDecoration: 'none' }}>
            <div className="app-card" style={{ padding: '1.5rem', display: 'flex', alignItems: 'flex-start', gap: '1rem', height: '100%' }}>
              <div style={{ background: '#f0f9ff', padding: '0.75rem', borderRadius: '12px', color: '#0284c7' }}>
                <BookOpen size={24} />
              </div>
              <div style={{ flex: 1 }}>
                <h3 style={{ fontSize: '1.1rem', fontWeight: 700, color: 'var(--text-main)', marginBottom: '0.25rem' }}>
                  Food Diary & Search
                </h3>
                <p style={{ fontSize: '0.875rem', color: 'var(--text-muted)', marginBottom: '0.75rem' }}>
                  Log meals, search USDA & OpenFoodFacts databases, and track daily nutrition.
                </p>
                <span style={{ fontSize: '0.875rem', fontWeight: 600, color: '#0284c7', display: 'inline-flex', alignItems: 'center', gap: '0.3rem' }}>
                  Open Food Diary <ArrowRight size={16} />
                </span>
              </div>
            </div>
          </Link>

          {/* Symptom Assessment Card */}
          <Link to="/symptoms" style={{ textDecoration: 'none' }}>
            <div className="app-card" style={{ padding: '1.5rem', display: 'flex', alignItems: 'flex-start', gap: '1rem', height: '100%' }}>
              <div style={{ background: '#fffbeb', padding: '0.75rem', borderRadius: '12px', color: '#d97706' }}>
                <Activity size={24} />
              </div>
              <div style={{ flex: 1 }}>
                <h3 style={{ fontSize: '1.1rem', fontWeight: 700, color: 'var(--text-main)', marginBottom: '0.25rem' }}>
                  Symptom Assessment
                </h3>
                <p style={{ fontSize: '0.875rem', color: 'var(--text-muted)', marginBottom: '0.75rem' }}>
                  Record fatigue, hair loss, skin conditions, muscle weakness, and mood observations.
                </p>
                <span style={{ fontSize: '0.875rem', fontWeight: 600, color: '#d97706', display: 'inline-flex', alignItems: 'center', gap: '0.3rem' }}>
                  Record Symptoms <ArrowRight size={16} />
                </span>
              </div>
            </div>
          </Link>

          {/* Blood Test Results Card */}
          <Link to="/blood-tests" style={{ textDecoration: 'none' }}>
            <div className="app-card" style={{ padding: '1.5rem', display: 'flex', alignItems: 'flex-start', gap: '1rem', height: '100%' }}>
              <div style={{ background: '#fcf4ff', padding: '0.75rem', borderRadius: '12px', color: '#9333ea' }}>
                <FileText size={24} />
              </div>
              <div style={{ flex: 1 }}>
                <h3 style={{ fontSize: '1.1rem', fontWeight: 700, color: 'var(--text-main)', marginBottom: '0.25rem' }}>
                  Blood Test Results
                </h3>
                <p style={{ fontSize: '0.875rem', color: 'var(--text-muted)', marginBottom: '0.75rem' }}>
                  Enter recent lab values for Hemoglobin, Vitamin D, Vitamin B12, Iron, and Calcium.
                </p>
                <span style={{ fontSize: '0.875rem', fontWeight: 600, color: '#9333ea', display: 'inline-flex', alignItems: 'center', gap: '0.3rem' }}>
                  View Lab Values <ArrowRight size={16} />
                </span>
              </div>
            </div>
          </Link>

          {/* AI Risk Predictor Card */}
          <Link to="/predict" style={{ textDecoration: 'none' }}>
            <div className="app-card" style={{ padding: '1.5rem', display: 'flex', alignItems: 'flex-start', gap: '1rem', height: '100%', background: 'linear-gradient(135deg, #ffffff 0%, #f0fdf4 100%)', borderColor: 'var(--border-mint)' }}>
              <div style={{ background: 'var(--bg-mint)', padding: '0.75rem', borderRadius: '12px', color: 'var(--primary-emerald)' }}>
                <Sparkles size={24} />
              </div>
              <div style={{ flex: 1 }}>
                <h3 style={{ fontSize: '1.1rem', fontWeight: 700, color: 'var(--text-main)', marginBottom: '0.25rem', display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
                  AI Risk Predictor <span className="badge badge-mint" style={{ fontSize: '0.7rem' }}>XGBoost + SHAP</span>
                </h3>
                <p style={{ fontSize: '0.875rem', color: 'var(--text-muted)', marginBottom: '0.75rem' }}>
                  Evaluate real-time nutritional deficiency risks, class probabilities, and feature explanations using ML.
                </p>
                <span style={{ fontSize: '0.875rem', fontWeight: 600, color: 'var(--primary-emerald)', display: 'inline-flex', alignItems: 'center', gap: '0.3rem' }}>
                  Launch Predictor Engine <ArrowRight size={16} />
                </span>
              </div>
            </div>
          </Link>
        </div>
      </main>
    </div>
  );
};
