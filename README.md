# AI-Powered Nutrition Intelligence System for Health Assessment & Personalized Diet Recommendation

[![FastAPI](https://img.shields.io/badge/FastAPI-0.110.0-009688.svg?logo=fastapi)](https://fastapi.tiangolo.com)
[![React](https://img.shields.io/badge/React-18.3.1-61DAFB.svg?logo=react)](https://react.dev)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.2.2-3178C6.svg?logo=typescript)](https://www.typescriptlang.org)
[![Vite](https://img.shields.io/badge/Vite-5.2.0-646CFF.svg?logo=vite)](https://vitejs.dev)
[![Python](https://img.shields.io/badge/Python-3.11+-3776AB.svg?logo=python)](https://www.python.org)
[![Supabase](https://img.shields.io/badge/Supabase-PostgreSQL-3ECF8E.svg?logo=supabase)](https://supabase.com)
[![Scikit-Learn](https://img.shields.io/badge/Scikit--Learn-1.4.0-F7931E.svg?logo=scikit-learn)](https://scikit-learn.org)
[![XGBoost](https://img.shields.io/badge/XGBoost-2.0.3-228B22.svg)](https://xgboost.readthedocs.io)

An end-to-end, full-stack intelligence platform that predicts nutritional deficiency risks, aggregates macro- and micronutrient intake from daily food logs, evaluates biomarker & symptom patterns, and delivers personalized 7-day meal plans with allergen-safe substitutions.

---

## 🌟 Key Features

1. **AI Nutritional Deficiency Risk Prediction**:
   - Multi-class classification models (**XGBoost** & **Random Forest** baselines).
   - Pre-trained preprocessor pipelines and serialized model artifacts (`.joblib`).
   - **SHAP (SHapley Additive exPlanations)** feature attribution and patient risk breakdown.
   - Fallback heuristic scoring to ensure 100% API uptime.

2. **Personalized Diet Recommendation & 7-Day Meal Planner**:
   - Automated nutrient-gap-to-food mapping addressing specific micronutrient deficiencies.
   - Intelligent 7-day plan generator respecting daily calorie and macronutrient targets.
   - Dynamic meal replacement engine with real-time allergen & dietary intolerance filtering.

3. **Longitudinal Progress Tracking & Dashboard**:
   - Time-series tracking of nutritional deficiency risk trajectories over time.
   - Visual macronutrient & calorie summaries, daily adherence analytics, and interactive charts.

4. **Food Diary & USDA Nutrition Database**:
   - Direct search across comprehensive USDA and curated food composition datasets (40,000+ foods).
   - Real-time aggregation of daily calorie, protein, fat, carbohydrate, vitamin, and mineral intake.

5. **Symptom Assessment & Blood Biomarker Log**:
   - Structured multi-symptom severity assessment (fatigue, brittle nails, muscle cramps, hair loss, etc.).
   - Serum biomarker tracking (Vitamin D, B12, Ferritin/Iron, Calcium, Folate, etc.).

6. **Authentication & Resilient Architecture**:
   - Dual authentication support via **Supabase Auth** (email/password & Google OAuth) + dev mock JWT tokens.
   - Built-in **resilient in-memory database fallback** allowing full local operation and testing without requiring live Supabase credentials.

---

## 🏗️ Architecture & Technology Stack

```
┌────────────────────────────────────────────────────────────────────────┐
│                        React 18 + Vite Frontend                        │
│     (TypeScript, Tailwind CSS, Lucide Icons, Chart.js, Axios, Router)  │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │ REST API / JWT
┌───────────────────────────────────▼────────────────────────────────────┐
│                        FastAPI Python Backend                          │
│     (Python 3.11+, Pydantic v2, Uvicorn, Resilient Query Builder)      │
├───────────────────┬────────────────────────────────┬───────────────────┤
│    ML Pipeline    │      Recommendation Engine     │    Auth & Data    │
│  - XGBoost        │  - Deficiency Mapping          │  - Supabase Auth  │
│  - Random Forest  │  - 7-Day Meal Generator        │  - PostgreSQL RLS │
│  - SHAP Explain   │  - Allergen Filter & Swaps     │  - In-Memory DB   │
└───────────────────┴────────────────────────────────┴───────────────────┘
```

- **Frontend**: React 18, Vite, TypeScript, Tailwind CSS, Lucide React, Axios
- **Backend**: FastAPI, Pydantic v2, Uvicorn, Python 3.11+
- **Machine Learning**: Scikit-Learn, XGBoost, SHAP, Joblib, NumPy, Pandas
- **Database & Auth**: Supabase (PostgreSQL with Row Level Security)
- **Testing**: Pytest, FastAPI TestClient, Postman Collections

---

## 📁 Project Directory Structure

```
.
├── backend/
│   ├── app/
│   │   ├── api/v1/          # REST API endpoints (predict, meal plans, diary, profile, etc.)
│   │   ├── core/            # App configuration (pydantic-settings) & security middleware
│   │   ├── db/              # Supabase client & resilient in-memory database fallback
│   │   ├── models/          # Pydantic domain models & schemas
│   │   ├── services/        # ML prediction, recommendation, meal planning & recipe services
│   │   └── main.py          # FastAPI application entrypoint
│   ├── ml/
│   │   ├── artifacts/       # Pre-trained models, preprocessors & SHAP metadata (.joblib)
│   │   ├── notebooks/       # EDA, model training & comparison Jupyter notebooks
│   │   ├── reports/         # Performance benchmarks, Day 13-21 logs, Postman collections
│   │   └── scripts/         # Dataset cleaning and validation scripts
│   ├── tests/               # Pytest unit, e2e integration, security & load test suites
│   ├── requirements.txt     # Python dependencies
│   └── run_server.py        # Development server launcher
├── frontend/
│   ├── src/
│   │   ├── components/      # UI components, ProtectedRoute, ErrorBoundary, Dashboard widgets
│   │   ├── context/         # AuthContext (Supabase + Google OAuth + Mock dev auth)
│   │   ├── pages/           # Dashboard, Prediction, Food Diary, Profile, Blood Test, Recipes
│   │   ├── services/        # Axios API client & Supabase browser client
│   │   ├── types/           # TypeScript data contracts & interfaces
│   │   ├── App.tsx          # Root routing and application layout
│   │   └── main.tsx         # React DOM mount point
│   ├── package.json         # Node.js dependencies & scripts
│   ├── tsconfig.json        # TypeScript configuration
│   └── vite.config.ts       # Vite bundler configuration
├── database/
│   ├── migrations/          # SQL migration files (tables, indexes, foreign keys)
│   └── seed.sql             # Reference seed data
├── datasets/
│   ├── deficiency/          # Cleaned & preprocessed ML deficiency training data
│   ├── food_nutrition/      # 40,000-row USDA food composition database
│   ├── allergens/           # Food allergen lookup dataset
│   ├── optional/            # NutriScore, EcoScore & healthy food references
│   └── archive/             # Historical datasets
├── supabase/
│   └── migrations/          # Supabase Row Level Security (RLS) policies
├── .env.example             # Project-wide environment template
├── backend/.env.example     # Backend environment template
├── frontend/.env.example    # Frontend environment template
├── .gitignore               # Excludes secrets, caches, node_modules, and virtualenvs
└── README.md
```

---

## 🚀 Quick Start & Local Setup

### Prerequisites
- **Python**: 3.11 or higher
- **Node.js**: 18.x or 20.x LTS
- **npm** or **yarn**

### 1. Clone the Repository
```bash
git clone https://github.com/Bhanusreekar14/AI-Nutrition-Intelligence-System.git
cd AI-Nutrition-Intelligence-System
```

### 2. Configure Environment Variables
Copy the provided `.env.example` templates:

```bash
# Backend environment configuration
cp backend/.env.example backend/.env

# Frontend environment configuration
cp frontend/.env.example frontend/.env
```

*(Note: The system includes a resilient local database fallback, meaning the backend will automatically run in local mode even without live Supabase credentials).*

### 3. Backend Setup
```bash
cd backend

# Create and activate a virtual environment
python3 -m venv venv
source venv/bin/activate       # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run the FastAPI server
python run_server.py
# or: uvicorn app.main:app --reload --port 8000
```
- API Documentation: [http://localhost:8000/docs](http://localhost:8000/docs) (Swagger UI)
- API Health Check: [http://localhost:8000/api/v1/health](http://localhost:8000/api/v1/health)

### 4. Frontend Setup
In a new terminal window:
```bash
cd frontend

# Install dependencies
npm install

# Start the Vite development server
npm run dev
```
- Web Application: [http://localhost:5173](http://localhost:5173)

---

## 🧪 Testing & Verification

The backend contains automated test suites covering unit tests, end-to-end integration, performance load checks, and security audits:

```bash
cd backend
source venv/bin/activate

# Run all test suites
pytest

# Run specific integration and API test suites
pytest tests/test_prediction_api.py
pytest tests/test_recommendation_api.py
pytest tests/test_meal_plans_api.py
pytest tests/test_e2e_pipeline_integration.py
pytest tests/test_security_and_auth_audit.py
pytest tests/test_load_and_performance.py
```

---

## 📡 API Endpoints Overview

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/api/v1/health` | Service health status and database connectivity |
| `POST` | `/api/v1/predict` | AI nutritional deficiency risk prediction (XGBoost/RF) |
| `GET` | `/api/v1/predict/history` | Historical deficiency risk assessments |
| `POST` | `/api/v1/recommendations` | Personalized nutrient-targeted food recommendations |
| `POST` | `/api/v1/meal-plans/generate` | Generates a 7-day personalized meal plan |
| `POST` | `/api/v1/meal-plans/replace` | Swaps meals with allergen-safe alternatives |
| `GET` | `/api/v1/recipes` | Recipe search and dietary constraint filtering |
| `GET` | `/api/v1/foods/search` | Search foods across the 40,000+ USDA composition dataset |
| `GET` | `/api/v1/diary` | Retrieve daily food logs and nutrient summaries |
| `POST` | `/api/v1/diary` | Log new food entries with automatic macro calculation |
| `GET` | `/api/v1/profile/me` | Fetch authenticated user health profile |
| `POST` | `/api/v1/profile` | Create or update user health profile |
| `POST` | `/api/v1/symptoms` | Submit symptom severity assessment |
| `POST` | `/api/v1/blood-tests` | Log serum biomarker and lab test results |

---

## 📊 Machine Learning Pipeline

1. **Preprocessing & Artifacts**:
   - Feature engineering on RDA percentages, demographic data, and symptom indicators.
   - Cleaned datasets stored under `datasets/deficiency/`.
   - Pipeline artifacts stored in `backend/ml/artifacts/`.
2. **Notebooks**:
   - `02_deficiency_preprocessing_explained.ipynb`: Comprehensive data cleaning rationale.
   - `03_random_forest_baseline.ipynb`: Baseline Random Forest model training.
   - `04_model_comparison.ipynb`: Cross-model evaluation (Random Forest vs. XGBoost).
   - `05_shap_risk_score.ipynb`: SHAP feature contribution and personalized risk scoring.

---

## 🔒 Security & Data Privacy

- **Row Level Security (RLS)**: Enforced on all Supabase tables ensuring users can only read and mutate their own data.
- **Credential Protection**: Strict `.gitignore` rules prevent accidental commits of `.env` files, API keys, and certificates.
- **Dependency Isolation**: Isolated Python virtual environments and pinned `requirements.txt` / `package-lock.json`.

---

## 👤 Author & Acknowledgments

- **Repository**: [https://github.com/Bhanusreekar14/AI-Nutrition-Intelligence-System](https://github.com/Bhanusreekar14/AI-Nutrition-Intelligence-System)
- Developed as part of the AI-Powered Nutrition Intelligence System Project.
