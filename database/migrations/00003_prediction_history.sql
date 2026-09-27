-- Migration: 00003_prediction_history.sql
-- Description: Create prediction_history table for longitudinal deficiency risk tracking with RLS.

CREATE TABLE IF NOT EXISTS public.prediction_history (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES public.profiles(id) ON DELETE CASCADE,
    predicted_class TEXT NOT NULL,
    predicted_probability NUMERIC(5,4) NOT NULL CHECK (predicted_probability >= 0.0 AND predicted_probability <= 1.0),
    risk_score NUMERIC(5,2) NOT NULL CHECK (risk_score >= 0.0 AND risk_score <= 100.0),
    risk_level TEXT NOT NULL,
    class_probabilities JSONB DEFAULT '{}'::jsonb,
    shap_positive_features JSONB DEFAULT '[]'::jsonb,
    shap_negative_features JSONB DEFAULT '[]'::jsonb,
    symptoms_count INT DEFAULT 0 CHECK (symptoms_count >= 0),
    serum_hemoglobin_g_dl NUMERIC(5,2),
    serum_vitamin_d_ng_ml NUMERIC(6,2),
    serum_vitamin_b12_pg_ml NUMERIC(7,2),
    serum_iron_ug_dl NUMERIC(6,2),
    serum_calcium_mg_dl NUMERIC(6,2),
    serum_folate_ng_ml NUMERIC(6,2),
    recorded_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    model_version TEXT DEFAULT 'v1.0.0',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Index for user prediction history queries over time
CREATE INDEX IF NOT EXISTS idx_prediction_history_user_recorded ON public.prediction_history(user_id, recorded_at);

-- Enable Row Level Security (RLS)
ALTER TABLE public.prediction_history ENABLE ROW LEVEL SECURITY;

-- Revoke all access from anonymous users
REVOKE ALL ON TABLE public.prediction_history FROM anon, public;

-- Grant privileges to authenticated and service_role
GRANT SELECT, INSERT, UPDATE, DELETE ON TABLE public.prediction_history TO authenticated;
GRANT ALL ON TABLE public.prediction_history TO service_role;

-- Row Level Security Policies
DROP POLICY IF EXISTS "Users can view own prediction history" ON public.prediction_history;
CREATE POLICY "Users can view own prediction history"
    ON public.prediction_history FOR SELECT
    TO authenticated
    USING (auth.uid() = user_id);

DROP POLICY IF EXISTS "Users can insert own prediction history" ON public.prediction_history;
CREATE POLICY "Users can insert own prediction history"
    ON public.prediction_history FOR INSERT
    TO authenticated
    WITH CHECK (auth.uid() = user_id);

DROP POLICY IF EXISTS "Users can update own prediction history" ON public.prediction_history;
CREATE POLICY "Users can update own prediction history"
    ON public.prediction_history FOR UPDATE
    TO authenticated
    USING (auth.uid() = user_id)
    WITH CHECK (auth.uid() = user_id);

DROP POLICY IF EXISTS "Users can delete own prediction history" ON public.prediction_history;
CREATE POLICY "Users can delete own prediction history"
    ON public.prediction_history FOR DELETE
    TO authenticated
    USING (auth.uid() = user_id);
