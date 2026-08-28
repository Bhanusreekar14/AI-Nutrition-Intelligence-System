import { DailyNutritionSummary } from '../types';

export interface MacroTargets {
  protein_g: number;
  carbs_g: number;
  fat_g: number;
}

export interface CalorieProgress {
  remaining: number;
  excess: number;
  percentage: number;
  visualPercentage: number;
}

export interface NutritionStatus {
  label: 'ON TRACK' | 'APPROACHING LIMIT' | 'TARGET EXCEEDED' | 'NO TARGET';
  color: string;
  bg: string;
  icon: string;
}

/**
 * Calculates suggested daily macronutrient targets based on TDEE.
 * Protein: 20% of calories (4 kcal/g)
 * Carbs: 50% of calories (4 kcal/g)
 * Fat: 30% of calories (9 kcal/g)
 */
export const calculateMacroTargets = (tdee: number): MacroTargets => {
  if (!tdee || tdee <= 0) {
    return { protein_g: 0, carbs_g: 0, fat_g: 0 };
  }

  return {
    protein_g: Math.round((tdee * 0.20) / 4),
    carbs_g: Math.round((tdee * 0.50) / 4),
    fat_g: Math.round((tdee * 0.30) / 9),
  };
};

/**
 * Calculates remaining calories, excess calories, and progress percentage.
 * Visual progress percentage is visually capped at 100%.
 */
export const calculateCalorieProgress = (consumed: number, target: number): CalorieProgress => {
  if (!target || target <= 0) {
    return {
      remaining: 0,
      excess: 0,
      percentage: 0,
      visualPercentage: 0,
    };
  }

  const rawPercentage = (consumed / target) * 100;
  const percentage = Math.round(rawPercentage);
  const visualPercentage = Math.min(100, Math.max(0, percentage));
  const excess = consumed > target ? Math.round(consumed - target) : 0;
  const remaining = Math.max(0, Math.round(target - consumed));

  return {
    remaining,
    excess,
    percentage,
    visualPercentage,
  };
};

/**
 * Determines the rule-based nutrition status based on consumption vs target.
 * <= 80%: ON TRACK
 * 80% - 100%: APPROACHING LIMIT
 * > 100%: TARGET EXCEEDED
 */
export const getNutritionStatus = (consumed: number, target: number): NutritionStatus => {
  if (!target || target <= 0) {
    return {
      label: 'NO TARGET',
      color: 'var(--text-muted)',
      bg: 'rgba(255, 255, 255, 0.05)',
      icon: '⚪',
    };
  }

  const ratio = consumed / target;

  if (ratio <= 0.8) {
    return {
      label: 'ON TRACK',
      color: '#34d399',
      bg: 'rgba(52, 211, 153, 0.15)',
      icon: '🟢',
    };
  } else if (ratio <= 1.0) {
    return {
      label: 'APPROACHING LIMIT',
      color: '#fbbf24',
      bg: 'rgba(251, 191, 36, 0.15)',
      icon: '🟡',
    };
  } else {
    return {
      label: 'TARGET EXCEEDED',
      color: '#f43f5e',
      bg: 'rgba(244, 63, 94, 0.15)',
      icon: '🔴',
    };
  }
};

/**
 * Generates data-driven personalized nutrition insights based on actual user data.
 */
export const generateNutritionInsights = (
  consumedCalories: number,
  dailyTarget: number,
  summary: DailyNutritionSummary,
  macroTargets: MacroTargets
): string[] => {
  const insights: string[] = [];

  if (!dailyTarget || dailyTarget <= 0) {
    insights.push('Complete your Health Profile to unlock personalized daily targets and insights.');
    return insights;
  }

  // 1. Calorie Insights
  const { remaining, excess } = calculateCalorieProgress(consumedCalories, dailyTarget);
  if (consumedCalories > dailyTarget) {
    insights.push(`You have exceeded your daily calorie target by ${excess} kcal.`);
  } else if (remaining > 0) {
    insights.push(`You have ${remaining} kcal remaining for today.`);
  } else {
    insights.push('You have reached your daily calorie target.');
  }

  // 2. Protein Insights
  if (macroTargets.protein_g > 0) {
    if (summary.total_protein_g < macroTargets.protein_g * 0.5) {
      insights.push('Your protein intake is currently below your suggested target.');
    } else if (summary.total_protein_g >= macroTargets.protein_g) {
      insights.push('You have reached your suggested protein target.');
    }
  }

  // 3. Carbohydrates Insights
  if (macroTargets.carbs_g > 0) {
    if (summary.total_carbs_g >= macroTargets.carbs_g * 0.8 && summary.total_carbs_g <= macroTargets.carbs_g) {
      insights.push('Your carbohydrate intake is approaching your suggested daily target.');
    } else if (summary.total_carbs_g > macroTargets.carbs_g) {
      insights.push('Your carbohydrate intake has exceeded your suggested target.');
    }
  }

  // 4. Fat Insights
  if (macroTargets.fat_g > 0) {
    if (summary.total_fat_g >= macroTargets.fat_g * 0.8 && summary.total_fat_g <= macroTargets.fat_g) {
      insights.push('Your fat intake is approaching your suggested daily target.');
    } else if (summary.total_fat_g > macroTargets.fat_g) {
      insights.push('Your fat intake has exceeded your suggested target.');
    }
  }

  return insights;
};
