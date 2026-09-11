-- Migration: 00002_week2_schema_updates.sql
-- Description: Add health goal fields, food diary micro-nutrients, symptom assessments, and blood test results tables with RLS.

-- ============================================================================
-- 1. EXTEND HEALTH PROFILES FOR GOAL & TARGET STORAGE
-- ============================================================================
ALTER TABLE public.health_profiles
ADD COLUMN IF NOT EXISTS health_goal TEXT DEFAULT 'Improve Nutrition',
ADD COLUMN IF NOT EXISTS target_value TEXT DEFAULT 'Improve daily nutrition',
ADD COLUMN IF NOT EXISTS target_unit TEXT DEFAULT '',
ADD COLUMN IF NOT EXISTS target_period TEXT DEFAULT 'This Month';

-- ============================================================================
-- 2. EXTEND FOOD DIARY FOR DETAILED NUTRIENT TRACKING
-- ============================================================================
ALTER TABLE public.food_diary
ADD COLUMN IF NOT EXISTS external_food_id TEXT,
ADD COLUMN IF NOT EXISTS source TEXT DEFAULT 'manual',
ADD COLUMN IF NOT EXISTS fiber_g NUMERIC(6,2) DEFAULT 0 CHECK (fiber_g >= 0),
ADD COLUMN IF NOT EXISTS sugar_g NUMERIC(6,2) DEFAULT 0 CHECK (sugar_g >= 0),
ADD COLUMN IF NOT EXISTS sodium_mg NUMERIC(7,2) DEFAULT 0 CHECK (sodium_mg >= 0),
ADD COLUMN IF NOT EXISTS vitamin_d_mcg NUMERIC(6,2) DEFAULT 0 CHECK (vitamin_d_mcg >= 0),
ADD COLUMN IF NOT EXISTS vitamin_b12_mcg NUMERIC(6,2) DEFAULT 0 CHECK (vitamin_b12_mcg >= 0),
ADD COLUMN IF NOT EXISTS iron_mg NUMERIC(6,2) DEFAULT 0 CHECK (iron_mg >= 0),
ADD COLUMN IF NOT EXISTS calcium_mg NUMERIC(6,2) DEFAULT 0 CHECK (calcium_mg >= 0);

-- ============================================================================
-- 3. SYMPTOM ASSESSMENTS TABLE
-- ============================================================================
CREATE TABLE IF NOT EXISTS public.symptom_assessments (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES public.profiles(id) ON DELETE CASCADE,
    symptom TEXT NOT NULL,
    severity TEXT NOT NULL CHECK (severity IN ('Never', 'Sometimes', 'Often', 'Very Often')),
    assessment_date DATE NOT NULL DEFAULT CURRENT_DATE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Index for querying symptoms by user and date
CREATE INDEX IF NOT EXISTS idx_symptom_assessments_user ON public.symptom_assessments(user_id, assessment_date);

-- ============================================================================
-- 4. BLOOD TEST RESULTS TABLE
-- ============================================================================
CREATE TABLE IF NOT EXISTS public.blood_test_results (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES public.profiles(id) ON DELETE CASCADE,
    test_date DATE NOT NULL DEFAULT CURRENT_DATE,
    hemoglobin NUMERIC(5,2),
    vitamin_d NUMERIC(6,2),
    vitamin_b12 NUMERIC(7,2),
    iron NUMERIC(6,2),
    calcium NUMERIC(6,2),
    report_file_reference TEXT, -- Nullable for future Supabase Storage integration
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Index for querying blood tests by user
CREATE INDEX IF NOT EXISTS idx_blood_test_results_user ON public.blood_test_results(user_id, test_date);

-- ============================================================================
-- 5. ROW LEVEL SECURITY (RLS) POLICIES
-- ============================================================================
ALTER TABLE public.symptom_assessments ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.blood_test_results ENABLE ROW LEVEL SECURITY;

-- Symptom Assessments Policies
DROP POLICY IF EXISTS "Users can view own symptom assessments" ON public.symptom_assessments;
CREATE POLICY "Users can view own symptom assessments" ON public.symptom_assessments FOR SELECT USING (auth.uid() = user_id);

DROP POLICY IF EXISTS "Users can insert own symptom assessments" ON public.symptom_assessments;
CREATE POLICY "Users can insert own symptom assessments" ON public.symptom_assessments FOR INSERT WITH CHECK (auth.uid() = user_id);

DROP POLICY IF EXISTS "Users can update own symptom assessments" ON public.symptom_assessments;
CREATE POLICY "Users can update own symptom assessments" ON public.symptom_assessments FOR UPDATE USING (auth.uid() = user_id);

DROP POLICY IF EXISTS "Users can delete own symptom assessments" ON public.symptom_assessments;
CREATE POLICY "Users can delete own symptom assessments" ON public.symptom_assessments FOR DELETE USING (auth.uid() = user_id);

-- Blood Test Results Policies
DROP POLICY IF EXISTS "Users can view own blood test results" ON public.blood_test_results;
CREATE POLICY "Users can view own blood test results" ON public.blood_test_results FOR SELECT USING (auth.uid() = user_id);

DROP POLICY IF EXISTS "Users can insert own blood test results" ON public.blood_test_results;
CREATE POLICY "Users can insert own blood test results" ON public.blood_test_results FOR INSERT WITH CHECK (auth.uid() = user_id);

DROP POLICY IF EXISTS "Users can update own blood test results" ON public.blood_test_results;
CREATE POLICY "Users can update own blood test results" ON public.blood_test_results FOR UPDATE USING (auth.uid() = user_id);

DROP POLICY IF EXISTS "Users can delete own blood test results" ON public.blood_test_results;
CREATE POLICY "Users can delete own blood test results" ON public.blood_test_results FOR DELETE USING (auth.uid() = user_id);
