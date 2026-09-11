import React, { useEffect, useState } from 'react';
import { Navbar } from '../components/Navbar';
import { 
  getFoodDiaryEntries, 
  createFoodDiaryEntry, 
  updateFoodDiaryEntry, 
  deleteFoodDiaryEntry, 
  getDailyNutritionSummary,
  searchFoods
} from '../services/api';
import { FoodDiaryEntry, DailyNutritionSummary, NormalizedFoodItem } from '../types';
import { 
  Calendar, ChevronLeft, ChevronRight, Plus, Trash2, Edit2, Search,
  Utensils, Coffee, Moon, PieChart, X, Info
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
    total_fiber_g: 0,
    total_sugar_g: 0,
    total_sodium_mg: 0,
    total_vitamin_d_mcg: 0,
    total_vitamin_b12_mcg: 0,
    total_iron_mg: 0,
    total_calcium_mg: 0,
    entry_count: 0,
  });

  const [loading, setLoading] = useState(true);
  const [showAddModal, setShowAddModal] = useState(false);
  const [editingEntry, setEditingEntry] = useState<FoodDiaryEntry | null>(null);

  // Search Modal State
  const [showSearchModal, setShowSearchModal] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  const [searchResults, setSearchResults] = useState<NormalizedFoodItem[]>([]);
  const [searching, setSearching] = useState(false);

  // Entry Form State
  const [mealType, setMealType] = useState<'breakfast' | 'lunch' | 'dinner' | 'snack'>('breakfast');
  const [foodName, setFoodName] = useState('');
  const [externalFoodId, setExternalFoodId] = useState<string | undefined>(undefined);
  const [source, setSource] = useState<string>('manual');
  const [quantity, setQuantity] = useState<number>(1);
  const [unit, setUnit] = useState<string>('serving');
  const [baseNutrients, setBaseNutrients] = useState({
    calories: 150,
    protein: 5,
    carbs: 20,
    fat: 3,
    fiber: 2,
    sugar: 1,
    sodium: 50,
    vitaminD: 0,
    vitaminB12: 0,
    iron: 0.5,
    calcium: 20
  });

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

  // Search Foods handler
  const handleFoodSearch = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!searchQuery.trim()) return;
    try {
      setSearching(true);
      const res = await searchFoods(searchQuery.trim());
      setSearchResults(res);
    } catch (err) {
      console.error('Search error:', err);
    } finally {
      setSearching(false);
    }
  };

  const selectFoodFromSearch = (item: NormalizedFoodItem) => {
    setFoodName(item.name);
    setExternalFoodId(item.externalId);
    setSource(item.source);
    setQuantity(1);
    setUnit(item.servingUnit || 'serving');
    setBaseNutrients({
      calories: item.calories,
      protein: item.protein,
      carbs: item.carbohydrates,
      fat: item.fat,
      fiber: item.fiber,
      sugar: item.sugar,
      sodium: item.sodium,
      vitaminD: item.vitaminD,
      vitaminB12: item.vitaminB12,
      iron: item.iron,
      calcium: item.calcium
    });
    setShowSearchModal(false);
    setShowAddModal(true);
  };

  const openCreateModal = () => {
    setEditingEntry(null);
    setFoodName('');
    setExternalFoodId(undefined);
    setSource('manual');
    setQuantity(1);
    setUnit('serving');
    setBaseNutrients({
      calories: 200,
      protein: 8,
      carbs: 25,
      fat: 5,
      fiber: 2,
      sugar: 2,
      sodium: 100,
      vitaminD: 0,
      vitaminB12: 0,
      iron: 1,
      calcium: 30
    });
    setShowAddModal(true);
  };

  const openEditModal = (entry: FoodDiaryEntry) => {
    setEditingEntry(entry);
    setMealType(entry.meal_type);
    setFoodName(entry.food_name);
    setExternalFoodId(entry.external_food_id);
    setSource(entry.source || 'manual');
    setQuantity(entry.serving_size);
    setUnit(entry.serving_unit);
    const qty = entry.serving_size || 1;
    setBaseNutrients({
      calories: entry.calories / qty,
      protein: entry.protein_g / qty,
      carbs: entry.carbs_g / qty,
      fat: entry.fat_g / qty,
      fiber: (entry.fiber_g || 0) / qty,
      sugar: (entry.sugar_g || 0) / qty,
      sodium: (entry.sodium_mg || 0) / qty,
      vitaminD: (entry.vitamin_d_mcg || 0) / qty,
      vitaminB12: (entry.vitamin_b12_mcg || 0) / qty,
      iron: (entry.iron_mg || 0) / qty,
      calcium: (entry.calcium_mg || 0) / qty,
    });
    setShowAddModal(true);
  };

  const handleSaveEntry = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      setSubmitting(true);
      const qty = Number(quantity) || 1;

      const payload: FoodDiaryEntry = {
        logged_date: selectedDate,
        meal_type: mealType,
        food_name: foodName,
        external_food_id: externalFoodId,
        source: source,
        serving_size: qty,
        serving_unit: unit,
        calories: Number((baseNutrients.calories * qty).toFixed(1)),
        protein_g: Number((baseNutrients.protein * qty).toFixed(1)),
        carbs_g: Number((baseNutrients.carbs * qty).toFixed(1)),
        fat_g: Number((baseNutrients.fat * qty).toFixed(1)),
        fiber_g: Number((baseNutrients.fiber * qty).toFixed(1)),
        sugar_g: Number((baseNutrients.sugar * qty).toFixed(1)),
        sodium_mg: Number((baseNutrients.sodium * qty).toFixed(1)),
        vitamin_d_mcg: Number((baseNutrients.vitaminD * qty).toFixed(2)),
        vitamin_b12_mcg: Number((baseNutrients.vitaminB12 * qty).toFixed(2)),
        iron_mg: Number((baseNutrients.iron * qty).toFixed(2)),
        calcium_mg: Number((baseNutrients.calcium * qty).toFixed(2)),
      };

      if (editingEntry?.id) {
        await updateFoodDiaryEntry(editingEntry.id, payload);
      } else {
        await createFoodDiaryEntry(payload);
      }

      setShowAddModal(false);
      await fetchDiaryData();
    } catch (err) {
      console.error('Error saving food entry:', err);
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
    breakfast: <Coffee size={18} color="#d97706" />,
    lunch: <Utensils size={18} color="var(--primary-emerald)" />,
    dinner: <Moon size={18} color="#9333ea" />,
    snack: <PieChart size={18} color="#0284c7" />,
  };

  return (
    <div style={{ minHeight: '100vh', background: 'var(--bg-page)' }}>
      <Navbar />

      <main className="app-container">
        {/* Header & Date Navigation */}
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '1.75rem', flexWrap: 'wrap', gap: '1rem' }}>
          <div>
            <h1 style={{ fontSize: '1.75rem', fontWeight: 700, color: 'var(--text-main)', display: 'flex', alignItems: 'center', gap: '0.6rem' }}>
              <Utensils size={26} color="var(--primary-emerald)" /> Food Diary
            </h1>
            <p style={{ color: 'var(--text-muted)', fontSize: '0.95rem' }}>
              Log meals, search food databases, and calculate daily totals.
            </p>
          </div>

          {/* Date Selector */}
          <div className="app-card" style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', padding: '0.4rem 0.85rem' }}>
            <button className="btn-secondary" style={{ padding: '0.35rem 0.5rem' }} onClick={() => handleDateChange(-1)}>
              <ChevronLeft size={16} />
            </button>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem', fontWeight: 600, fontSize: '0.9rem' }}>
              <Calendar size={16} color="var(--primary-emerald)" />
              <input
                type="date"
                value={selectedDate}
                onChange={(e) => setSelectedDate(e.target.value)}
                style={{
                  background: 'transparent',
                  border: 'none',
                  color: 'var(--text-main)',
                  fontFamily: 'inherit',
                  fontSize: '0.9rem',
                  fontWeight: 600,
                  cursor: 'pointer'
                }}
              />
            </div>
            <button className="btn-secondary" style={{ padding: '0.35rem 0.5rem' }} onClick={() => handleDateChange(1)}>
              <ChevronRight size={16} />
            </button>
          </div>
        </div>

        {/* Daily Totals Cards */}
        <div className="grid-4" style={{ marginBottom: '1.5rem' }}>
          <div className="app-card" style={{ padding: '1rem 1.25rem' }}>
            <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', fontWeight: 600 }}>CALORIES</div>
            <div style={{ fontSize: '1.4rem', fontWeight: 700, color: 'var(--text-main)', marginTop: '0.2rem' }}>
              {summary.total_calories} <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>kcal</span>
            </div>
          </div>
          <div className="app-card" style={{ padding: '1rem 1.25rem' }}>
            <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', fontWeight: 600 }}>PROTEIN</div>
            <div style={{ fontSize: '1.4rem', fontWeight: 700, color: 'var(--primary-emerald)', marginTop: '0.2rem' }}>
              {summary.total_protein_g} <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>g</span>
            </div>
          </div>
          <div className="app-card" style={{ padding: '1rem 1.25rem' }}>
            <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', fontWeight: 600 }}>CARBS</div>
            <div style={{ fontSize: '1.4rem', fontWeight: 700, color: '#0284c7', marginTop: '0.2rem' }}>
              {summary.total_carbs_g} <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>g</span>
            </div>
          </div>
          <div className="app-card" style={{ padding: '1rem 1.25rem' }}>
            <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', fontWeight: 600 }}>FAT</div>
            <div style={{ fontSize: '1.4rem', fontWeight: 700, color: '#d97706', marginTop: '0.2rem' }}>
              {summary.total_fat_g} <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>g</span>
            </div>
          </div>
        </div>

        {/* Micronutrients Accordion/Summary */}
        <div className="mint-card" style={{ marginBottom: '1.75rem', padding: '1rem 1.25rem' }}>
          <div style={{ fontSize: '0.85rem', fontWeight: 700, color: '#15803d', marginBottom: '0.5rem', display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
            <Info size={16} /> Daily Nutrient Totals ({selectedDate})
          </div>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(130px, 1fr))', gap: '0.75rem', fontSize: '0.85rem' }}>
            <div><strong>Fiber:</strong> {summary.total_fiber_g} g</div>
            <div><strong>Sugar:</strong> {summary.total_sugar_g} g</div>
            <div><strong>Sodium:</strong> {summary.total_sodium_mg} mg</div>
            <div><strong>Vitamin D:</strong> {summary.total_vitamin_d_mcg} mcg</div>
            <div><strong>Vitamin B12:</strong> {summary.total_vitamin_b12_mcg} mcg</div>
            <div><strong>Iron:</strong> {summary.total_iron_mg} mg</div>
            <div><strong>Calcium:</strong> {summary.total_calcium_mg} mg</div>
          </div>
        </div>

        {/* Action Buttons */}
        <div style={{ display: 'flex', gap: '0.75rem', justifyContent: 'flex-end', marginBottom: '1.5rem' }}>
          <button className="btn-secondary" onClick={() => { setSearchResults([]); setSearchQuery(''); setShowSearchModal(true); }}>
            <Search size={16} /> Search Food (USDA / OpenFoodFacts)
          </button>
          <button className="btn-primary" onClick={openCreateModal}>
            <Plus size={16} /> Add Food
          </button>
        </div>

        {/* Meal Categories */}
        {loading ? (
          <div className="app-card" style={{ padding: '3rem', textAlign: 'center', color: 'var(--text-muted)' }}>
            Loading diary entries...
          </div>
        ) : (
          <div style={{ display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>
            {(['breakfast', 'lunch', 'dinner', 'snack'] as const).map((category) => {
              const mealEntries = getEntriesForMeal(category);
              const mealCalories = mealEntries.reduce((sum, item) => sum + item.calories, 0);

              return (
                <div key={category} className="app-card" style={{ padding: '1.25rem' }}>
                  <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '0.85rem', borderBottom: '1px solid var(--border-subtle)', paddingBottom: '0.6rem' }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', textTransform: 'capitalize', fontSize: '1.05rem', fontWeight: 700, color: 'var(--text-main)' }}>
                      {mealIcons[category]} {category}
                    </div>
                    <span className="badge badge-mint">
                      {mealCalories.toFixed(0)} kcal
                    </span>
                  </div>

                  {mealEntries.length === 0 ? (
                    <div style={{ padding: '0.75rem', textAlign: 'center', color: 'var(--text-light)', fontSize: '0.875rem' }}>
                      No food items logged for {category}.
                    </div>
                  ) : (
                    <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
                      {mealEntries.map((item) => (
                        <div
                          key={item.id}
                          style={{
                            display: 'flex',
                            alignItems: 'center',
                            justifyContent: 'space-between',
                            background: '#f8fafc',
                            border: '1px solid var(--border-subtle)',
                            borderRadius: 'var(--radius-sm)',
                            padding: '0.75rem 1rem'
                          }}
                        >
                          <div>
                            <div style={{ fontWeight: 600, color: 'var(--text-main)', fontSize: '0.95rem' }}>
                              {item.food_name}
                            </div>
                            <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>
                              Quantity: {item.serving_size} {item.serving_unit} • P: {item.protein_g}g | C: {item.carbs_g}g | F: {item.fat_g}g
                              {item.source && item.source !== 'manual' && (
                                <span style={{ marginLeft: '0.5rem', color: 'var(--primary-teal)', textTransform: 'uppercase', fontSize: '0.7rem', fontWeight: 600 }}>
                                  [{item.source}]
                                </span>
                              )}
                            </div>
                          </div>

                          <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
                            <span style={{ fontWeight: 700, color: 'var(--primary-emerald)', fontSize: '0.95rem' }}>
                              {item.calories} kcal
                            </span>
                            <button
                              onClick={() => openEditModal(item)}
                              style={{ background: 'transparent', border: 'none', color: 'var(--text-muted)', cursor: 'pointer', padding: '0.2rem' }}
                              title="Edit Entry"
                            >
                              <Edit2 size={16} />
                            </button>
                            <button
                              onClick={() => handleDeleteEntry(item.id)}
                              style={{ background: 'transparent', border: 'none', color: 'var(--accent-rose)', cursor: 'pointer', padding: '0.2rem' }}
                              title="Delete Entry"
                            >
                              <Trash2 size={16} />
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

        {/* FOOD SEARCH MODAL */}
        {showSearchModal && (
          <div className="modal-overlay">
            <div className="app-card" style={{ width: '100%', maxWidth: '600px', padding: '1.75rem', maxHeight: '85vh', display: 'flex', flexDirection: 'column' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.25rem' }}>
                <h2 style={{ fontSize: '1.2rem', fontWeight: 700, color: 'var(--text-main)' }}>Search Food Database</h2>
                <button onClick={() => setShowSearchModal(false)} style={{ background: 'transparent', border: 'none', cursor: 'pointer' }}>
                  <X size={20} />
                </button>
              </div>

              <form onSubmit={handleFoodSearch} style={{ display: 'flex', gap: '0.5rem', marginBottom: '1.25rem' }}>
                <input
                  type="text"
                  className="input-field"
                  placeholder="Type food (e.g., Rice, Egg, Apple, Milk, Spinach)..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  style={{ flex: 1 }}
                  required
                />
                <button type="submit" className="btn-primary" disabled={searching}>
                  {searching ? 'Searching...' : 'Search'}
                </button>
              </form>

              <div style={{ flex: 1, overflowY: 'auto', display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
                {searching ? (
                  <div style={{ padding: '2rem', textAlign: 'center', color: 'var(--text-muted)' }}>Searching USDA & OpenFoodFacts...</div>
                ) : searchResults.length === 0 ? (
                  <div style={{ padding: '2rem', textAlign: 'center', color: 'var(--text-light)' }}>
                    {searchQuery ? 'No food results found. Try another query.' : 'Enter a query above to search.'}
                  </div>
                ) : (
                  searchResults.map((item) => (
                    <div
                      key={item.id}
                      style={{
                        padding: '0.85rem 1rem',
                        border: '1px solid var(--border-subtle)',
                        borderRadius: 'var(--radius-sm)',
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'space-between',
                        background: '#f8fafc'
                      }}
                    >
                      <div>
                        <div style={{ fontWeight: 600, fontSize: '0.95rem', color: 'var(--text-main)' }}>{item.name}</div>
                        <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>
                          Per {item.servingSize} {item.servingUnit}: {item.calories} kcal | P: {item.protein}g | C: {item.carbohydrates}g | F: {item.fat}g
                        </div>
                      </div>
                      <button className="btn-secondary" style={{ padding: '0.35rem 0.75rem', fontSize: '0.85rem' }} onClick={() => selectFoodFromSearch(item)}>
                        Add to Diary
                      </button>
                    </div>
                  ))
                )}
              </div>
            </div>
          </div>
        )}

        {/* ADD / EDIT FOOD ENTRY MODAL */}
        {showAddModal && (
          <div className="modal-overlay">
            <div className="app-card" style={{ width: '100%', maxWidth: '520px', padding: '1.75rem', maxHeight: '90vh', overflowY: 'auto' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.25rem' }}>
                <h2 style={{ fontSize: '1.2rem', fontWeight: 700, color: 'var(--text-main)' }}>
                  {editingEntry ? 'Edit Food Entry' : 'Add Food Entry'}
                </h2>
                <button onClick={() => setShowAddModal(false)} style={{ background: 'transparent', border: 'none', cursor: 'pointer' }}>
                  <X size={20} />
                </button>
              </div>

              <form onSubmit={handleSaveEntry}>
                <div className="form-group">
                  <label>Meal Type</label>
                  <select className="input-field" value={mealType} onChange={(e) => setMealType(e.target.value as any)}>
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
                    placeholder="e.g. Rice, Oatmeal, Chicken"
                    value={foodName}
                    onChange={(e) => setFoodName(e.target.value)}
                    required
                  />
                </div>

                <div className="grid-2">
                  <div className="form-group">
                    <label>Quantity</label>
                    <input
                      type="number"
                      step="0.1"
                      className="input-field"
                      value={quantity}
                      onChange={(e) => setQuantity(parseFloat(e.target.value) || 1)}
                      required
                    />
                  </div>
                  <div className="form-group">
                    <label>Unit</label>
                    <input
                      type="text"
                      className="input-field"
                      placeholder="cup, g, serving"
                      value={unit}
                      onChange={(e) => setUnit(e.target.value)}
                      required
                    />
                  </div>
                </div>

                <div className="grid-2">
                  <div className="form-group">
                    <label>Calories (kcal per unit)</label>
                    <input
                      type="number"
                      step="0.1"
                      className="input-field"
                      value={baseNutrients.calories}
                      onChange={(e) => setBaseNutrients({ ...baseNutrients, calories: parseFloat(e.target.value) || 0 })}
                    />
                  </div>
                  <div className="form-group">
                    <label>Protein (g per unit)</label>
                    <input
                      type="number"
                      step="0.1"
                      className="input-field"
                      value={baseNutrients.protein}
                      onChange={(e) => setBaseNutrients({ ...baseNutrients, protein: parseFloat(e.target.value) || 0 })}
                    />
                  </div>
                </div>

                <div className="grid-2">
                  <div className="form-group">
                    <label>Carbs (g per unit)</label>
                    <input
                      type="number"
                      step="0.1"
                      className="input-field"
                      value={baseNutrients.carbs}
                      onChange={(e) => setBaseNutrients({ ...baseNutrients, carbs: parseFloat(e.target.value) || 0 })}
                    />
                  </div>
                  <div className="form-group">
                    <label>Fat (g per unit)</label>
                    <input
                      type="number"
                      step="0.1"
                      className="input-field"
                      value={baseNutrients.fat}
                      onChange={(e) => setBaseNutrients({ ...baseNutrients, fat: parseFloat(e.target.value) || 0 })}
                    />
                  </div>
                </div>

                <div style={{ marginTop: '1rem', background: '#f8fafc', padding: '0.85rem 1rem', borderRadius: 'var(--radius-sm)', border: '1px solid var(--border-subtle)', marginBottom: '1.25rem' }}>
                  <div style={{ fontSize: '0.85rem', fontWeight: 600, color: 'var(--text-main)' }}>
                    Calculated Total for {quantity} {unit}:
                  </div>
                  <div style={{ fontSize: '0.85rem', color: 'var(--primary-emerald)', fontWeight: 700, marginTop: '0.2rem' }}>
                    {(baseNutrients.calories * quantity).toFixed(1)} kcal | P: {(baseNutrients.protein * quantity).toFixed(1)}g | C: {(baseNutrients.carbs * quantity).toFixed(1)}g | F: {(baseNutrients.fat * quantity).toFixed(1)}g
                  </div>
                </div>

                <div style={{ display: 'flex', gap: '0.75rem', justifyContent: 'flex-end' }}>
                  <button type="button" className="btn-secondary" onClick={() => setShowAddModal(false)}>Cancel</button>
                  <button type="submit" className="btn-primary" disabled={submitting}>
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
