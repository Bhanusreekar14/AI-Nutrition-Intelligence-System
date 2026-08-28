import axios from 'axios';
import { supabase } from './supabase';
import { HealthProfile, FoodDiaryEntry, DailyNutritionSummary } from '../types';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api/v1';

export const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Interceptor to attach Supabase JWT Access Token
apiClient.interceptors.request.use(async (config) => {
  const { data } = await supabase.auth.getSession();
  const token = data.session?.access_token;
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
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

export const deleteFoodDiaryEntry = async (id: string): Promise<void> => {
  await apiClient.delete(`/diary/${id}`);
};

export const getDailyNutritionSummary = async (date: string): Promise<DailyNutritionSummary> => {
  const response = await apiClient.get<DailyNutritionSummary>('/diary/summary', {
    params: { logged_date: date },
  });
  return response.data;
};
