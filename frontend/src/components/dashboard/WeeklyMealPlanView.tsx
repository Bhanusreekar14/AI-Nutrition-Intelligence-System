import React, { useState } from 'react';
import { WeeklyMealPlan, MealType, RecommendedFood } from '../../types';
import { Calendar, RefreshCw, Utensils, Info } from 'lucide-react';

interface Props {
  weeklyPlan: WeeklyMealPlan | null;
  onReplaceItem: (dayNum: number, mealType: MealType, foodName: string) => Promise<void>;
  loadingReplace: boolean;
  onRefreshPlan: () => void;
}

export const WeeklyMealPlanView: React.FC<Props> = ({
  weeklyPlan,
  onReplaceItem,
  loadingReplace,
  onRefreshPlan
}) => {
  const [activeDay, setActiveDay] = useState<number>(1);
  const [replacingFoodName, setReplacingFoodName] = useState<string | null>(null);

  if (!weeklyPlan || !weeklyPlan.days || weeklyPlan.days.length === 0) {
    return (
      <div className="app-card" style={{ padding: '2rem', textAlign: 'center', marginBottom: '1.5rem' }}>
        <Utensils size={36} style={{ color: 'var(--primary-emerald)', marginBottom: '0.5rem' }} />
        <h3 style={{ fontSize: '1.1rem', fontWeight: 600, color: 'var(--text-main)' }}>
          No 7-Day Meal Plan Generated
        </h3>
        <p style={{ fontSize: '0.875rem', color: 'var(--text-muted)', marginBottom: '1rem' }}>
          Generate a personalized, safety-filtered 7-day meal plan tailored to your nutritional targets.
        </p>
        <button onClick={onRefreshPlan} className="btn-primary" style={{ fontSize: '0.875rem' }}>
          Generate Meal Plan
        </button>
      </div>
    );
  }

  const currentDayPlan = weeklyPlan.days.find(d => d.day === activeDay) || weeklyPlan.days[0];
  const mealTypes: MealType[] = ['breakfast', 'lunch', 'snack', 'dinner'];

  const handleReplaceClick = async (dayNum: number, mealType: MealType, foodName: string) => {
    setReplacingFoodName(foodName);
    try {
      await onReplaceItem(dayNum, mealType, foodName);
    } finally {
      setReplacingFoodName(null);
    }
  };

  return (
    <div className="app-card" style={{ padding: '1.5rem', marginBottom: '1.5rem' }}>
      {/* Header Banner */}
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '1rem', flexWrap: 'wrap', gap: '0.5rem' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
          <Calendar size={20} style={{ color: 'var(--primary-emerald)' }} />
          <h3 style={{ fontSize: '1.05rem', fontWeight: 700, color: 'var(--text-main)' }}>
            Personalized 7-Day Meal Plan
          </h3>
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
          <span className="badge badge-mint">
            Target: {weeklyPlan.deficiency_class.replace('_', ' ')}
          </span>
          <button
            onClick={onRefreshPlan}
            className="btn-secondary"
            style={{ fontSize: '0.775rem', padding: '0.35rem 0.75rem' }}
            disabled={loadingReplace}
          >
            <RefreshCw size={14} /> Regenerate Plan
          </button>
        </div>
      </div>

      {/* Day Selector Tabs */}
      <div style={{ display: 'flex', gap: '0.4rem', overflowX: 'auto', paddingBottom: '0.5rem', marginBottom: '1.25rem' }}>
        {weeklyPlan.days.map((d) => (
          <button
            key={d.day}
            onClick={() => setActiveDay(d.day)}
            style={{
              padding: '0.5rem 0.85rem',
              borderRadius: 'var(--radius-md)',
              border: d.day === activeDay ? '1px solid var(--primary-emerald)' : '1px solid var(--border-subtle)',
              background: d.day === activeDay ? 'var(--bg-mint)' : '#ffffff',
              color: d.day === activeDay ? 'var(--primary-emerald)' : 'var(--text-muted)',
              fontWeight: d.day === activeDay ? 700 : 500,
              fontSize: '0.85rem',
              cursor: 'pointer',
              whiteSpace: 'nowrap',
              transition: 'all 0.2s ease'
            }}
          >
            Day {d.day}
          </button>
        ))}
      </div>

      {/* Daily Summary Bar */}
      <div style={{
        background: '#f8fafc',
        padding: '0.75rem 1rem',
        borderRadius: 'var(--radius-md)',
        border: '1px solid var(--border-subtle)',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        flexWrap: 'wrap',
        gap: '0.75rem',
        marginBottom: '1.25rem'
      }}>
        <span style={{ fontSize: '0.85rem', fontWeight: 600, color: 'var(--text-main)' }}>
          Day {currentDayPlan.day} Nutritional Totals
        </span>
        <div style={{ display: 'flex', gap: '1rem', fontSize: '0.8rem' }}>
          <span><strong>{Math.round(currentDayPlan.total_calories)}</strong> kcal</span>
          <span><strong style={{ color: 'var(--primary-emerald)' }}>{currentDayPlan.total_protein_g.toFixed(1)}g</strong> protein</span>
          <span><strong style={{ color: '#0284c7' }}>{currentDayPlan.total_carbs_g.toFixed(1)}g</strong> carbs</span>
          <span><strong style={{ color: '#d97706' }}>{currentDayPlan.total_fat_g.toFixed(1)}g</strong> fat</span>
        </div>
      </div>

      {/* Meal Slots (Breakfast, Lunch, Snack, Dinner) */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(240px, 1fr))', gap: '1rem', marginBottom: '1.25rem' }}>
        {mealTypes.map((mType) => {
          const mealSlot = currentDayPlan.meals[mType];
          const selectedFoods: RecommendedFood[] = mealSlot?.selected_foods || [];

          return (
            <div
              key={mType}
              style={{
                background: '#ffffff',
                border: '1px solid var(--border-subtle)',
                borderRadius: 'var(--radius-md)',
                padding: '1rem'
              }}
            >
              <div style={{ textTransform: 'capitalize', fontWeight: 700, fontSize: '0.9rem', color: 'var(--text-main)', marginBottom: '0.6rem', borderBottom: '1px solid var(--border-subtle)', paddingBottom: '0.4rem' }}>
                🍽️ {mType}
              </div>

              {selectedFoods.length === 0 ? (
                <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)', fontStyle: 'italic', padding: '0.5rem 0' }}>
                  No items selected
                </div>
              ) : (
                <div style={{ display: 'flex', flexDirection: 'column', gap: '0.6rem' }}>
                  {selectedFoods.map((food) => {
                    const isReplacingThis = replacingFoodName === food.food_name && loadingReplace;
                    return (
                      <div
                        key={food.food_name}
                        style={{
                          background: '#f8fafc',
                          padding: '0.6rem 0.75rem',
                          borderRadius: 'var(--radius-sm)',
                          fontSize: '0.825rem',
                          display: 'flex',
                          alignItems: 'flex-start',
                          justifyContent: 'space-between',
                          gap: '0.5rem'
                        }}
                      >
                        <div>
                          <div style={{ fontWeight: 600, color: 'var(--text-main)', lineHeight: '1.3' }}>
                            {food.food_name}
                          </div>
                          <div style={{ fontSize: '0.725rem', color: 'var(--text-muted)', marginTop: '0.2rem' }}>
                            {food.calories != null ? `${Math.round(food.calories)} kcal` : 'N/A'} • {food.protein_g ?? 0}g protein
                          </div>
                        </div>

                        <button
                          onClick={() => handleReplaceClick(currentDayPlan.day, mType, food.food_name)}
                          className="btn-secondary"
                          style={{ fontSize: '0.7rem', padding: '0.25rem 0.5rem', whiteSpace: 'nowrap' }}
                          disabled={loadingReplace}
                          title="Replace with alternative food item"
                        >
                          {isReplacingThis ? 'Replacing...' : 'Swap'}
                        </button>
                      </div>
                    );
                  })}
                </div>
              )}
            </div>
          );
        })}
      </div>

      {/* Mandatory Disclaimer Notice */}
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
        <span>{weeklyPlan.medical_disclaimer}</span>
      </div>
    </div>
  );
};
