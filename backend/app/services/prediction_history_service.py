import logging
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta, timezone
from fastapi import HTTPException, status
from app.db.supabase import get_supabase_admin_client
from app.models.prediction import DeficiencyPredictionResponse, DeficiencyPredictionRequest
from app.models.prediction_history import (
    PredictionHistoryEntry,
    PredictionProgressResponse,
    SymptomTrendPoint,
    BiomarkerTrendPoint
)

logger = logging.getLogger(__name__)

class PredictionHistoryService:

    @staticmethod
    def save_prediction_snapshot(
        user_id: str,
        prediction: DeficiencyPredictionResponse,
        req_features: Optional[DeficiencyPredictionRequest] = None
    ) -> Optional[dict]:
        """
        Saves a historical prediction snapshot for an authenticated user to the Supabase database.
        Enforces duplicate protection: at most one snapshot per user per calendar day
        for identical predicted class and risk score.
        Does NOT fall back to in-memory store; logs and returns None on DB persistence failure.
        """
        if not user_id:
            logger.warning("save_prediction_snapshot called without user_id")
            return None

        today_start = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0).isoformat()

        # Extract SHAP explanations
        shap_pos = []
        shap_neg = []
        if prediction.explanation:
            shap_pos = [
                {"feature": f.feature, "shap_value": getattr(f, "shap_value", getattr(f, "contribution", 0.0))}
                for f in prediction.explanation.top_positive_features
            ]
            shap_neg = [
                {"feature": f.feature, "shap_value": getattr(f, "shap_value", getattr(f, "contribution", 0.0))}
                for f in prediction.explanation.top_negative_features
            ]

        payload = {
            "user_id": user_id,
            "predicted_class": prediction.predicted_class,
            "predicted_probability": round(float(prediction.predicted_probability), 4),
            "risk_score": round(float(prediction.risk_score), 2),
            "risk_level": prediction.risk_level,
            "class_probabilities": prediction.class_probabilities,
            "shap_positive_features": shap_pos,
            "shap_negative_features": shap_neg,
            "symptoms_count": req_features.symptoms_count if req_features else 0,
            "serum_hemoglobin_g_dl": req_features.hemoglobin_g_dl if req_features else None,
            "serum_vitamin_d_ng_ml": req_features.serum_vitamin_d_ng_ml if req_features else None,
            "serum_vitamin_b12_pg_ml": req_features.serum_vitamin_b12_pg_ml if req_features else None,
            "serum_folate_ng_ml": req_features.serum_folate_ng_ml if req_features else None,
            "model_version": "v1.0.0",
            "recorded_at": datetime.now(timezone.utc).isoformat()
        }

        try:
            supabase = get_supabase_admin_client()
            res = supabase.table("prediction_history") \
                .select("*") \
                .eq("user_id", user_id) \
                .gte("recorded_at", today_start) \
                .order("recorded_at", desc=True) \
                .execute()

            existing = res.data or []
            if existing:
                latest_today = existing[0]
                same_class = latest_today.get("predicted_class") == prediction.predicted_class
                same_score = abs(float(latest_today.get("risk_score", 0)) - prediction.risk_score) < 0.5
                if same_class and same_score:
                    logger.info("Duplicate snapshot detected for user %s today; skipping insert.", user_id)
                    return latest_today

            insert_res = supabase.table("prediction_history").insert(payload).execute()
            if insert_res.data and len(insert_res.data) > 0:
                logger.info("Successfully persisted prediction snapshot for user %s", user_id)
                return insert_res.data[0]
            else:
                logger.error("Supabase insert returned empty data for user %s snapshot", user_id)
                return None
        except Exception as exc:
            logger.error("Failed to persist prediction history snapshot for user %s: %s", user_id, str(exc))
            return None

    @staticmethod
    def get_prediction_history(user_id: str, weeks: int = 4) -> List[dict]:
        """
        Retrieves historical prediction snapshots for an authenticated user in chronological order.
        Valid weeks parameter: 4, 8, or 12.
        Queries Supabase prediction_history table.
        """
        if weeks not in (4, 8, 12):
            raise ValueError(f"Invalid weeks parameter '{weeks}'. Supported evaluation windows are 4, 8, or 12 weeks.")

        cutoff = datetime.now(timezone.utc) - timedelta(weeks=weeks)
        cutoff_iso = cutoff.isoformat()

        try:
            supabase = get_supabase_admin_client()
            res = supabase.table("prediction_history") \
                .select("*") \
                .eq("user_id", user_id) \
                .gte("recorded_at", cutoff_iso) \
                .order("recorded_at", desc=False) \
                .execute()

            if res.data is not None:
                return res.data
            return []
        except Exception as exc:
            logger.error("Failed to fetch prediction history for user %s: %s", user_id, str(exc))
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Database error while retrieving prediction history: {str(exc)}"
            )

    @staticmethod
    def get_prediction_progress(user_id: str, weeks: int = 4) -> Dict[str, Any]:
        """
        Calculates longitudinal progress summary for an authenticated user over 4, 8, or 12 weeks.
        """
        if weeks not in (4, 8, 12):
            raise ValueError(f"Invalid weeks parameter '{weeks}'. Supported evaluation windows are 4, 8, or 12 weeks.")

        cutoff = datetime.now(timezone.utc) - timedelta(weeks=weeks)
        cutoff_date_str = cutoff.strftime("%Y-%m-%d")

        # 1. Fetch prediction history (raises HTTPException if DB fails)
        history_raw = PredictionHistoryService.get_prediction_history(user_id, weeks=weeks)

        # 2. Fetch real symptoms history
        symptoms_raw = []
        try:
            supabase = get_supabase_admin_client()
            sym_res = supabase.table("symptom_assessments") \
                .select("*") \
                .eq("user_id", user_id) \
                .gte("assessment_date", cutoff_date_str) \
                .order("assessment_date", desc=False) \
                .execute()
            symptoms_raw = sym_res.data or []
        except Exception as exc:
            logger.warning("Could not fetch symptom assessments for user %s progress: %s", user_id, str(exc))

        # 3. Fetch real blood tests history
        blood_raw = []
        try:
            supabase = get_supabase_admin_client()
            blood_res = supabase.table("blood_test_results") \
                .select("*") \
                .eq("user_id", user_id) \
                .gte("test_date", cutoff_date_str) \
                .order("test_date", desc=False) \
                .execute()
            blood_raw = blood_res.data or []
        except Exception as exc:
            logger.warning("Could not fetch blood test results for user %s progress: %s", user_id, str(exc))

        # Parse history items
        history_entries = []
        for item in history_raw:
            history_entries.append(PredictionHistoryEntry(
                id=str(item.get("id", "")),
                user_id=str(item.get("user_id", user_id)),
                predicted_class=str(item.get("predicted_class", "Healthy")),
                predicted_probability=float(item.get("predicted_probability", 0.0)),
                risk_score=float(item.get("risk_score", 0.0)),
                risk_level=str(item.get("risk_level", "Low Risk")),
                class_probabilities=item.get("class_probabilities") or {},
                shap_positive_features=item.get("shap_positive_features") or [],
                shap_negative_features=item.get("shap_negative_features") or [],
                symptoms_count=int(item.get("symptoms_count", 0)),
                serum_hemoglobin_g_dl=item.get("serum_hemoglobin_g_dl"),
                serum_vitamin_d_ng_ml=item.get("serum_vitamin_d_ng_ml"),
                serum_vitamin_b12_pg_ml=item.get("serum_vitamin_b12_pg_ml"),
                serum_iron_ug_dl=item.get("serum_iron_ug_dl"),
                serum_calcium_mg_dl=item.get("serum_calcium_mg_dl"),
                serum_folate_ng_ml=item.get("serum_folate_ng_ml"),
                recorded_at=str(item.get("recorded_at", "")),
                model_version=item.get("model_version", "v1.0.0")
            ))

        total_snapshots = len(history_entries)

        if total_snapshots == 0:
            return PredictionProgressResponse(
                status="insufficient_history",
                message="No historical deficiency-risk snapshots are available yet. Continue using the app and complete periodic health assessments to build your progress history.",
                selected_weeks=weeks,
                total_snapshots=0,
                chronological_history=[],
                class_distribution={},
                symptom_trend=[],
                biomarker_trend=[],
                available_biomarkers=[]
            ).model_dump()

        first_snapshot = history_entries[0]
        latest_snapshot = history_entries[-1]

        first_score = first_snapshot.risk_score
        latest_score = latest_snapshot.risk_score
        score_change = round(latest_score - first_score, 2)

        percentage_change = 0.0
        if first_score > 0:
            percentage_change = round(((latest_score - first_score) / first_score) * 100, 2)

        first_level = first_snapshot.risk_level
        latest_level = latest_snapshot.risk_level
        risk_level_changed = (first_level != latest_level)

        if risk_level_changed:
            transition_text = f"{first_level} → {latest_level}"
        else:
            transition_text = "Risk level has remained unchanged in the available history."

        # Class distribution
        class_dist: Dict[str, int] = {}
        for entry in history_entries:
            cls_name = entry.predicted_class
            class_dist[cls_name] = class_dist.get(cls_name, 0) + 1

        # Symptom trend aggregation
        symptom_date_counts: Dict[str, int] = {}
        for sym in symptoms_raw:
            d_str = sym.get("assessment_date", "")
            if d_str:
                symptom_date_counts[d_str] = symptom_date_counts.get(d_str, 0) + 1

        symptom_trend_list = [
            SymptomTrendPoint(date=d, symptoms_count=c)
            for d, c in sorted(symptom_date_counts.items())
        ]

        # Biomarker trend aggregation from real blood tests
        biomarker_trend_list = []
        found_biomarkers = set()
        for btest in blood_raw:
            d_str = btest.get("test_date", "")
            if not d_str:
                continue

            hb = btest.get("hemoglobin")
            vd = btest.get("vitamin_d")
            vb12 = btest.get("vitamin_b12")
            fe = btest.get("iron")
            ca = btest.get("calcium")
            fol = btest.get("folate") or btest.get("serum_folate")

            if hb is not None: found_biomarkers.add("hemoglobin")
            if vd is not None: found_biomarkers.add("vitamin_d")
            if vb12 is not None: found_biomarkers.add("vitamin_b12")
            if fe is not None: found_biomarkers.add("iron")
            if ca is not None: found_biomarkers.add("calcium")
            if fol is not None: found_biomarkers.add("folate")

            biomarker_trend_list.append(BiomarkerTrendPoint(
                date=d_str,
                hemoglobin=float(hb) if hb is not None else None,
                vitamin_d=float(vd) if vd is not None else None,
                vitamin_b12=float(vb12) if vb12 is not None else None,
                iron=float(fe) if fe is not None else None,
                calcium=float(ca) if ca is not None else None,
                folate=float(fol) if fol is not None else None
            ))

        status_str = "complete" if total_snapshots >= 2 else "insufficient_history"
        msg_str = (
            f"Successfully retrieved {total_snapshots} historical prediction snapshots over the last {weeks} weeks."
            if total_snapshots >= 2 else
            f"Single prediction snapshot recorded. Complete additional periodic health assessments over time to track longitudinal trends."
        )

        resp = PredictionProgressResponse(
            status=status_str,
            message=msg_str,
            selected_weeks=weeks,
            total_snapshots=total_snapshots,
            first_risk_score=first_score,
            latest_risk_score=latest_score,
            risk_score_change=score_change,
            percentage_change=percentage_change,
            first_risk_level=first_level,
            latest_risk_level=latest_level,
            risk_level_changed=risk_level_changed,
            transition_text=transition_text,
            chronological_history=history_entries,
            class_distribution=class_dist,
            symptom_trend=symptom_trend_list,
            biomarker_trend=biomarker_trend_list,
            available_biomarkers=sorted(list(found_biomarkers))
        )
        return resp.model_dump()
