-- Migration: 20260909175500_enable_rls_for_user_data.sql
-- Description: Enable Row Level Security (RLS) and enforce strict owner-only access policies for user data tables.

-- ============================================================================
-- 1. ENABLE ROW LEVEL SECURITY (RLS)
-- ============================================================================
ALTER TABLE public.profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.health_profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.food_diary ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.symptom_assessments ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.blood_test_results ENABLE ROW LEVEL SECURITY;

-- ============================================================================
-- 2. TABLE LEVEL GRANTS (Role Permissions)
-- Revoke all table access from anonymous users.
-- Grant standard CRUD privileges to authenticated users (RLS will restrict row access).
-- ============================================================================
REVOKE ALL ON TABLE public.profiles FROM anon, public;
REVOKE ALL ON TABLE public.health_profiles FROM anon, public;
REVOKE ALL ON TABLE public.food_diary FROM anon, public;
REVOKE ALL ON TABLE public.symptom_assessments FROM anon, public;
REVOKE ALL ON TABLE public.blood_test_results FROM anon, public;

GRANT SELECT, INSERT, UPDATE, DELETE ON TABLE public.profiles TO authenticated;
GRANT SELECT, INSERT, UPDATE, DELETE ON TABLE public.health_profiles TO authenticated;
GRANT SELECT, INSERT, UPDATE, DELETE ON TABLE public.food_diary TO authenticated;
GRANT SELECT, INSERT, UPDATE, DELETE ON TABLE public.symptom_assessments TO authenticated;
GRANT SELECT, INSERT, UPDATE, DELETE ON TABLE public.blood_test_results TO authenticated;

-- Service role bypasses RLS for system operations
GRANT ALL ON TABLE public.profiles TO service_role;
GRANT ALL ON TABLE public.health_profiles TO service_role;
GRANT ALL ON TABLE public.food_diary TO service_role;
GRANT ALL ON TABLE public.symptom_assessments TO service_role;
GRANT ALL ON TABLE public.blood_test_results TO service_role;

-- ============================================================================
-- 3. POLICIES FOR public.profiles
-- Owner column: id (references auth.users.id)
-- ============================================================================
DROP POLICY IF EXISTS "Users can view own profile" ON public.profiles;
CREATE POLICY "Users can view own profile" 
    ON public.profiles FOR SELECT 
    TO authenticated 
    USING (auth.uid() = id);

DROP POLICY IF EXISTS "Users can insert own profile" ON public.profiles;
CREATE POLICY "Users can insert own profile" 
    ON public.profiles FOR INSERT 
    TO authenticated 
    WITH CHECK (auth.uid() = id);

DROP POLICY IF EXISTS "Users can update own profile" ON public.profiles;
CREATE POLICY "Users can update own profile" 
    ON public.profiles FOR UPDATE 
    TO authenticated 
    USING (auth.uid() = id) 
    WITH CHECK (auth.uid() = id);

DROP POLICY IF EXISTS "Users can delete own profile" ON public.profiles;
CREATE POLICY "Users can delete own profile" 
    ON public.profiles FOR DELETE 
    TO authenticated 
    USING (auth.uid() = id);

-- ============================================================================
-- 4. POLICIES FOR public.health_profiles
-- Owner column: user_id (references public.profiles.id)
-- ============================================================================
DROP POLICY IF EXISTS "Users can view own health profile" ON public.health_profiles;
CREATE POLICY "Users can view own health profile" 
    ON public.health_profiles FOR SELECT 
    TO authenticated 
    USING (auth.uid() = user_id);

DROP POLICY IF EXISTS "Users can insert own health profile" ON public.health_profiles;
CREATE POLICY "Users can insert own health profile" 
    ON public.health_profiles FOR INSERT 
    TO authenticated 
    WITH CHECK (auth.uid() = user_id);

DROP POLICY IF EXISTS "Users can update own health profile" ON public.health_profiles;
CREATE POLICY "Users can update own health profile" 
    ON public.health_profiles FOR UPDATE 
    TO authenticated 
    USING (auth.uid() = user_id) 
    WITH CHECK (auth.uid() = user_id);

