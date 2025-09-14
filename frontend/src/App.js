import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from 'react-query';
import { Toaster } from 'react-hot-toast';
import { AuthProvider } from './contexts/AuthContext';
import { LanguageProvider } from './contexts/LanguageContext';
import ProtectedRoute from './components/ProtectedRoute';
import Navbar from './components/Navbar';
import Login from './pages/Login';
import Register from './pages/Register';
import Dashboard from './pages/Dashboard';
import SoilAnalysis from './pages/SoilAnalysis';
import Weather from './pages/Weather';
import Market from './pages/Market';
import Recommendations from './pages/Recommendations';
import DiseaseDetection from './pages/DiseaseDetection';
import VoiceAssistant from './pages/VoiceAssistant';
import Profile from './pages/Profile';
import './App.css';

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      retry: 1,
      refetchOnWindowFocus: false,
    },
  },
});

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <LanguageProvider>
        <AuthProvider>
          <Router>
            <div className="App">
              <Navbar />
              <main className="main-content">
                <Routes>
                  <Route path="/login" element={<Login />} />
                  <Route path="/register" element={<Register />} />
                  <Route path="/" element={<Navigate to="/dashboard" replace />} />
                  <Route
                    path="/dashboard"
                    element={
                      <ProtectedRoute>
                        <Dashboard />
                      </ProtectedRoute>
                    }
                  />
                  <Route
                    path="/soil"
                    element={
                      <ProtectedRoute>
                        <SoilAnalysis />
                      </ProtectedRoute>
                    }
                  />
                  <Route
                    path="/weather"
                    element={
                      <ProtectedRoute>
                        <Weather />
                      </ProtectedRoute>
                    }
                  />
                  <Route
                    path="/market"
                    element={
                      <ProtectedRoute>
                        <Market />
                      </ProtectedRoute>
                    }
                  />
                  <Route
                    path="/recommendations"
                    element={
                      <ProtectedRoute>
                        <Recommendations />
                      </ProtectedRoute>
                    }
                  />
                  <Route
                    path="/disease"
                    element={
                      <ProtectedRoute>
                        <DiseaseDetection />
                      </ProtectedRoute>
                    }
                  />
                  <Route
                    path="/voice"
                    element={
                      <ProtectedRoute>
                        <VoiceAssistant />
                      </ProtectedRoute>
                    }
                  />
                  <Route
                    path="/profile"
                    element={
                      <ProtectedRoute>
                        <Profile />
                      </ProtectedRoute>
                    }
                  />
                </Routes>
              </main>
              <Toaster position="top-right" />
            </div>
          </Router>
        </AuthProvider>
      </LanguageProvider>
    </QueryClientProvider>
  );
}

export default App;
