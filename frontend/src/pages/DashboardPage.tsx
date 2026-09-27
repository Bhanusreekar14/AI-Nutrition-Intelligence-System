import React, { useEffect, useState, useCallback } from 'react';
import { Link } from 'react-router-dom';
import { Navbar } from '../components/Navbar';
import {
  getMyHealthProfile,
  getDailyNutritionSummary,
  getFoodDiaryEntries,
  getSymptomAssessments,
  getBloodTests,
  predictDeficiencyRisk,
  generateWeeklyMealPlan,
  replaceMealItem
} from '../services/api';
import {
  HealthProfile,
  DailyNutritionSummary,
  FoodDiaryEntry,
  DeficiencyPredictionRequest,
  DeficiencyPredictionResponse,
  WeeklyMealPlan,
  MealType,
  DietRecommendationRequest,
  MealReplacementRequest
} from '../types';
import { NutritionSummaryCards } from '../components/dashboard/NutritionSummaryCards';
import { NutritionChart } from '../components/dashboard/NutritionChart';
import { DeficiencyRiskCard } from '../components/dashboard/DeficiencyRiskCard';
import { WeeklyMealPlanView } from '../components/dashboard/WeeklyMealPlanView';
import { LongitudinalProgressTracker } from '../components/dashboard/LongitudinalProgressTracker';
import {
  UserCheck,
  BookOpen,
  Activity,
  Sparkles,
  Apple,
  AlertCircle,
  Plus,
  RefreshCw
} from 'lucide-react';

interface DailySummaryItem {
  date: string;
  summary: DailyNutritionSummary | null;
}

