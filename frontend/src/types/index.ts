export interface UserProfile {
  id: string;
  email: string;
  full_name?: string;
  avatar_url?: string;
  created_at: string;
  updated_at: string;
}

export interface HealthProfile {
  id?: string;
  user_id?: string;
  age: number;
  gender: 'male' | 'female' | 'other' | 'prefer_not_to_say';
  height_cm: number;
  weight_kg: number;
  activity_level: 'sedentary' | 'lightly_active' | 'moderately_active' | 'very_active' | 'extra_active';
  dietary_preference: 'omnivore' | 'vegetarian' | 'vegan' | 'keto' | 'paleo' | 'mediterranean' | 'other';
  health_goals: string[];
  allergies_intolerances: string[];
  medical_conditions: string[];
  bmr?: number;
  tdee?: number;
  created_at?: string;
  updated_at?: string;
}

export interface FoodDiaryEntry {
  id?: string;
  user_id?: string;
  logged_date: string; // YYYY-MM-DD
  meal_type: 'breakfast' | 'lunch' | 'dinner' | 'snack';
  food_name: string;
  serving_size: number;
  serving_unit: string;
  calories: number;
  protein_g: number;
  carbs_g: number;
  fat_g: number;
  micros_json?: Record<string, number | string>;
  created_at?: string;
}

export interface DailyNutritionSummary {
  logged_date: string;
  total_calories: number;
  total_protein_g: number;
  total_carbs_g: number;
  total_fat_g: number;
  entry_count: number;
}
