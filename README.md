# AI-Powered Nutrition Intelligence System

A real-world application for health assessment, deficiency risk prediction, personalized diet recommendations, and meal planning.

## Architecture
- **Frontend**: React 18 + Vite + TypeScript + Tailwind CSS
- **Backend**: Python 3.11+ + FastAPI
- **Database & Auth**: Supabase (PostgreSQL with Row Level Security & Supabase Auth)
- **ML**: Scikit-Learn / CatBoost (Predictive Deficiency Models)

## Directory Structure
- `frontend/`: React + Vite + TypeScript Web Application
- `backend/`: FastAPI Python Backend API
- `database/`: Supabase PostgreSQL Migrations and Seed Data
- `ml/`: Machine Learning Training Pipelines & Models

## Setup & Local Development
1. **Database Setup**: Run migrations in `database/migrations/` inside your Supabase project SQL Editor.
2. **Backend**:
   ```bash
   cd backend
   python -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   uvicorn app.main:app --reload --port 8000
   ```
3. **Frontend**:
   ```bash
   cd frontend
   npm install
   npm run dev
   ```