export const DashboardPage: React.FC = () => {
  const [profile, setProfile] = useState<HealthProfile | null>(null);
  const [todaySummary, setTodaySummary] = useState<DailyNutritionSummary | null>(null);
  const [todayEntries, setTodayEntries] = useState<FoodDiaryEntry[]>([]);
  const [weeklySummaries, setWeeklySummaries] = useState<DailySummaryItem[]>([]);

  const [prediction, setPrediction] = useState<DeficiencyPredictionResponse | null>(null);
  const [hasEnoughPredictionData, setHasEnoughPredictionData] = useState<boolean>(false);

  const [weeklyPlan, setWeeklyPlan] = useState<WeeklyMealPlan | null>(null);

  const [loading, setLoading] = useState<boolean>(true);
  const [loadingReplace, setLoadingReplace] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  // Helper to generate YYYY-MM-DD date strings for the last N days
  const getLastNDates = (n: number): string[] => {
    const dates: string[] = [];
    const now = new Date();
    for (let i = n - 1; i >= 0; i--) {
      const d = new Date(now);
      d.setDate(now.getDate() - i);
      dates.push(d.toISOString().split('T')[0]);
    }
    return dates;
  };

  const loadDashboardData = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const todayStr = new Date().toISOString().split('T')[0];
      const last7Dates = getLastNDates(7);

      // 1. Fetch Profile, Today's Summary & Today's Diary Entries in parallel
      const [profRes, todaySumRes, todayEntriesRes, symptomsRes, bloodRes] = await Promise.allSettled([
        getMyHealthProfile(),
        getDailyNutritionSummary(todayStr),
        getFoodDiaryEntries(todayStr),
        getSymptomAssessments(),
        getBloodTests()
      ]);

      const loadedProfile = profRes.status === 'fulfilled' ? profRes.value : null;
      setProfile(loadedProfile);

      if (todaySumRes.status === 'fulfilled') setTodaySummary(todaySumRes.value);
      if (todayEntriesRes.status === 'fulfilled') setTodayEntries(todayEntriesRes.value);

      // 2. Fetch past 7 days daily summaries for trend chart
      const weeklyPromises = last7Dates.map(d => getDailyNutritionSummary(d).catch(() => null));
      const weeklyResults = await Promise.all(weeklyPromises);
      const formattedWeekly: DailySummaryItem[] = last7Dates.map((d, idx) => ({
        date: d,
        summary: weeklyResults[idx]
      }));
      setWeeklySummaries(formattedWeekly);

      // 3. Inspect real symptoms and blood tests for XGBoost prediction
      const symptomsList = symptomsRes.status === 'fulfilled' ? symptomsRes.value : [];
      const bloodList = bloodRes.status === 'fulfilled' ? bloodRes.value : [];

      const hasSymptoms = symptomsList.length > 0;
      const hasBloodTests = bloodList.length > 0;

      let currentPrediction: DeficiencyPredictionResponse | null = null;

      // Calculate BMI only when loadedProfile height_cm and weight_kg are valid positive numbers
      const validHeight = loadedProfile?.height_cm && loadedProfile.height_cm > 0;
      const validWeight = loadedProfile?.weight_kg && loadedProfile.weight_kg > 0;
      const canCalculateBmi = Boolean(validHeight && validWeight);

      if (loadedProfile && canCalculateBmi && (hasSymptoms || hasBloodTests)) {
        setHasEnoughPredictionData(true);
        try {
          const heightM = loadedProfile.height_cm / 100;
          const calculatedBmi = Number((loadedProfile.weight_kg / (heightM * heightM)).toFixed(1));

          const latestBlood = hasBloodTests ? bloodList[0] : null;

          // Map profile gender
          const genderMap: Record<string, string> = {
            female: 'Female',
            male: 'Male'
          };
          const formattedGender = genderMap[loadedProfile.gender?.toLowerCase() || ''] || 'Male';

          // Map dietary_preference to diet_type
          const dietMap: Record<string, string> = {
            vegetarian: 'Vegetarian',
            vegan: 'Vegan',
            pescatarian: 'Pescatarian',
            omnivore: 'Omnivore'
          };
          const formattedDietType = dietMap[loadedProfile.dietary_preference?.toLowerCase() || ''] || 'Omnivore';

          // Map activity_level to exercise_level
          const exerciseMap: Record<string, string> = {
            sedentary: 'Sedentary',
            lightly_active: 'Light',
            moderately_active: 'Moderate',
            very_active: 'Active',
            extra_active: 'Active'
          };
          const formattedExerciseLevel = exerciseMap[loadedProfile.activity_level?.toLowerCase() || ''] || 'Moderate';

          // Map symptom flags from real symptom records (checking symptom or symptom_name)
          const hasSymptom = (keywords: string[]): boolean =>
            symptomsList.some(record => {
              const symName = (record.symptom || (record as any).symptom_name || '').toLowerCase();
              return keywords.some(kw => symName.includes(kw.toLowerCase()));
            });

          // Parse numeric blood test values safely
          const parseNum = (val: number | string | undefined | null): number | undefined => {
            if (val === undefined || val === null || val === '') return undefined;
            const n = typeof val === 'number' ? val : parseFloat(val);
            return isNaN(n) ? undefined : n;
          };

          const folateVal = (latestBlood as any)?.folate ?? (latestBlood as any)?.serum_folate;

          const predReq: DeficiencyPredictionRequest = {
            age: loadedProfile.age,
            bmi: calculatedBmi,
            gender: formattedGender,
            diet_type: formattedDietType,
            exercise_level: formattedExerciseLevel,
            smoking_status: 'Never',
            alcohol_consumption: 'Unknown',
            sun_exposure: 'Moderate',
            income_level: 'Middle',
            latitude_region: 'Mid',
            symptoms_count: symptomsList.length,
            has_night_blindness: hasSymptom(['night', 'blindness']),
            has_fatigue: hasSymptom(['fatigue']),
            has_bleeding_gums: hasSymptom(['gum', 'bleeding']),
            has_bone_pain: hasSymptom(['bone']),
            has_muscle_weakness: hasSymptom(['weakness', 'muscle']),
            has_numbness_tingling: hasSymptom(['numb', 'tingling']),
            has_memory_problems: hasSymptom(['memory']),
            has_pale_skin: hasSymptom(['pale', 'skin']),
            ...(parseNum(latestBlood?.hemoglobin) !== undefined && { hemoglobin_g_dl: parseNum(latestBlood?.hemoglobin) }),
            ...(parseNum(latestBlood?.vitamin_d) !== undefined && { serum_vitamin_d_ng_ml: parseNum(latestBlood?.vitamin_d) }),
            ...(parseNum(latestBlood?.vitamin_b12) !== undefined && { serum_vitamin_b12_pg_ml: parseNum(latestBlood?.vitamin_b12) }),
            ...(parseNum(folateVal) !== undefined && { serum_folate_ng_ml: parseNum(folateVal) })
          };

          currentPrediction = await predictDeficiencyRisk(predReq);
          setPrediction(currentPrediction);
        } catch {
          setHasEnoughPredictionData(false);
          setPrediction(null);
        }
      } else {
        setHasEnoughPredictionData(false);
        setPrediction(null);
      }

      // 4. Generate 7-Day Meal Plan using real deficiency class or healthy baseline
      const targetClass = currentPrediction ? currentPrediction.predicted_class : 'Healthy';
      const targetScore = currentPrediction ? currentPrediction.risk_score : 50.0;
      const targetLevel = currentPrediction ? currentPrediction.risk_level : 'Moderate Risk';

      const mealPlanReq: DietRecommendationRequest = {
        predicted_class: targetClass,
        deficiency_class: targetClass,
        risk_level: targetLevel,
        risk_score: targetScore,
        dietary_preference: loadedProfile?.dietary_preference || 'omnivore',
        allergies_intolerances: loadedProfile?.allergies_intolerances || [],
        allergies: loadedProfile?.allergies_intolerances || [],
        limit: 50
      };

      const planRes = await generateWeeklyMealPlan(mealPlanReq);
      setWeeklyPlan(planRes);

    } catch (err: any) {
      setError(err.response?.data?.detail || err.message || 'Failed to load dashboard data.');
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    loadDashboardData();
  }, [loadDashboardData]);

  // Meal Replacement Action Handler
  const handleReplaceItem = async (dayNum: number, mealType: MealType, foodName: string) => {
    if (!weeklyPlan) return;
    setLoadingReplace(true);
    try {
      const payload: MealReplacementRequest = {
        weekly_plan: weeklyPlan,
        day: dayNum,
        meal_type: mealType,
        target_food_name: foodName,
        dietary_preference: profile?.dietary_preference || 'omnivore',
        allergies_intolerances: profile?.allergies_intolerances || [],
        predicted_class: prediction ? prediction.predicted_class : 'Healthy',
        risk_level: prediction ? prediction.risk_level : 'Moderate Risk',
        risk_score: prediction ? prediction.risk_score : 50.0
      };
      const repRes = await replaceMealItem(payload);
      setWeeklyPlan(repRes.updated_weekly_plan);
    } catch (err: any) {
      alert(err.response?.data?.detail || err.message || 'Failed to replace meal item.');
    } finally {
      setLoadingReplace(false);
    }
  };

  return (
    <div style={{ minHeight: '100vh', background: 'var(--bg-page)' }}>
      <Navbar />

      <main className="app-container">
        {/* Header / Welcome Section */}
        <div className="mint-card" style={{ marginBottom: '1.5rem', borderRadius: 'var(--radius-lg)' }}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: '1rem' }}>
            <div>
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.3rem' }}>
                <span className="badge badge-mint">AI Nutrition Intelligence System</span>
                <span className="badge badge-blue">Real-Time Intelligence</span>
              </div>
              <h1 style={{ fontSize: '1.65rem', fontWeight: 700, color: 'var(--text-main)', marginBottom: '0.4rem' }}>
                Nutrition & Health Intelligence Dashboard
              </h1>
              <p style={{ color: 'var(--text-muted)', fontSize: '0.925rem', maxWidth: '650px' }}>
                Monitor daily calorie and macro targets, track weekly intake trends, evaluate XGBoost deficiency risk, and generate personalized 7-day meal plans.
              </p>
            </div>

            <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
              {profile?.tdee && (
                <div style={{ background: '#ffffff', padding: '0.85rem 1.25rem', borderRadius: 'var(--radius-md)', border: '1px solid var(--border-mint)' }}>
                  <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', fontWeight: 600 }}>DAILY TDEE TARGET</div>
                  <div style={{ fontSize: '1.35rem', fontWeight: 700, color: 'var(--primary-emerald)' }}>
                    {profile.tdee} <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>kcal</span>
                  </div>
                </div>
              )}
              <button
                onClick={loadDashboardData}
                className="btn-secondary"
                style={{ padding: '0.6rem 0.85rem' }}
                title="Refresh Dashboard"
                disabled={loading}
              >
                <RefreshCw size={16} />
              </button>
            </div>
          </div>
        </div>

        {/* Global Error Banner */}
        {error && (
          <div className="alert-error" style={{ marginBottom: '1.5rem' }}>
            <AlertCircle size={20} />
            <span>{error}</span>
          </div>
        )}

        {/* Global Loading Spinner */}
        {loading ? (
          <div className="app-card" style={{ padding: '4rem', textAlign: 'center', marginBottom: '2rem' }}>
            <div style={{
              display: 'inline-block',
              width: '40px',
              height: '40px',
              border: '3px solid var(--border-mint)',
              borderTopColor: 'var(--primary-emerald)',
              borderRadius: '50%',
              animation: 'spin 0.8s linear infinite'
            }} />
            <p style={{ marginTop: '1rem', color: 'var(--text-muted)', fontSize: '0.95rem' }}>
              Gathering health profile, food diary records, and deficiency intelligence...
            </p>
            <style>{`@keyframes spin { to { transform: rotate(360deg); } }`}</style>
          </div>
        ) : (
          <>
            {/* 1. Summary Cards (Calories, Protein, Carbs, Fat) */}
            <NutritionSummaryCards summary={todaySummary} profile={profile} />

            {/* 2. Grid Layout: 7-Day Nutrition Trend Chart + AI Deficiency Risk Card */}
            <div className="grid-2" style={{ gap: '1.5rem', marginBottom: '1.5rem' }}>
              <NutritionChart data={weeklySummaries} tdeeTarget={profile?.tdee} />
              <DeficiencyRiskCard prediction={prediction} hasEnoughData={hasEnoughPredictionData} />
            </div>

            {/* 3. Longitudinal Deficiency Risk & Progress Tracker (4/8/12 Weeks) */}
            <LongitudinalProgressTracker />

            {/* 3. Today's Logged Food Diary Summary Section */}
            <div className="app-card" style={{ padding: '1.5rem', marginBottom: '1.5rem' }}>
              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '1rem', flexWrap: 'wrap', gap: '0.5rem' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                  <Apple size={20} style={{ color: 'var(--primary-emerald)' }} />
                  <h3 style={{ fontSize: '1.05rem', fontWeight: 700, color: 'var(--text-main)' }}>
                    Today's Logged Meals ({todayEntries.length})
                  </h3>
                </div>
                <Link to="/diary" className="btn-primary" style={{ fontSize: '0.8rem', padding: '0.4rem 0.85rem' }}>
                  <Plus size={16} /> Log Meal
                </Link>
              </div>

              {todayEntries.length === 0 ? (
                <div style={{ background: '#f8fafc', padding: '1.5rem', borderRadius: 'var(--radius-md)', textAlign: 'center', color: 'var(--text-muted)' }}>
                  <BookOpen size={28} style={{ color: 'var(--text-light)', marginBottom: '0.4rem' }} />
                  <p style={{ fontSize: '0.875rem' }}>No meals logged for today yet. Use the Food Diary to track your nutrition.</p>
                </div>
              ) : (
                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))', gap: '0.75rem' }}>
                  {todayEntries.map((entry) => (
                    <div key={entry.id || entry.food_name} style={{ background: '#ffffff', border: '1px solid var(--border-subtle)', borderRadius: 'var(--radius-sm)', padding: '0.75rem' }}>
                      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '0.2rem' }}>
                        <span className="badge badge-mint" style={{ fontSize: '0.675rem', textTransform: 'capitalize' }}>
                          {entry.meal_type}
                        </span>
                        <span style={{ fontSize: '0.75rem', fontWeight: 600, color: 'var(--primary-emerald)' }}>
                          {Math.round(entry.calories)} kcal
                        </span>
                      </div>
                      <div style={{ fontWeight: 600, fontSize: '0.875rem', color: 'var(--text-main)' }}>
                        {entry.food_name}
                      </div>
                      <div style={{ fontSize: '0.725rem', color: 'var(--text-muted)', marginTop: '0.2rem' }}>
                        {entry.serving_size} {entry.serving_unit} • P: {entry.protein_g}g | C: {entry.carbs_g}g | F: {entry.fat_g}g
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>

            {/* 4. Generated 7-Day Meal Plan View */}
            <WeeklyMealPlanView
              weeklyPlan={weeklyPlan}
              onReplaceItem={handleReplaceItem}
              loadingReplace={loadingReplace}
              onRefreshPlan={loadDashboardData}
            />

            {/* Quick Action Navigation Grid */}
            <h3 style={{ fontSize: '1.1rem', fontWeight: 700, marginBottom: '1rem', color: 'var(--text-main)' }}>
              Quick Navigation Actions
            </h3>
            <div className="grid-4" style={{ gap: '1rem', marginBottom: '2rem' }}>
              <Link to="/profile" style={{ textDecoration: 'none' }}>
                <div className="app-card" style={{ padding: '1rem', display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
                  <UserCheck size={20} style={{ color: 'var(--primary-emerald)' }} />
                  <span style={{ fontSize: '0.875rem', fontWeight: 600, color: 'var(--text-main)' }}>Health Profile</span>
                </div>
              </Link>
              <Link to="/diary" style={{ textDecoration: 'none' }}>
                <div className="app-card" style={{ padding: '1rem', display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
                  <BookOpen size={20} style={{ color: '#0284c7' }} />
                  <span style={{ fontSize: '0.875rem', fontWeight: 600, color: 'var(--text-main)' }}>Food Diary</span>
                </div>
              </Link>
              <Link to="/symptoms" style={{ textDecoration: 'none' }}>
                <div className="app-card" style={{ padding: '1rem', display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
                  <Activity size={20} style={{ color: '#d97706' }} />
                  <span style={{ fontSize: '0.875rem', fontWeight: 600, color: 'var(--text-main)' }}>Symptoms</span>
                </div>
              </Link>
              <Link to="/predict" style={{ textDecoration: 'none' }}>
                <div className="app-card" style={{ padding: '1rem', display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
                  <Sparkles size={20} style={{ color: 'var(--primary-emerald)' }} />
                  <span style={{ fontSize: '0.875rem', fontWeight: 600, color: 'var(--text-main)' }}>AI Predictor</span>
                </div>
              </Link>
            </div>
          </>
        )}
      </main>
    </div>
  );
};

export default DashboardPage;
