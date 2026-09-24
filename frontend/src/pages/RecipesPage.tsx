import React, { useState, useEffect, useCallback } from 'react';
import { Navbar } from '../components/Navbar';
import {
  searchRecipes,
  getRecipeRecommendations
} from '../services/api';
import { Recipe } from '../types';
import {
  Search,
  Utensils,
  Info,
  AlertCircle,
  Sparkles,
  X,
  ChevronRight,
  ShieldAlert,
  Award
} from 'lucide-react';

const CATEGORY_OPTIONS = [
  'All Categories',
  'Vegetables and Vegetable Products',
  'Fruits and Fruit Juices',
  'Legumes and Legume Products',
  'Nut and Seed Products',
  'Cereal Grains and Pasta',
  'Poultry Products',
  'Beef Products',
  'Finfish and Shellfish Products',
  'Dairy and Egg Products',
  'Soups, Sauces, and Gravies',
  'Snacks',
  'Sweets',
  'Beverages'
];

const DIETARY_OPTIONS = [
  { label: 'Any Dietary Preference', value: '' },
  { label: 'Vegetarian', value: 'Vegetarian' },
  { label: 'Vegan', value: 'Vegan' },
  { label: 'Keto-Friendly', value: 'Keto-Friendly' },
  { label: 'Paleo-Friendly', value: 'Paleo-Friendly' },
];

const DEFICIENCY_OPTIONS = [
  { label: 'All / General Search', value: '' },
  { label: 'Anemia (Iron & Vit C focus)', value: 'Anemia' },
  { label: 'Scurvy (Vitamin C focus)', value: 'Scurvy' },
  { label: 'Rickets & Osteomalacia (Calcium & Protein focus)', value: 'Rickets_Osteomalacia' },
  { label: 'Night Blindness (Pro-Vitamin A / Green focus)', value: 'Night_Blindness' },
  { label: 'Healthy Baseline', value: 'Healthy' },
];

