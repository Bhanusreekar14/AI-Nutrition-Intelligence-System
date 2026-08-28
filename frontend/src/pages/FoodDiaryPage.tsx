import React, { useEffect, useState } from 'react';
import { Navbar } from '../components/Navbar';
import { getFoodDiaryEntries, createFoodDiaryEntry, deleteFoodDiaryEntry, getDailyNutritionSummary } from '../services/api';
import { FoodDiaryEntry, DailyNutritionSummary } from '../types';
import { 
  Calendar, ChevronLeft, ChevronRight, Plus, Trash2, 
  Utensils, Coffee, Moon, PieChart 
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
      const [fetchedEntries, fetchedSummary] = await Promise.all([
        getFoodDiaryEntries(selectedDate),
        getDailyNutritionSummary(selectedDate),
      ]);
      setEntries(fetchedEntries);
      setSummary(fetchedSummary);
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

      // Reset form & reload
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

  return (
    <div style={{ minHeight: '100vh' }}>
      <Navbar />

      <main className="app-container" style={{ marginTop: '1rem' }}>
        {/* Header & Date Picker */}
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '2rem', flexWrap: 'wrap', gap: '1rem' }}>
          <div>
            <h1 style={{ fontSize: '1.8rem', fontWeight: 800, color: '#fff', display: 'flex', alignItems: 'center', gap: '0.6rem' }}>
              <Utensils size={28} color="var(--primary-emerald)" /> Daily Food Diary
            </h1>
            <p style={{ color: 'var(--text-muted)', fontSize: '0.95rem' }}>
              Log meals and track macronutrients & daily caloric intake.
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

        {/* Macro Summary Dashboard Cards */}
        <div className="grid-4" style={{ marginBottom: '2rem' }}>
          <div className="glass-card" style={{ padding: '1.25rem' }}>
            <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.05em' }}>Calories</div>
            <div style={{ fontSize: '1.6rem', fontWeight: 800, color: '#fff', marginTop: '0.2rem' }}>
              {summary.total_calories} <span style={{ fontSize: '0.85rem', color: 'var(--text-muted)' }}>kcal</span>
            </div>
          </div>

          <div className="glass-card" style={{ padding: '1.25rem' }}>
            <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.05em' }}>Protein</div>
            <div style={{ fontSize: '1.6rem', fontWeight: 800, color: '#34d399', marginTop: '0.2rem' }}>
              {summary.total_protein_g} <span style={{ fontSize: '0.85rem', color: 'var(--text-muted)' }}>g</span>
            </div>
          </div>

          <div className="glass-card" style={{ padding: '1.25rem' }}>
            <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.05em' }}>Carbohydrates</div>
            <div style={{ fontSize: '1.6rem', fontWeight: 800, color: '#38bdf8', marginTop: '0.2rem' }}>
              {summary.total_carbs_g} <span style={{ fontSize: '0.85rem', color: 'var(--text-muted)' }}>g</span>
            </div>
          </div>

          <div className="glass-card" style={{ padding: '1.25rem' }}>
            <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.05em' }}>Fats</div>
            <div style={{ fontSize: '1.6rem', fontWeight: 800, color: '#fbbf24', marginTop: '0.2rem' }}>
              {summary.total_fat_g} <span style={{ fontSize: '0.85rem', color: 'var(--text-muted)' }}>g</span>
            </div>
          </div>
        </div>

        {/* Action Button to Log Food */}
        <div style={{ display: 'flex', justifyContent: 'flex-end', marginBottom: '1.5rem' }}>
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
