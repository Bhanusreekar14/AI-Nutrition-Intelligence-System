import axios from 'axios';
import { supabase } from './supabase';
import { createDevJwtToken } from '../context/AuthContext';
import { 
  HealthProfile, 
  FoodDiaryEntry, 
  DailyNutritionSummary, 
  NormalizedFoodItem,
  SymptomAssessmentPayload,
  SymptomAssessmentRecord,
  BloodTestEntry,
  DeficiencyPredictionRequest,
  DeficiencyPredictionResponse
} from '../types';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api/v1';

export const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Interceptor to attach JWT Access Token safely
apiClient.interceptors.request.use(async (config) => {
  let token = localStorage.getItem('nutri_access_token');
  
  if (!token) {
    try {
      const timeoutPromise = new Promise<{ data: { session: null } }>((resolve) => 
        setTimeout(() => resolve({ data: { session: null } }), 300)
      );
      const { data } = await Promise.race([
        supabase.auth.getSession(),
        timeoutPromise
      ]);
      token = data?.session?.access_token || null;
    } catch {
      token = null;
    }
  }

  if (!token) {
    let email = 'user@example.com';
    try {
      const savedUser = localStorage.getItem('nutri_user');
      if (savedUser) {
        const parsed = JSON.parse(savedUser);
        if (parsed.email) email = parsed.email;
      }
    } catch {}
    token = createDevJwtToken('00000000-0000-0000-0000-000000000001', email);
  }

  config.headers.Authorization = `Bearer ${token}`;
  return config;
}, (error) => {
  return Promise.reject(error);
});

// Health Profile Endpoints
export const getMyHealthProfile = async (): Promise<HealthProfile> => {
  const response = await apiClient.get<HealthProfile>('/profile/me');
  return response.data;
};

export const saveHealthProfile = async (profile: HealthProfile): Promise<HealthProfile> => {
  const response = await apiClient.post<HealthProfile>('/profile', profile);
  return response.data;
};

// Food Diary Endpoints
export const getFoodDiaryEntries = async (date?: string): Promise<FoodDiaryEntry[]> => {
  const params = date ? { logged_date: date } : {};
  const response = await apiClient.get<FoodDiaryEntry[]>('/diary', { params });
  return response.data;
};

export const createFoodDiaryEntry = async (entry: FoodDiaryEntry): Promise<FoodDiaryEntry> => {
  const response = await apiClient.post<FoodDiaryEntry>('/diary', entry);
  return response.data;
};

export const updateFoodDiaryEntry = async (id: string, entry: Partial<FoodDiaryEntry>): Promise<FoodDiaryEntry> => {
  const response = await apiClient.put<FoodDiaryEntry>(`/diary/${id}`, entry);
  return response.data;
};

export const deleteFoodDiaryEntry = async (id: string): Promise<void> => {
  await apiClient.delete(`/diary/${id}`);
};

export const getDailyNutritionSummary = async (date: string): Promise<DailyNutritionSummary> => {
  const response = await apiClient.get<DailyNutritionSummary>('/diary/summary', {
    params: { logged_date: date },
  });
  return response.data;
};

// Food Search Endpoint
export const searchFoods = async (query: string): Promise<NormalizedFoodItem[]> => {
  const response = await apiClient.get<NormalizedFoodItem[]>('/food/search', {
    params: { q: query },
  });
  return response.data;
};

// Symptoms Endpoints
export const getSymptomAssessments = async (date?: string): Promise<SymptomAssessmentRecord[]> => {
  const params = date ? { assessment_date: date } : {};
  const response = await apiClient.get<SymptomAssessmentRecord[]>('/symptoms', { params });
  return response.data;
};

export const saveSymptomAssessment = async (payload: SymptomAssessmentPayload): Promise<SymptomAssessmentRecord[]> => {
  const response = await apiClient.post<SymptomAssessmentRecord[]>('/symptoms', payload);
  return response.data;
};

// Blood Tests Endpoints
export const getBloodTests = async (): Promise<BloodTestEntry[]> => {
  const response = await apiClient.get<BloodTestEntry[]>('/blood-tests');
  return response.data;
};

export const createBloodTest = async (test: BloodTestEntry): Promise<BloodTestEntry> => {
  const response = await apiClient.post<BloodTestEntry>('/blood-tests', test);
  return response.data;
};

export const updateBloodTest = async (id: string, test: Partial<BloodTestEntry>): Promise<BloodTestEntry> => {
  const response = await apiClient.put<BloodTestEntry>(`/blood-tests/${id}`, test);
  return response.data;
};

// ML Deficiency Risk Prediction Endpoint
export const predictDeficiencyRisk = async (
  payload: DeficiencyPredictionRequest
): Promise<DeficiencyPredictionResponse> => {
  const response = await apiClient.post<DeficiencyPredictionResponse>('/predict', payload);
  return response.data;
};