export const RecipesPage: React.FC = () => {
  const [recipes, setRecipes] = useState<Recipe[]>([]);
  const [totalResults, setTotalResults] = useState<number>(0);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  // Search & Filter controls
  const [searchQuery, setSearchQuery] = useState<string>('');
  const [selectedCategory, setSelectedCategory] = useState<string>('');
  const [selectedDiet, setSelectedDiet] = useState<string>('');
  const [selectedDeficiency, setSelectedDeficiency] = useState<string>('');
  const [allergiesInput, setAllergiesInput] = useState<string>('');
  const [prohibitedInput, setProhibitedInput] = useState<string>('');
  const [preferredInput, setPreferredInput] = useState<string>('');

  // Active modal recipe
  const [selectedRecipe, setSelectedRecipe] = useState<Recipe | null>(null);

  const fetchRecipes = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const allergyList = allergiesInput.split(',').map(s => s.trim()).filter(Boolean);
      const prohibitedList = prohibitedInput.split(',').map(s => s.trim()).filter(Boolean);
      const preferredList = preferredInput.split(',').map(s => s.trim()).filter(Boolean);

      if (selectedDeficiency) {
        // Use Recommendation Service Endpoint
        const res = await getRecipeRecommendations({
          deficiency_class: selectedDeficiency,
          dietary_preference: selectedDiet || undefined,
          allergies: allergyList,
          prohibited_foods: prohibitedList,
          preferred_foods: preferredList,
          limit: 30
        });
        setRecipes(res.recipes);
        setTotalResults(res.total_count);
      } else {
        // Use General Search Endpoint
        const res = await searchRecipes({
          query: searchQuery || undefined,
          category: selectedCategory !== 'All Categories' && selectedCategory ? selectedCategory : undefined,
          dietary_preference: selectedDiet || undefined,
          allergies: allergyList,
          prohibited_foods: prohibitedList,
          preferred_foods: preferredList,
          limit: 30
        });
        setRecipes(res.recipes);
        setTotalResults(res.total_count);
      }
    } catch (err: any) {
      setError(err.response?.data?.detail || err.message || 'Failed to load recipe candidates.');
      setRecipes([]);
    } finally {
      setLoading(false);
    }
  }, [searchQuery, selectedCategory, selectedDiet, selectedDeficiency, allergiesInput, prohibitedInput, preferredInput]);

  useEffect(() => {
    fetchRecipes();
  }, [fetchRecipes]);

  const handleResetFilters = () => {
    setSearchQuery('');
    setSelectedCategory('');
    setSelectedDiet('');
    setSelectedDeficiency('');
    setAllergiesInput('');
    setProhibitedInput('');
    setPreferredInput('');
  };

  return (
    <div style={{ minHeight: '100vh', background: 'var(--bg-page)' }}>
      <Navbar />

      <main className="app-container">
        {/* Header Banner */}
        <div className="mint-card" style={{ marginBottom: '1.5rem', borderRadius: 'var(--radius-lg)' }}>
          <div style={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between', flexWrap: 'wrap', gap: '1rem' }}>
            <div>
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.25rem' }}>
                <Utensils style={{ color: 'var(--primary-emerald)' }} size={24} />
                <h1 style={{ fontSize: '1.5rem', fontWeight: 700, color: 'var(--text-main)' }}>
                  Nutrition & Recipe Intelligence Candidates
                </h1>
              </div>
              <p style={{ color: 'var(--text-muted)', fontSize: '0.925rem', maxWidth: '750px' }}>
                Explore safety-verified, nutrient-dense food candidates tailored to your dietary preferences, allergy profiles, and micronutrient deficiency target needs.
              </p>
            </div>
            <span className="badge badge-mint" style={{ padding: '0.4rem 0.85rem', fontSize: '0.825rem' }}>
              <Sparkles size={14} style={{ marginRight: '0.35rem' }} /> Safety-Filtered
            </span>
          </div>

          {/* Educational Disclaimer Banner */}
          <div style={{
            marginTop: '1rem',
            padding: '0.75rem 1rem',
            background: 'rgba(255, 255, 255, 0.7)',
            border: '1px solid var(--border-mint)',
            borderRadius: 'var(--radius-md)',
            display: 'flex',
            alignItems: 'center',
            gap: '0.6rem',
            fontSize: '0.825rem',
            color: 'var(--text-muted)'
          }}>
            <Info size={18} style={{ color: 'var(--primary-emerald)', flexShrink: 0 }} />
            <span>
              <strong>Note:</strong> Items shown are verified nutritional food and ingredient candidates from USDA dataset benchmarks. Cooking instructions or prep times are intentionally not fabricated to ensure high data integrity.
            </span>
          </div>
        </div>

        {/* Search & Filter Controls */}
        <div className="app-card" style={{ padding: '1.25rem', marginBottom: '1.5rem' }}>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))', gap: '1rem' }}>
            {/* Title / Ingredient Search */}
            <div className="form-group" style={{ marginBottom: 0 }}>
              <label>Search Title or Ingredient</label>
              <div style={{ position: 'relative' }}>
                <input
                  type="text"
                  className="input-field"
                  placeholder="e.g. Spinach, Salmon, Quinoa..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  style={{ width: '100%', paddingLeft: '2.5rem' }}
                />
                <Search size={18} style={{ position: 'absolute', left: '0.85rem', top: '50%', transform: 'translateY(-50%)', color: 'var(--text-muted)' }} />
              </div>
            </div>

            {/* Dietary Preference Filter */}
            <div className="form-group" style={{ marginBottom: 0 }}>
              <label>Dietary Preference</label>
              <select
                className="input-field"
                value={selectedDiet}
                onChange={(e) => setSelectedDiet(e.target.value)}
              >
                {DIETARY_OPTIONS.map((opt) => (
                  <option key={opt.value} value={opt.value}>{opt.label}</option>
                ))}
              </select>
            </div>

            {/* Deficiency Targeting */}
            <div className="form-group" style={{ marginBottom: 0 }}>
              <label>Deficiency Targeting</label>
              <select
                className="input-field"
                value={selectedDeficiency}
                onChange={(e) => setSelectedDeficiency(e.target.value)}
              >
                {DEFICIENCY_OPTIONS.map((opt) => (
                  <option key={opt.value} value={opt.value}>{opt.label}</option>
                ))}
              </select>
            </div>

            {/* Food Category */}
            <div className="form-group" style={{ marginBottom: 0 }}>
              <label>Food Category</label>
              <select
                className="input-field"
                value={selectedCategory}
                onChange={(e) => setSelectedCategory(e.target.value)}
                disabled={Boolean(selectedDeficiency)}
              >
                {CATEGORY_OPTIONS.map((cat) => (
                  <option key={cat} value={cat}>{cat}</option>
                ))}
              </select>
            </div>
          </div>

          {/* Advanced Filters Toggle Section */}
          <div style={{
            marginTop: '1rem',
            paddingTop: '1rem',
            borderTop: '1px solid var(--border-subtle)',
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))',
            gap: '1rem'
          }}>
            <div className="form-group" style={{ marginBottom: 0 }}>
              <label style={{ fontSize: '0.8rem' }}>Exclude Allergies (comma-separated)</label>
              <input
                type="text"
                className="input-field"
                placeholder="e.g. peanuts, gluten, milk"
                value={allergiesInput}
                onChange={(e) => setAllergiesInput(e.target.value)}
                style={{ fontSize: '0.875rem', padding: '0.5rem 0.75rem' }}
              />
            </div>
            <div className="form-group" style={{ marginBottom: 0 }}>
              <label style={{ fontSize: '0.8rem' }}>Prohibited Foods (comma-separated)</label>
              <input
                type="text"
                className="input-field"
                placeholder="e.g. pork, beef, sugar"
                value={prohibitedInput}
                onChange={(e) => setProhibitedInput(e.target.value)}
                style={{ fontSize: '0.875rem', padding: '0.5rem 0.75rem' }}
              />
            </div>
            <div className="form-group" style={{ marginBottom: 0 }}>
              <label style={{ fontSize: '0.8rem' }}>Preferred Foods Boost (comma-separated)</label>
              <input
                type="text"
                className="input-field"
                placeholder="e.g. salmon, berries"
                value={preferredInput}
                onChange={(e) => setPreferredInput(e.target.value)}
                style={{ fontSize: '0.875rem', padding: '0.5rem 0.75rem' }}
              />
            </div>
            <div style={{ display: 'flex', alignItems: 'flex-end', justifyContent: 'flex-end' }}>
              <button
                type="button"
                onClick={handleResetFilters}
                className="btn-secondary"
                style={{ fontSize: '0.825rem', padding: '0.5rem 1rem' }}
              >
                Reset Filters
              </button>
            </div>
          </div>
        </div>

        {/* Status Messages */}
        {error && (
          <div className="alert-error">
            <AlertCircle size={20} />
            <span>{error}</span>
          </div>
        )}

        {/* Results Header */}
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '1rem' }}>
          <span style={{ fontSize: '0.9rem', color: 'var(--text-muted)', fontWeight: 500 }}>
            Showing <strong>{recipes.length}</strong> candidate result{recipes.length !== 1 ? 's' : ''} (Total matched: {totalResults})
          </span>
          {selectedDeficiency && (
            <span className="badge badge-amber">
              Targeting: {selectedDeficiency.replace('_', ' ')}
            </span>
          )}
        </div>

        {/* Main Content State Rendering */}
        {loading ? (
          <div className="app-card" style={{ padding: '3rem', textAlign: 'center' }}>
            <div style={{
              display: 'inline-block',
              width: '36px',
              height: '36px',
              border: '3px solid var(--border-mint)',
              borderTopColor: 'var(--primary-emerald)',
              borderRadius: '50%',
              animation: 'spin 0.8s linear infinite'
            }} />
            <p style={{ marginTop: '1rem', color: 'var(--text-muted)', fontSize: '0.925rem' }}>
              Filtering food & recipe candidates based on safety rules...
            </p>
            <style>{`@keyframes spin { to { transform: rotate(360deg); } }`}</style>
          </div>
        ) : recipes.length === 0 ? (
          <div className="app-card" style={{ padding: '3rem', textAlign: 'center' }}>
            <ShieldAlert size={42} style={{ color: 'var(--accent-amber)', marginBottom: '0.75rem' }} />
            <h3 style={{ fontSize: '1.1rem', fontWeight: 600, color: 'var(--text-main)' }}>
              No Safety-Compliant Recipe Candidates Found
            </h3>
            <p style={{ color: 'var(--text-muted)', fontSize: '0.9rem', maxWidth: '450px', margin: '0.5rem auto 1.25rem auto' }}>
              We couldn't find food candidates matching all specified search queries and safety/allergy filters. Try broadening your criteria or removing strict prohibited terms.
            </p>
            <button onClick={handleResetFilters} className="btn-primary" style={{ padding: '0.5rem 1.25rem', fontSize: '0.875rem' }}>
              Reset Filters
            </button>
          </div>
        ) : (
          <div className="grid-3" style={{ gap: '1.25rem' }}>
            {recipes.map((rec) => (
              <div
                key={rec.recipe_id}
                className="app-card"
                onClick={() => setSelectedRecipe(rec)}
                style={{
                  padding: '1.25rem',
                  cursor: 'pointer',
                  display: 'flex',
                  flexDirection: 'column',
                  justifyContent: 'space-between',
                  position: 'relative'
                }}
              >
                <div>
                  {/* Category & Health Score Header */}
                  <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '0.6rem' }}>
                    <span className="badge badge-blue" style={{ fontSize: '0.7rem', textTransform: 'uppercase' }}>
                      {rec.category || 'Food Item'}
                    </span>
                    {rec.health_score !== undefined && rec.health_score !== null && (
                      <span style={{
                        fontSize: '0.75rem',
                        fontWeight: 700,
                        color: rec.health_score >= 70 ? 'var(--primary-emerald)' : 'var(--accent-amber)',
                        display: 'flex',
                        alignItems: 'center',
                        gap: '0.2rem'
                      }}>
                        <Award size={14} /> Score: {Math.round(rec.health_score)}
                      </span>
                    )}
                  </div>

                  {/* Recipe Title */}
                  <h3 style={{
                    fontSize: '1rem',
                    fontWeight: 600,
                    color: 'var(--text-main)',
                    marginBottom: '0.5rem',
                    lineHeight: '1.35',
                    display: '-webkit-box',
                    WebkitLineClamp: 2,
                    WebkitBoxOrient: 'vertical',
                    overflow: 'hidden'
                  }}>
                    {rec.title}
                  </h3>

                  {/* Recommendation Reason if present */}
                  {rec.recommendation_reason && (
                    <div style={{
                      fontSize: '0.775rem',
                      background: 'var(--bg-mint)',
                      color: '#15803d',
                      padding: '0.35rem 0.6rem',
                      borderRadius: 'var(--radius-sm)',
                      marginBottom: '0.6rem'
                    }}>
                      💡 {rec.recommendation_reason}
                    </div>
                  )}

                  {/* Dietary Tags */}
                  {rec.dietary_tags && rec.dietary_tags.length > 0 && (
                    <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.3rem', marginBottom: '0.75rem' }}>
                      {rec.dietary_tags.map(tag => (
                        <span key={tag} className="badge badge-mint" style={{ fontSize: '0.675rem' }}>
                          {tag}
                        </span>
                      ))}
                    </div>
                  )}

                  {/* Macro Summary Pills */}
                  <div style={{
                    display: 'grid',
                    gridTemplateColumns: 'repeat(3, 1fr)',
                    gap: '0.4rem',
                    background: '#f8fafc',
                    padding: '0.5rem',
                    borderRadius: 'var(--radius-sm)',
                    fontSize: '0.75rem',
                    textAlign: 'center',
                    marginBottom: '0.75rem'
                  }}>
                    <div>
                      <div style={{ color: 'var(--text-muted)', fontSize: '0.675rem' }}>Calories</div>
                      <div style={{ fontWeight: 700, color: 'var(--text-main)' }}>
                        {rec.calories != null ? `${Math.round(rec.calories)} kcal` : 'N/A'}
                      </div>
                    </div>
                    <div>
                      <div style={{ color: 'var(--text-muted)', fontSize: '0.675rem' }}>Protein</div>
                      <div style={{ fontWeight: 700, color: 'var(--primary-emerald)' }}>
                        {(rec.protein_g ?? 0).toFixed(1)}g
                      </div>
                    </div>
                    <div>
                      <div style={{ color: 'var(--text-muted)', fontSize: '0.675rem' }}>Carbs</div>
                      <div style={{ fontWeight: 700, color: 'var(--text-main)' }}>
                        {(rec.carbs_g ?? 0).toFixed(1)}g
                      </div>
                    </div>
                  </div>
                </div>

                {/* Card Action Link */}
                <div style={{
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'space-between',
                  paddingTop: '0.6rem',
                  borderTop: '1px solid var(--border-subtle)',
                  fontSize: '0.8rem',
                  color: 'var(--primary-emerald)',
                  fontWeight: 600
                }}>
                  <span>View Nutrition Details</span>
                  <ChevronRight size={16} />
                </div>
              </div>
            ))}
          </div>
        )}

        {/* Detailed Modal Popup */}
        {selectedRecipe && (
          <div className="modal-overlay" onClick={() => setSelectedRecipe(null)}>
            <div
              className="app-card"
              onClick={(e) => e.stopPropagation()}
              style={{
                width: '100%',
                maxWidth: '620px',
                maxHeight: '90vh',
                overflowY: 'auto',
                padding: '1.5rem',
                borderRadius: 'var(--radius-lg)'
              }}
            >
              {/* Modal Header */}
              <div style={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between', marginBottom: '1rem' }}>
                <div>
                  <span className="badge badge-blue" style={{ marginBottom: '0.4rem' }}>
                    {selectedRecipe.category || 'Food Item'}
                  </span>
                  <h2 style={{ fontSize: '1.25rem', fontWeight: 700, color: 'var(--text-main)' }}>
                    {selectedRecipe.title}
                  </h2>
                  <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)', marginTop: '0.2rem' }}>
                    FDC ID: #{selectedRecipe.recipe_id}
                  </div>
                </div>
                <button
                  onClick={() => setSelectedRecipe(null)}
                  style={{ background: 'transparent', border: 'none', cursor: 'pointer', color: 'var(--text-muted)' }}
                >
                  <X size={22} />
                </button>
              </div>

              {/* Recommendation reason if available */}
              {selectedRecipe.recommendation_reason && (
                <div className="alert-success" style={{ marginBottom: '1rem', fontSize: '0.85rem' }}>
                  <Sparkles size={18} />
                  <span><strong>AI Match:</strong> {selectedRecipe.recommendation_reason}</span>
                </div>
              )}

              {/* Serving size & Health score info */}
              <div style={{ display: 'flex', gap: '1rem', marginBottom: '1rem', flexWrap: 'wrap' }}>
                <div style={{ background: '#f8fafc', padding: '0.6rem 0.85rem', borderRadius: 'var(--radius-sm)', flex: 1 }}>
                  <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>Serving Size</div>
                  <div style={{ fontWeight: 600, fontSize: '0.9rem' }}>{selectedRecipe.serving_size} {selectedRecipe.serving_unit}</div>
                </div>
                <div style={{ background: '#f8fafc', padding: '0.6rem 0.85rem', borderRadius: 'var(--radius-sm)', flex: 1 }}>
                  <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>Health Score</div>
                  <div style={{ fontWeight: 600, fontSize: '0.9rem', color: 'var(--primary-emerald)' }}>
                    {selectedRecipe.health_score != null ? `${Math.round(selectedRecipe.health_score)} / 100` : 'N/A'}
                  </div>
                </div>
              </div>

              {/* Ingredients List */}
              <div style={{ marginBottom: '1.25rem' }}>
                <h4 style={{ fontSize: '0.9rem', fontWeight: 600, color: 'var(--text-main)', marginBottom: '0.4rem' }}>
                  Ingredients Composition
                </h4>
                <p style={{ fontSize: '0.85rem', color: 'var(--text-muted)', background: '#f8fafc', padding: '0.75rem', borderRadius: 'var(--radius-sm)', lineHeight: '1.5' }}>
                  {selectedRecipe.ingredients || 'Natural single-ingredient or unlisted composite food product.'}
                </p>
              </div>

              {/* Complete Nutritional Breakdown */}
              <div style={{ marginBottom: '1.25rem' }}>
                <h4 style={{ fontSize: '0.9rem', fontWeight: 600, color: 'var(--text-main)', marginBottom: '0.6rem' }}>
                  Nutritional Breakdown (per serving)
                </h4>
                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(130px, 1fr))', gap: '0.6rem' }}>
                  <div style={{ border: '1px solid var(--border-subtle)', padding: '0.5rem 0.75rem', borderRadius: 'var(--radius-sm)' }}>
                    <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>Calories</span>
                    <div style={{ fontWeight: 600, fontSize: '0.9rem' }}>{selectedRecipe.calories ?? 'N/A'} kcal</div>
                  </div>
                  <div style={{ border: '1px solid var(--border-subtle)', padding: '0.5rem 0.75rem', borderRadius: 'var(--radius-sm)' }}>
                    <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>Protein</span>
                    <div style={{ fontWeight: 600, fontSize: '0.9rem' }}>{selectedRecipe.protein_g ?? '0'} g</div>
                  </div>
                  <div style={{ border: '1px solid var(--border-subtle)', padding: '0.5rem 0.75rem', borderRadius: 'var(--radius-sm)' }}>
                    <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>Carbohydrates</span>
                    <div style={{ fontWeight: 600, fontSize: '0.9rem' }}>{selectedRecipe.carbs_g ?? '0'} g</div>
                  </div>
                  <div style={{ border: '1px solid var(--border-subtle)', padding: '0.5rem 0.75rem', borderRadius: 'var(--radius-sm)' }}>
                    <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>Total Fat</span>
                    <div style={{ fontWeight: 600, fontSize: '0.9rem' }}>{selectedRecipe.fat_g ?? '0'} g</div>
                  </div>
                  <div style={{ border: '1px solid var(--border-subtle)', padding: '0.5rem 0.75rem', borderRadius: 'var(--radius-sm)' }}>
                    <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>Dietary Fiber</span>
                    <div style={{ fontWeight: 600, fontSize: '0.9rem' }}>{selectedRecipe.fiber_g ?? '0'} g</div>
                  </div>
                  <div style={{ border: '1px solid var(--border-subtle)', padding: '0.5rem 0.75rem', borderRadius: 'var(--radius-sm)' }}>
                    <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>Iron</span>
                    <div style={{ fontWeight: 600, fontSize: '0.9rem' }}>{selectedRecipe.iron_mg ?? '0'} mg</div>
                  </div>
                  <div style={{ border: '1px solid var(--border-subtle)', padding: '0.5rem 0.75rem', borderRadius: 'var(--radius-sm)' }}>
                    <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>Vitamin C</span>
                    <div style={{ fontWeight: 600, fontSize: '0.9rem' }}>{selectedRecipe.vitamin_c_mg ?? '0'} mg</div>
                  </div>
                  <div style={{ border: '1px solid var(--border-subtle)', padding: '0.5rem 0.75rem', borderRadius: 'var(--radius-sm)' }}>
                    <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>Calcium</span>
                    <div style={{ fontWeight: 600, fontSize: '0.9rem' }}>{selectedRecipe.calcium_mg ?? '0'} mg</div>
                  </div>
                  <div style={{ border: '1px solid var(--border-subtle)', padding: '0.5rem 0.75rem', borderRadius: 'var(--radius-sm)' }}>
                    <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>Sodium</span>
                    <div style={{ fontWeight: 600, fontSize: '0.9rem' }}>{selectedRecipe.sodium_mg ?? '0'} mg</div>
                  </div>
                  <div style={{ border: '1px solid var(--border-subtle)', padding: '0.5rem 0.75rem', borderRadius: 'var(--radius-sm)' }}>
                    <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>Sugar</span>
                    <div style={{ fontWeight: 600, fontSize: '0.9rem' }}>{selectedRecipe.sugar_g ?? '0'} g</div>
                  </div>
                </div>
              </div>

              {/* Data Integrity Notice */}
              <div style={{
                background: '#f1f5f9',
                padding: '0.75rem 1rem',
                borderRadius: 'var(--radius-sm)',
                fontSize: '0.775rem',
                color: 'var(--text-muted)'
              }}>
                ℹ️ <strong>Candidate Notice:</strong> Nutrient values reflect standardized USDA data. Unmeasured values (such as specific vitamin isomers not present in source benchmark) are excluded to prevent data fabrication.
              </div>

              <div style={{ marginTop: '1.25rem', textAlign: 'right' }}>
                <button
                  onClick={() => setSelectedRecipe(null)}
                  className="btn-secondary"
                  style={{ padding: '0.5rem 1.25rem', fontSize: '0.875rem' }}
                >
                  Close
                </button>
              </div>
            </div>
          </div>
        )}
      </main>
    </div>
  );
};

export default RecipesPage;