DROP POLICY IF EXISTS "Users can delete own health profile" ON public.health_profiles;
CREATE POLICY "Users can delete own health profile" 
    ON public.health_profiles FOR DELETE 
    TO authenticated 
    USING (auth.uid() = user_id);

-- ============================================================================
-- 5. POLICIES FOR public.food_diary
-- Owner column: user_id (references public.profiles.id)
-- ============================================================================
DROP POLICY IF EXISTS "Users can view own food diary" ON public.food_diary;
CREATE POLICY "Users can view own food diary" 
    ON public.food_diary FOR SELECT 
    TO authenticated 
    USING (auth.uid() = user_id);

DROP POLICY IF EXISTS "Users can insert own food diary" ON public.food_diary;
CREATE POLICY "Users can insert own food diary" 
    ON public.food_diary FOR INSERT 
    TO authenticated 
    WITH CHECK (auth.uid() = user_id);

DROP POLICY IF EXISTS "Users can update own food diary" ON public.food_diary;
CREATE POLICY "Users can update own food diary" 
    ON public.food_diary FOR UPDATE 
    TO authenticated 
    USING (auth.uid() = user_id) 
    WITH CHECK (auth.uid() = user_id);

DROP POLICY IF EXISTS "Users can delete own food diary" ON public.food_diary;
CREATE POLICY "Users can delete own food diary" 
    ON public.food_diary FOR DELETE 
    TO authenticated 
    USING (auth.uid() = user_id);

-- ============================================================================
-- 6. POLICIES FOR public.symptom_assessments
-- Owner column: user_id (references public.profiles.id)
-- ============================================================================
DROP POLICY IF EXISTS "Users can view own symptom assessments" ON public.symptom_assessments;
CREATE POLICY "Users can view own symptom assessments" 
    ON public.symptom_assessments FOR SELECT 
    TO authenticated 
    USING (auth.uid() = user_id);

DROP POLICY IF EXISTS "Users can insert own symptom assessments" ON public.symptom_assessments;
CREATE POLICY "Users can insert own symptom assessments" 
    ON public.symptom_assessments FOR INSERT 
    TO authenticated 
    WITH CHECK (auth.uid() = user_id);

DROP POLICY IF EXISTS "Users can update own symptom assessments" ON public.symptom_assessments;
CREATE POLICY "Users can update own symptom assessments" 
    ON public.symptom_assessments FOR UPDATE 
    TO authenticated 
    USING (auth.uid() = user_id) 
    WITH CHECK (auth.uid() = user_id);

DROP POLICY IF EXISTS "Users can delete own symptom assessments" ON public.symptom_assessments;
CREATE POLICY "Users can delete own symptom assessments" 
    ON public.symptom_assessments FOR DELETE 
    TO authenticated 
    USING (auth.uid() = user_id);

-- ============================================================================
-- 7. POLICIES FOR public.blood_test_results
-- Owner column: user_id (references public.profiles.id)
-- ============================================================================
DROP POLICY IF EXISTS "Users can view own blood test results" ON public.blood_test_results;
CREATE POLICY "Users can view own blood test results" 
    ON public.blood_test_results FOR SELECT 
    TO authenticated 
    USING (auth.uid() = user_id);

DROP POLICY IF EXISTS "Users can insert own blood test results" ON public.blood_test_results;
CREATE POLICY "Users can insert own blood test results" 
    ON public.blood_test_results FOR INSERT 
    TO authenticated 
    WITH CHECK (auth.uid() = user_id);

DROP POLICY IF EXISTS "Users can update own blood test results" ON public.blood_test_results;
CREATE POLICY "Users can update own blood test results" 
    ON public.blood_test_results FOR UPDATE 
    TO authenticated 
    USING (auth.uid() = user_id) 
    WITH CHECK (auth.uid() = user_id);

DROP POLICY IF EXISTS "Users can delete own blood test results" ON public.blood_test_results;
CREATE POLICY "Users can delete own blood test results" 
    ON public.blood_test_results FOR DELETE 
    TO authenticated 
    USING (auth.uid() = user_id);
