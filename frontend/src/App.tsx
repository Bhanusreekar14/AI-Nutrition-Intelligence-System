import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider } from './context/AuthContext';
import { ProtectedRoute } from './components/ProtectedRoute';
import { LoginPage } from './pages/LoginPage';
import { RegisterPage } from './pages/RegisterPage';
import { HomePage } from './pages/HomePage';
import { HealthProfilePage } from './pages/HealthProfilePage';
import { FoodDiaryPage } from './pages/FoodDiaryPage';
import { SymptomsPage } from './pages/SymptomsPage';
import { BloodTestPage } from './pages/BloodTestPage';
import { PredictionPage } from './pages/PredictionPage';

export const App: React.FC = () => {
  return (
    <AuthProvider>
      <Router>
        <Routes>
          {/* Public Auth Routes */}
          <Route path="/login" element={<LoginPage />} />
          <Route path="/register" element={<RegisterPage />} />

          {/* Protected Application Routes */}
          <Route
            path="/"
            element={
              <ProtectedRoute>
                <HomePage />
              </ProtectedRoute>
            }
          />
          <Route
            path="/profile"
            element={
              <ProtectedRoute>
                <HealthProfilePage />
              </ProtectedRoute>
            }
          />
          <Route
            path="/diary"
            element={
              <ProtectedRoute>
                <FoodDiaryPage />
              </ProtectedRoute>
            }
          />
          <Route
            path="/symptoms"
            element={
              <ProtectedRoute>
                <SymptomsPage />
              </ProtectedRoute>
            }
          />
          <Route
            path="/blood-tests"
            element={
              <ProtectedRoute>
                <BloodTestPage />
              </ProtectedRoute>
            }
          />
          <Route
            path="/predict"
            element={
              <ProtectedRoute>
                <PredictionPage />
              </ProtectedRoute>
            }
          />

          {/* Root Redirect */}
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </Router>
    </AuthProvider>
  );
};

export default App;
