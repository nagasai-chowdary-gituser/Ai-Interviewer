/**
 * AI Interviewer Pro Max - Main App Component
 * 
 * Sets up routing, auth provider, and global providers.
 * 
 * AUTHENTICATION RULES (per MASTER CONSTRAINTS):
 * - All features locked behind authentication
 * - Login/Signup are the only public routes
 * - After login → Dashboard
 * - After logout → Login
 */

import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';

// Context Providers
import { AuthProvider } from './context/AuthContext';
import { ThemeProvider } from './context/ThemeContext';

// Pages
import Login from './pages/Login';
import Signup from './pages/Signup';
import Dashboard from './pages/Dashboard';
import DomainSelection from './pages/DomainSelection';
import Interview from './pages/Interview';
import LiveInterview from './pages/LiveInterview';
import InterviewReadiness from './pages/InterviewReadiness';
import InterviewReport from './pages/InterviewReport';
import CareerRoadmap from './pages/CareerRoadmap';
import Resumes from './pages/Resumes';
import AnalyticsDashboard from './pages/AnalyticsDashboard';
import UserProfile from './pages/UserProfile';
import AvatarTest from './pages/AvatarTest';

// Components
import ProtectedRoute from './components/ProtectedRoute';


function App() {
    return (
        <ThemeProvider>
            <AuthProvider>
                <BrowserRouter>
                    <Routes>
                        {/* ===========================================
                            PUBLIC ROUTES (No auth required)
                            =========================================== */}
                        <Route path="/login" element={<Login />} />
                        <Route path="/signup" element={<Signup />} />
                        <Route path="/avatar-test" element={<AvatarTest />} />

                        {/* ===========================================
                        PROTECTED ROUTES (Auth required)
                        All features locked behind authentication
                        =========================================== */}

                        {/* Dashboard - Main hub after login */}
                        <Route
                            path="/dashboard"
                            element={
                                <ProtectedRoute>
                                    <Dashboard />
                                </ProtectedRoute>
                            }
                        />

                        {/* Domain Selection - Choose interview field */}
                        <Route
                            path="/select-domain"
                            element={
                                <ProtectedRoute>
                                    <DomainSelection />
                                </ProtectedRoute>
                            }
                        />

                        {/* User Profile */}
                        <Route
                            path="/profile"
                            element={
                                <ProtectedRoute>
                                    <UserProfile />
                                </ProtectedRoute>
                            }
                        />

                        {/* Interview - Mock interview session (legacy) */}
                        <Route
                            path="/interview-old"
                            element={
                                <ProtectedRoute>
                                    <Interview />
                                </ProtectedRoute>
                            }
                        />

                        {/* Live Interview - Active interview session */}
                        <Route
                            path="/interview"
                            element={
                                <ProtectedRoute>
                                    <LiveInterview />
                                </ProtectedRoute>
                            }
                        />
                        <Route
                            path="/interview/:sessionId"
                            element={
                                <ProtectedRoute>
                                    <LiveInterview />
                                </ProtectedRoute>
                            }
                        />

                        {/* Interview Readiness - Plan and prepare */}
                        <Route
                            path="/interview-prep"
                            element={
                                <ProtectedRoute>
                                    <InterviewReadiness />
                                </ProtectedRoute>
                            }
                        />

                        {/* Report - Interview results */}
                        <Route
                            path="/report/:sessionId"
                            element={
                                <ProtectedRoute>
                                    <InterviewReport />
                                </ProtectedRoute>
                            }
                        />

                        {/* Resumes - Resume management */}
                        <Route
                            path="/resumes"
                            element={
                                <ProtectedRoute>
                                    <Resumes />
                                </ProtectedRoute>
                            }
                        />

                        {/* Career Roadmap */}
                        <Route
                            path="/roadmap/:sessionId"
                            element={
                                <ProtectedRoute>
                                    <CareerRoadmap />
                                </ProtectedRoute>
                            }
                        />

                        {/* Analytics Dashboard */}
                        <Route
                            path="/analytics"
                            element={
                                <ProtectedRoute>
                                    <AnalyticsDashboard />
                                </ProtectedRoute>
                            }
                        />

                        {/* ===========================================
                        REDIRECTS
                        =========================================== */}

                        {/* Root → Dashboard (ProtectedRoute will redirect to login if needed) */}
                        <Route path="/" element={<Navigate to="/dashboard" replace />} />

                        {/* Catch-all → Dashboard */}
                        <Route path="*" element={<Navigate to="/dashboard" replace />} />
                    </Routes>
                </BrowserRouter>
            </AuthProvider>
        </ThemeProvider>
    );
}

export default App;

