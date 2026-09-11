export interface UserProfile {
  id: string;
  email: string;
  full_name?: string;
  avatar_url?: string;
  created_at?: string;
  updated_at?: string;
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
  health_goal?: string;
  target_value?: string;
  target_unit?: string;
  target_period?: string;
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
  external_food_id?: string;
  source?: string;
  serving_size: number;
  serving_unit: string;
  calories: number;
  protein_g: number;
  carbs_g: number;
  fat_g: number;
  fiber_g?: number;
  sugar_g?: number;
  sodium_mg?: number;
  vitamin_d_mcg?: number;
  vitamin_b12_mcg?: number;
  iron_mg?: number;
  calcium_mg?: number;
  micros_json?: Record<string, any>;
  created_at?: string;
}

export interface DailyNutritionSummary {
  logged_date: string;
  total_calories: number;
  total_protein_g: number;
  total_carbs_g: number;
  total_fat_g: number;
  total_fiber_g: number;
  total_sugar_g: number;
  total_sodium_mg: number;
  total_vitamin_d_mcg: number;
  total_vitamin_b12_mcg: number;
  total_iron_mg: number;
  total_calcium_mg: number;
  entry_count: number;
}

export interface NormalizedFoodItem {
  id: string;
  source: 'usda' | 'openfoodfacts';
  externalId: string;
  name: string;
  servingSize: number;
  servingUnit: string;
  calories: number;
  protein: number;
  carbohydrates: number;
  fat: number;
  fiber: number;
  sugar: number;
  sodium: number;
  vitaminD: number;
  vitaminB12: number;
  iron: number;
  calcium: number;
}

export interface SymptomItem {
  symptom: string;
  severity: 'Never' | 'Sometimes' | 'Often' | 'Very Often';
}

export interface SymptomAssessmentPayload {
  assessment_date: string;
  assessments: SymptomItem[];
}

export interface SymptomAssessmentRecord {
  id: string;
  user_id: string;
  symptom: string;
  severity: string;
  assessment_date: string;
  created_at: string;
}

export interface BloodTestEntry {
  id?: string;
  user_id?: string;
  test_date: string;
  hemoglobin?: number | string;
  vitamin_d?: number | string;
  vitamin_b12?: number | string;
  iron?: number | string;
  calcium?: number | string;
  report_file_reference?: string | null;
  created_at?: string;
  updated_at?: string;
}

export interface DeficiencyPredictionRequest {
  age?: number;
  gender?: string;
  bmi?: number;
  diet_type?: string;
  smoking_status?: string;
  alcohol_consumption?: string;
  exercise_level?: string;
  sun_exposure?: string;
  income_level?: string;
  latitude_region?: string;

  vitamin_a_percent_rda?: number;
  vitamin_c_percent_rda?: number;
  vitamin_d_percent_rda?: number;
  vitamin_e_percent_rda?: number;
  vitamin_k_percent_rda?: number;
  thiamin_b1_percent_rda?: number;
  riboflavin_b2_percent_rda?: number;
  niacin_b3_percent_rda?: number;
  vitamin_b6_percent_rda?: number;
  folate_b9_percent_rda?: number;
  vitamin_b12_percent_rda?: number;
  calcium_percent_rda?: number;
  iron_percent_rda?: number;
  magnesium_percent_rda?: number;
  zinc_percent_rda?: number;
  potassium_percent_rda?: number;

  hemoglobin_g_dl?: number;
  serum_vitamin_d_ng_ml?: number;
  serum_vitamin_b12_pg_ml?: number;
  serum_folate_ng_ml?: number;

  symptoms_count?: number;
  has_fatigue?: boolean;
  has_weakness?: boolean;
  has_dizziness?: boolean;
  has_hair_loss?: boolean;
  has_brittle_nails?: boolean;
  has_pale_skin?: boolean;
  has_bone_pain?: boolean;
  has_muscle_cramps?: boolean;
  has_numbness_tingling?: boolean;
  has_night_blindness?: boolean;
  has_mouth_sores?: boolean;
  has_slow_wound_healing?: boolean;
}

export interface SHAPFeatureContribution {
  feature: string;
  shap_value: number;
}

export interface SHAPExplanation {
  top_positive_features: SHAPFeatureContribution[];
  top_negative_features: SHAPFeatureContribution[];
}

export interface DeficiencyPredictionResponse {
  predicted_class: string;
  predicted_probability: number;
  risk_score: number;
  risk_level: string;
  class_probabilities: Record<string, number>;
  explanation: SHAPExplanation;
  medical_disclaimer: string;
}

