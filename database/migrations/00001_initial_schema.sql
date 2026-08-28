-- Migration: 00001_initial_schema.sql
-- Description: Create initial tables, triggers, and Row Level Security (RLS) policies for AI Nutrition System

-- ============================================================================
-- 1. EXTENDED USER PROFILES TABLE
-- ============================================================================
CREATE TABLE IF NOT EXISTS public.profiles (
    id UUID PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
    email TEXT NOT NULL UNIQUE,
    full_name TEXT,
    avatar_url TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- ============================================================================
-- 2. HEALTH PROFILES TABLE (1:1 with public.profiles)
-- ============================================================================
CREATE TABLE IF NOT EXISTS public.health_profiles (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL UNIQUE REFERENCES public.profiles(id) ON DELETE CASCADE,
    age INT NOT NULL CHECK (age > 0 AND age < 120),
    gender TEXT NOT NULL CHECK (gender IN ('male', 'female', 'other', 'prefer_not_to_say')),
    height_cm NUMERIC(5,2) NOT NULL CHECK (height_cm > 0),
    weight_kg NUMERIC(5,2) NOT NULL CHECK (weight_kg > 0),
    activity_level TEXT NOT NULL CHECK (
        activity_level IN ('sedentary', 'lightly_active', 'moderately_active', 'very_active', 'extra_active')
    ),
    dietary_preference TEXT NOT NULL DEFAULT 'omnivore' CHECK (
        dietary_preference IN ('omnivore', 'vegetarian', 'vegan', 'keto', 'paleo', 'mediterranean', 'other')
    ),
    health_goals TEXT[] DEFAULT '{}',
    allergies_intolerances TEXT[] DEFAULT '{}',
    medical_conditions TEXT[] DEFAULT '{}',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- ============================================================================
-- 3. FOOD DIARY TABLE (1:N with public.profiles)
-- ============================================================================
CREATE TABLE IF NOT EXISTS public.food_diary (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES public.profiles(id) ON DELETE CASCADE,
    logged_date DATE NOT NULL DEFAULT CURRENT_DATE,
    meal_type TEXT NOT NULL CHECK (meal_type IN ('breakfast', 'lunch', 'dinner', 'snack')),
    food_name TEXT NOT NULL,
    serving_size NUMERIC(6,2) NOT NULL DEFAULT 1.0 CHECK (serving_size > 0),
    serving_unit TEXT NOT NULL DEFAULT 'g',
    calories NUMERIC(7,2) NOT NULL DEFAULT 0 CHECK (calories >= 0),
    protein_g NUMERIC(6,2) NOT NULL DEFAULT 0 CHECK (protein_g >= 0),
    carbs_g NUMERIC(6,2) NOT NULL DEFAULT 0 CHECK (carbs_g >= 0),
    fat_g NUMERIC(6,2) NOT NULL DEFAULT 0 CHECK (fat_g >= 0),
    micros_json JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Index for date queries per user
CREATE INDEX IF NOT EXISTS idx_food_diary_user_date ON public.food_diary(user_id, logged_date);

-- ============================================================================
-- 4. AUTOMATED USER PROVISIONING TRIGGER
-- ============================================================================
CREATE OR REPLACE FUNCTION public.handle_new_user()
RETURNS TRIGGER AS $$
BEGIN
    INSERT INTO public.profiles (id, email, full_name, avatar_url)
    VALUES (
        NEW.id,
        NEW.email,
        NEW.raw_user_meta_data->>'full_name',
        NEW.raw_user_meta_data->>'avatar_url'
    )
    ON CONFLICT (id) DO UPDATE SET
        email = EXCLUDED.email,
        full_name = COALESCE(EXCLUDED.full_name, public.profiles.full_name),
        updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Recreate trigger cleanly
DROP TRIGGER IF EXISTS on_auth_user_created ON auth.users;
CREATE TRIGGER on_auth_user_created
    AFTER INSERT ON auth.users
    FOR EACH ROW EXECUTE FUNCTION public.handle_new_user();

-- ============================================================================
-- 5. ROW LEVEL SECURITY (RLS) POLICIES
-- ============================================================================
ALTER TABLE public.profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.health_profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.food_diary ENABLE ROW LEVEL SECURITY;

-- Profiles Policies
DROP POLICY IF EXISTS "Users can view own profile" ON public.profiles;
CREATE POLICY "Users can view own profile" ON public.profiles FOR SELECT USING (auth.uid() = id);

DROP POLICY IF EXISTS "Users can update own profile" ON public.profiles;
CREATE POLICY "Users can update own profile" ON public.profiles FOR UPDATE USING (auth.uid() = id);

-- Health Profiles Policies
DROP POLICY IF EXISTS "Users can view own health profile" ON public.health_profiles;
CREATE POLICY "Users can view own health profile" ON public.health_profiles FOR SELECT USING (auth.uid() = user_id);

DROP POLICY IF EXISTS "Users can insert own health profile" ON public.health_profiles;
CREATE POLICY "Users can insert own health profile" ON public.health_profiles FOR INSERT WITH CHECK (auth.uid() = user_id);

DROP POLICY IF EXISTS "Users can update own health profile" ON public.health_profiles;
CREATE POLICY "Users can update own health profile" ON public.health_profiles FOR UPDATE USING (auth.uid() = user_id);

-- Food Diary Policies
DROP POLICY IF EXISTS "Users can view own food diary" ON public.food_diary;
CREATE POLICY "Users can view own food diary" ON public.food_diary FOR SELECT USING (auth.uid() = user_id);

DROP POLICY IF EXISTS "Users can insert own food diary" ON public.food_diary;
CREATE POLICY "Users can insert own food diary" ON public.food_diary FOR INSERT WITH CHECK (auth.uid() = user_id);

DROP POLICY IF EXISTS "Users can update own food diary" ON public.food_diary;
CREATE POLICY "Users can update own food diary" ON public.food_diary FOR UPDATE USING (auth.uid() = user_id);

DROP POLICY IF EXISTS "Users can delete own food diary" ON public.food_diary;
CREATE POLICY "Users can delete own food diary" ON public.food_diary FOR DELETE USING (auth.uid() = user_id);
