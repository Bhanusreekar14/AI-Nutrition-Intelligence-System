import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { Navbar } from '../components/Navbar';
import { 
  getFoodDiaryEntries, 
  createFoodDiaryEntry, 
  deleteFoodDiaryEntry, 
  getDailyNutritionSummary,
  getMyHealthProfile 
} from '../services/api';
import { FoodDiaryEntry, DailyNutritionSummary, HealthProfile } from '../types';
import { 
  calculateMacroTargets, 
  calculateCalorieProgress, 
  getNutritionStatus, 
  generateNutritionInsights 
} from '../utils/nutrition';
import { 
  Calendar, ChevronLeft, ChevronRight, Plus, Trash2, 
  Utensils, Coffee, Moon, PieChart, Target, Sparkles, 
  AlertTriangle, Info, ArrowUpRight, CheckCircle2 
} from 'lucide-react';

export const FoodDiaryPage: React.FC = () => {
  const [selectedDate, setSelectedDate] = useState<string>(new Date().toISOString().split('T')[0]);
  const [entries, setEntries] = useState<FoodDiaryEntry[]>([]);
  const [summary, setSummary] = useState<DailyNutritionSummary>({
    logged_date: selectedDate,
    total_calories: 0,
    total_protein_g: 0,
    total_carbs_g: 0,
    total_fat_g: 0,
    entry_count: 0,
  });
  const [healthProfile, setHealthProfile] = useState<HealthProfile | null>(null);
  const [loading, setLoading] = useState(true);
  const [showAddModal, setShowAddModal] = useState(false);

  // Form State
  const [mealType, setMealType] = useState<'breakfast' | 'lunch' | 'dinner' | 'snack'>('breakfast');
  const [foodName, setFoodName] = useState('');
  const [servingSize, setServingSize] = useState(1);
  const [servingUnit, setServingUnit] = useState('g');
  const [calories, setCalories] = useState(250);
  const [proteinG, setProteinG] = useState(15);
  const [carbsG, setCarbsG] = useState(30);
  const [fatG, setFatG] = useState(8);
  const [submitting, setSubmitting] = useState(false);

  useEffect(() => {
    fetchDiaryData();
  }, [selectedDate]);

  const fetchDiaryData = async () => {
    try {
      setLoading(true);
      const [fetchedEntries, fetchedSummary, fetchedProfile] = await Promise.all([
        getFoodDiaryEntries(selectedDate),
        getDailyNutritionSummary(selectedDate),
        getMyHealthProfile().catch((err) => {
          console.warn('Could not fetch health profile:', err);
          return null;
        }),
      ]);
      setEntries(fetchedEntries);
      setSummary(fetchedSummary);
      setHealthProfile(fetchedProfile);
    } catch (err) {
      console.error('Error loading diary data:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleDateChange = (days: number) => {
    const d = new Date(selectedDate);
    d.setDate(d.getDate() + days);
    setSelectedDate(d.toISOString().split('T')[0]);
  };

  const handleCreateEntry = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      setSubmitting(true);
      await createFoodDiaryEntry({
        logged_date: selectedDate,
        meal_type: mealType,
        food_name: foodName,
        serving_size: Number(servingSize),
        serving_unit: servingUnit,
        calories: Number(calories),
        protein_g: Number(proteinG),
        carbs_g: Number(carbsG),
        fat_g: Number(fatG),
      });

      // Reset form & reload data
      setFoodName('');
      setShowAddModal(false);
      await fetchDiaryData();
    } catch (err) {
      console.error('Error adding food entry:', err);
    } finally {
      setSubmitting(false);
    }
  };

  const handleDeleteEntry = async (id?: string) => {
    if (!id) return;
    try {
      await deleteFoodDiaryEntry(id);
      await fetchDiaryData();
    } catch (err) {
      console.error('Error deleting entry:', err);
    }
  };

  const getEntriesForMeal = (type: string) => {
    return entries.filter(e => e.meal_type === type);
  };

  const mealIcons: Record<string, React.ReactNode> = {
    breakfast: <Coffee size={20} color="var(--accent-amber)" />,
    lunch: <Utensils size={20} color="var(--primary-emerald)" />,
    dinner: <Moon size={20} color="var(--accent-purple)" />,
    snack: <PieChart size={20} color="var(--primary-teal)" />,
  };

  // Dynamic Intelligence Calculations
  const tdee = healthProfile?.tdee || 0;
  const calorieProgress = calculateCalorieProgress(summary.total_calories, tdee);
  const macroTargets = calculateMacroTargets(tdee);
  const nutritionStatus = getNutritionStatus(summary.total_calories, tdee);
  const insights = generateNutritionInsights(summary.total_calories, tdee, summary, macroTargets);

  // Macro progress helper
  const getMacroProgress = (consumed: number, target: number) => {
    if (!target || target <= 0) return 0;
    return Math.min(100, Math.round((consumed / target) * 100));
  };

  return (
    <div style={{ minHeight: '100vh', paddingBottom: '3rem' }}>
      <Navbar />

      <main className="app-container" style={{ marginTop: '1rem' }}>
        {/* Header & Date Picker */}
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '1.5rem', flexWrap: 'wrap', gap: '1rem' }}>
          <div>
            <h1 style={{ fontSize: '1.8rem', fontWeight: 800, color: '#fff', display: 'flex', alignItems: 'center', gap: '0.6rem' }}>
              <Utensils size={28} color="var(--primary-emerald)" /> Nutrition Intelligence Dashboard
            </h1>
            <p style={{ color: 'var(--text-muted)', fontSize: '0.95rem' }}>
              Track daily meals, monitor macro targets, and view rule-based nutrition progress.
            </p>
          </div>

          {/* Date Selector Navigation */}
          <div className="glass-card" style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', padding: '0.5rem 1rem' }}>
            <button className="btn-secondary" style={{ padding: '0.4rem' }} onClick={() => handleDateChange(-1)}>
              <ChevronLeft size={18} />
            </button>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', fontWeight: 600, fontSize: '0.95rem' }}>
              <Calendar size={18} color="var(--primary-emerald)" />
              <input
                type="date"
                value={selectedDate}
                onChange={(e) => setSelectedDate(e.target.value)}
                style={{
                  background: 'transparent',
                  border: 'none',
                  color: '#fff',
                  fontFamily: 'inherit',
                  fontSize: '0.95rem',
                  fontWeight: 600,
                  cursor: 'pointer'
                }}
              />
            </div>
            <button className="btn-secondary" style={{ padding: '0.4rem' }} onClick={() => handleDateChange(1)}>
              <ChevronRight size={18} />
            </button>
          </div>
        </div>

        {/* Missing Health Profile Warning Banner */}
        {(!healthProfile || !healthProfile.tdee) && !loading && (
          <div style={{
            background: 'rgba(251, 191, 36, 0.1)',
            border: '1px solid rgba(251, 191, 36, 0.3)',
            borderRadius: 'var(--radius-lg)',
            padding: '1rem 1.25rem',
            marginBottom: '1.5rem',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            gap: '1rem',
            flexWrap: 'wrap'
          }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', color: '#fcd34d', fontSize: '0.9rem' }}>
              <AlertTriangle size={20} />
              <span>
                <strong>Health Profile Incomplete:</strong> Complete your Health Profile to unlock your personalized Daily Calorie Target (TDEE) and macro goals.
              </span>
            </div>
            <Link to="/profile" className="btn-secondary" style={{ fontSize: '0.85rem', display: 'inline-flex', alignItems: 'center', gap: '0.3rem' }}>
              Setup Profile <ArrowUpRight size={16} />
            </Link>
          </div>
        )}

        {/* ==================================================== */}
        {/* NUTRITION OVERVIEW DASHBOARD */}
        {/* ==================================================== */}
        <div className="glass-card" style={{ padding: '1.75rem', marginBottom: '2rem' }}>
          {/* Header Row: Title & Status Badge */}
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '1.5rem', flexWrap: 'wrap', gap: '1rem' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.6rem' }}>
              <Target size={22} color="var(--primary-emerald)" />
              <h2 style={{ fontSize: '1.25rem', fontWeight: 700, color: '#fff', margin: 0 }}>
                Today's Calorie & Macro Target Progress
              </h2>
            </div>

            {/* Nutrition Status Badge */}
            <div style={{
              background: nutritionStatus.bg,
              color: nutritionStatus.color,
              border: `1px solid ${nutritionStatus.color}40`,
              borderRadius: '20px',
              padding: '0.4rem 0.9rem',
              fontSize: '0.85rem',
              fontWeight: 700,
              display: 'inline-flex',
              alignItems: 'center',
              gap: '0.4rem',
              letterSpacing: '0.03em'
            }}>
              <span>{nutritionStatus.icon}</span>
              <span>{nutritionStatus.label}</span>
            </div>
          </div>

          {/* Calorie Stats Grid */}
          <div className="grid-3" style={{ marginBottom: '1.5rem' }}>
            {/* 1. Daily Calorie Target */}
            <div style={{ background: 'rgba(255, 255, 255, 0.03)', border: '1px solid var(--bg-card-border)', borderRadius: 'var(--radius-md)', padding: '1.25rem' }}>
              <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.05em', fontWeight: 600 }}>
                Daily Calorie Target
              </div>
              <div style={{ fontSize: '1.8rem', fontWeight: 800, color: '#fff', marginTop: '0.25rem' }}>
                {tdee > 0 ? (
                  <>{tdee} <span style={{ fontSize: '0.9rem', color: 'var(--text-muted)', fontWeight: 500 }}>kcal</span></>
                ) : (
                  <span style={{ fontSize: '1.1rem', color: 'var(--text-dim)' }}>Not Configured</span>
                )}
              </div>
              <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginTop: '0.3rem' }}>
                {tdee > 0 ? 'Calculated from TDEE profile' : 'Complete health profile to set'}
              </div>
            </div>

            {/* 2. Consumed Calories */}
            <div style={{ background: 'rgba(255, 255, 255, 0.03)', border: '1px solid var(--bg-card-border)', borderRadius: 'var(--radius-md)', padding: '1.25rem' }}>
              <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.05em', fontWeight: 600 }}>
                Consumed
              </div>
              <div style={{ fontSize: '1.8rem', fontWeight: 800, color: '#38bdf8', marginTop: '0.25rem' }}>
                {summary.total_calories} <span style={{ fontSize: '0.9rem', color: 'var(--text-muted)', fontWeight: 500 }}>kcal</span>
              </div>
              <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginTop: '0.3rem' }}>
                {summary.entry_count} food entry logged today
              </div>
            </div>

            {/* 3. Remaining Calories */}
            <div style={{ background: 'rgba(255, 255, 255, 0.03)', border: '1px solid var(--bg-card-border)', borderRadius: 'var(--radius-md)', padding: '1.25rem' }}>
              <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.05em', fontWeight: 600 }}>
                Remaining
              </div>
              <div style={{ fontSize: '1.8rem', fontWeight: 800, color: calorieProgress.excess > 0 ? '#f43f5e' : '#34d399', marginTop: '0.25rem' }}>
                {tdee > 0 ? (
                  calorieProgress.excess > 0 ? (
                    <>0 <span style={{ fontSize: '0.9rem', color: 'var(--text-muted)', fontWeight: 500 }}>kcal</span></>
                  ) : (
                    <>{calorieProgress.remaining} <span style={{ fontSize: '0.9rem', color: 'var(--text-muted)', fontWeight: 500 }}>kcal</span></>
                  )
                ) : (
                  <span style={{ fontSize: '1.1rem', color: 'var(--text-dim)' }}>—</span>
                )}
              </div>
              <div style={{ fontSize: '0.75rem', color: calorieProgress.excess > 0 ? '#fda4af' : 'var(--text-muted)', marginTop: '0.3rem', fontWeight: calorieProgress.excess > 0 ? 600 : 400 }}>
                {tdee > 0 ? (
                  calorieProgress.excess > 0 ? `${calorieProgress.excess} kcal over target` : `${calorieProgress.percentage}% of daily goal consumed`
                ) : (
                  'TDEE goal required'
                )}
              </div>
            </div>
          </div>

          {/* Calorie Visual Progress Bar */}
          {tdee > 0 && (
            <div style={{ marginBottom: '1.75rem' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.85rem', marginBottom: '0.4rem', color: 'var(--text-muted)' }}>
                <span>Calorie Goal Progress</span>
                <span style={{ fontWeight: 600, color: '#fff' }}>{summary.total_calories} / {tdee} kcal ({calorieProgress.percentage}%)</span>
              </div>
              <div style={{ height: '10px', background: 'rgba(255, 255, 255, 0.08)', borderRadius: '5px', overflow: 'hidden' }}>
                <div style={{
                  height: '100%',
                  width: `${calorieProgress.visualPercentage}%`,
                  background: calorieProgress.excess > 0 
                    ? 'linear-gradient(90deg, #f59e0b 0%, #f43f5e 100%)' 
                    : 'linear-gradient(90deg, #10b981 0%, #34d399 100%)',
                  borderRadius: '5px',
                  transition: 'width 0.5s ease-in-out'
                }} />
              </div>
            </div>
          )}

          {/* Suggested Daily Macro Targets Section */}
          <div style={{ borderTop: '1px solid var(--bg-card-border)', paddingTop: '1.5rem', marginTop: '1.5rem' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'baseline', marginBottom: '1rem', flexWrap: 'wrap', gap: '0.5rem' }}>
              <h3 style={{ fontSize: '1.05rem', fontWeight: 700, color: '#fff', margin: 0 }}>
                Suggested Daily Macro Targets
              </h3>
              <span style={{ fontSize: '0.78rem', color: 'var(--text-muted)' }}>
                Based on 20% Protein • 50% Carbs • 30% Fat distribution
              </span>
            </div>

            <div className="grid-3">
              {/* Protein Progress */}
              <div style={{ background: 'rgba(255, 255, 255, 0.02)', border: '1px solid var(--bg-card-border)', borderRadius: 'var(--radius-md)', padding: '1rem' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.85rem', fontWeight: 600, color: '#34d399', marginBottom: '0.3rem' }}>
                  <span>Protein</span>
                  <span>{summary.total_protein_g} / {macroTargets.protein_g} g</span>
                </div>
                <div style={{ height: '6px', background: 'rgba(255, 255, 255, 0.08)', borderRadius: '3px', overflow: 'hidden' }}>
                  <div style={{
                    height: '100%',
                    width: `${getMacroProgress(summary.total_protein_g, macroTargets.protein_g)}%`,
                    background: '#34d399',
                    borderRadius: '3px',
                    transition: 'width 0.4s ease'
                  }} />
                </div>
              </div>

              {/* Carbohydrates Progress */}
              <div style={{ background: 'rgba(255, 255, 255, 0.02)', border: '1px solid var(--bg-card-border)', borderRadius: 'var(--radius-md)', padding: '1rem' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.85rem', fontWeight: 600, color: '#38bdf8', marginBottom: '0.3rem' }}>
                  <span>Carbohydrates</span>
                  <span>{summary.total_carbs_g} / {macroTargets.carbs_g} g</span>
                </div>
                <div style={{ height: '6px', background: 'rgba(255, 255, 255, 0.08)', borderRadius: '3px', overflow: 'hidden' }}>
                  <div style={{
                    height: '100%',
                    width: `${getMacroProgress(summary.total_carbs_g, macroTargets.carbs_g)}%`,
                    background: '#38bdf8',
                    borderRadius: '3px',
                    transition: 'width 0.4s ease'
                  }} />
                </div>
              </div>

              {/* Fat Progress */}
              <div style={{ background: 'rgba(255, 255, 255, 0.02)', border: '1px solid var(--bg-card-border)', borderRadius: 'var(--radius-md)', padding: '1rem' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.85rem', fontWeight: 600, color: '#fbbf24', marginBottom: '0.3rem' }}>
                  <span>Fat</span>
                  <span>{summary.total_fat_g} / {macroTargets.fat_g} g</span>
                </div>
                <div style={{ height: '6px', background: 'rgba(255, 255, 255, 0.08)', borderRadius: '3px', overflow: 'hidden' }}>
                  <div style={{
                    height: '100%',
                    width: `${getMacroProgress(summary.total_fat_g, macroTargets.fat_g)}%`,
                    background: '#fbbf24',
                    borderRadius: '3px',
                    transition: 'width 0.4s ease'
                  }} />
                </div>
              </div>
            </div>
          </div>

          {/* Today's Nutrition Insights */}
          <div style={{ borderTop: '1px solid var(--bg-card-border)', paddingTop: '1.5rem', marginTop: '1.5rem' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.8rem' }}>
              <Sparkles size={18} color="var(--primary-teal)" />
              <h3 style={{ fontSize: '1.05rem', fontWeight: 700, color: '#fff', margin: 0 }}>
                Today's Nutrition Insights
              </h3>
            </div>

            <div style={{ background: 'rgba(15, 23, 42, 0.4)', borderRadius: 'var(--radius-md)', padding: '1rem 1.25rem', border: '1px solid rgba(255, 255, 255, 0.05)' }}>
              <ul style={{ margin: 0, paddingLeft: '1.25rem', color: 'var(--text-light)', fontSize: '0.9rem', display: 'flex', flexDirection: 'column', gap: '0.4rem' }}>
                {insights.map((insight, idx) => (
                  <li key={idx} style={{ lineHeight: '1.4' }}>{insight}</li>
                ))}
              </ul>

              {/* Informational Disclaimer */}
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem', color: 'var(--text-dim)', fontSize: '0.78rem', marginTop: '0.8rem', borderTop: '1px dotted rgba(255, 255, 255, 0.1)', paddingTop: '0.6rem' }}>
                <Info size={14} />
                <span>These insights are informational and are not medical advice.</span>
              </div>
            </div>
          </div>
        </div>

        {/* Action Button to Log Food */}
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.5rem' }}>
          <h2 style={{ fontSize: '1.4rem', fontWeight: 700, color: '#fff', margin: 0 }}>
            Logged Meals
          </h2>
          <button className="btn-primary" onClick={() => setShowAddModal(true)}>
            <Plus size={18} /> Log Food Entry
          </button>
        </div>

        {/* Meal Category Sections */}
        {loading ? (
          <div style={{ padding: '3rem', textAlign: 'center', color: 'var(--text-muted)' }}>
            Fetching food diary logs...
          </div>
        ) : (
          <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
            {(['breakfast', 'lunch', 'dinner', 'snack'] as const).map((category) => {
              const mealEntries = getEntriesForMeal(category);
              const mealCalories = mealEntries.reduce((sum, item) => sum + item.calories, 0);

              return (
                <div key={category} className="glass-card" style={{ padding: '1.5rem' }}>
                  <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '1rem', borderBottom: '1px solid var(--bg-card-border)', paddingBottom: '0.75rem' }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '0.6rem', textTransform: 'capitalize', fontSize: '1.15rem', fontWeight: 700, color: '#fff' }}>
                      {mealIcons[category]} {category}
                    </div>
                    <span className="badge badge-emerald">
                      {mealCalories} kcal
                    </span>
                  </div>

                  {mealEntries.length === 0 ? (
                    <div style={{ padding: '1rem', textAlign: 'center', color: 'var(--text-dim)', fontSize: '0.875rem' }}>
                      No items logged for {category} yet.
                    </div>
                  ) : (
                    <div style={{ display: 'flex', flexDirection: 'column', gap: '0.6rem' }}>
                      {mealEntries.map((item) => (
                        <div
                          key={item.id}
                          style={{
                            display: 'flex',
                            alignItems: 'center',
                            justifyContent: 'space-between',
                            background: 'rgba(255, 255, 255, 0.03)',
                            border: '1px solid var(--bg-card-border)',
                            borderRadius: 'var(--radius-md)',
                            padding: '0.75rem 1rem'
                          }}
                        >
                          <div>
                            <div style={{ fontWeight: 600, color: '#fff', fontSize: '0.95rem' }}>{item.food_name}</div>
                            <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>
                              Serving: {item.serving_size} {item.serving_unit} • P: {item.protein_g}g | C: {item.carbs_g}g | F: {item.fat_g}g
                            </div>
                          </div>

                          <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
                            <span style={{ fontWeight: 700, color: 'var(--primary-teal)', fontSize: '0.95rem' }}>
                              {item.calories} kcal
                            </span>
                            <button
                              onClick={() => handleDeleteEntry(item.id)}
                              style={{
                                background: 'transparent',
                                border: 'none',
                                color: 'var(--accent-rose)',
                                cursor: 'pointer',
                                padding: '0.2rem',
                                opacity: 0.8
                              }}
                              title="Delete Entry"
                            >
                              <Trash2 size={18} />
                            </button>
                          </div>
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              );
            })}
          </div>
        )}

        {/* Modal for Adding Food Entry */}
        {showAddModal && (
          <div style={{
            position: 'fixed',
            inset: 0,
            background: 'rgba(0, 0, 0, 0.75)',
            backdropFilter: 'blur(8px)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            zIndex: 100,
            padding: '1.5rem'
          }}>
            <div className="glass-card animate-fade-in" style={{ width: '100%', maxWidth: '500px', padding: '2rem' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.5rem' }}>
                <h2 style={{ fontSize: '1.3rem', fontWeight: 700, color: '#fff' }}>Log New Food Entry</h2>
                <button
                  onClick={() => setShowAddModal(false)}
                  style={{ background: 'transparent', border: 'none', color: 'var(--text-muted)', fontSize: '1.2rem', cursor: 'pointer' }}
                >
                  ✕
                </button>
              </div>

              <form onSubmit={handleCreateEntry}>
                <div className="form-group">
                  <label>Meal Category</label>
                  <select
                    className="input-field"
                    value={mealType}
                    onChange={(e) => setMealType(e.target.value as any)}
                  >
                    <option value="breakfast">Breakfast</option>
                    <option value="lunch">Lunch</option>
                    <option value="dinner">Dinner</option>
                    <option value="snack">Snack</option>
                  </select>
                </div>

                <div className="form-group">
                  <label>Food Item Name</label>
                  <input
                    type="text"
                    className="input-field"
                    placeholder="e.g., Grilled Chicken Breast with Quinoa"
                    value={foodName}
                    onChange={(e) => setFoodName(e.target.value)}
                    required
                  />
                </div>

                <div className="grid-2">
                  <div className="form-group">
                    <label>Serving Size</label>
                    <input
                      type="number"
                      step="0.1"
                      className="input-field"
                      value={servingSize}
                      onChange={(e) => setServingSize(parseFloat(e.target.value) || 1)}
                      required
                    />
                  </div>
                  <div className="form-group">
                    <label>Unit</label>
                    <input
                      type="text"
                      className="input-field"
                      placeholder="g, cup, serving"
                      value={servingUnit}
                      onChange={(e) => setServingUnit(e.target.value)}
                      required
                    />
                  </div>
                </div>

                <div className="grid-2">
                  <div className="form-group">
                    <label>Calories (kcal)</label>
                    <input
                      type="number"
                      className="input-field"
                      value={calories}
                      onChange={(e) => setCalories(parseFloat(e.target.value) || 0)}
                      required
                    />
                  </div>
                  <div className="form-group">
                    <label>Protein (g)</label>
                    <input
                      type="number"
                      step="0.1"
                      className="input-field"
                      value={proteinG}
                      onChange={(e) => setProteinG(parseFloat(e.target.value) || 0)}
                      required
                    />
                  </div>
                </div>

                <div className="grid-2">
                  <div className="form-group">
                    <label>Carbs (g)</label>
                    <input
                      type="number"
                      step="0.1"
                      className="input-field"
                      value={carbsG}
                      onChange={(e) => setCarbsG(parseFloat(e.target.value) || 0)}
                      required
                    />
                  </div>
                  <div className="form-group">
                    <label>Fat (g)</label>
                    <input
                      type="number"
                      step="0.1"
                      className="input-field"
                      value={fatG}
                      onChange={(e) => setFatG(parseFloat(e.target.value) || 0)}
                      required
                    />
                  </div>
                </div>

                <div style={{ display: 'flex', gap: '1rem', marginTop: '1.5rem' }}>
                  <button type="button" className="btn-secondary" style={{ flex: 1 }} onClick={() => setShowAddModal(false)}>
                    Cancel
                  </button>
                  <button type="submit" className="btn-primary" style={{ flex: 1 }} disabled={submitting}>
                    {submitting ? 'Saving...' : 'Save Entry'}
                  </button>
                </div>
              </form>
            </div>
          </div>
        )}
      </main>
    </div>
  );
};
