/**
 * Login Page - Premium Design
 * 
 * Glassmorphism card with animated background.
 * Handles both login and signup with smooth transitions.
 */

import React, { useState, useEffect } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { authApi, isAuthenticated } from '../services/api';
import { useTheme } from '../context/ThemeContext';
import { Mail, Lock, User, AlertCircle, CheckCircle, Loader2, Sun, Moon, Shield } from 'lucide-react';

function Login() {
    const navigate = useNavigate();
    const location = useLocation();
    const { isDark, toggleTheme } = useTheme();

    // Check if coming from /signup route
    const initialMode = location.state?.mode === 'signup' ? false : true;
    const [isLogin, setIsLogin] = useState(initialMode);

    // Form state
    const [formData, setFormData] = useState({
        name: '',
        email: '',
        password: '',
    });

    // UI state
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState('');
    const [success, setSuccess] = useState('');

    // Redirect if already authenticated
    useEffect(() => {
        if (isAuthenticated()) {
            const from = location.state?.from?.pathname || '/dashboard';
            navigate(from, { replace: true });
        }
    }, [navigate, location]);

    // Handle input changes
    const handleChange = (e) => {
        const { name, value } = e.target;
        setFormData(prev => ({ ...prev, [name]: value }));
        setError('');
        setSuccess('');
    };

    // Validate form
    const validateForm = () => {
        if (!formData.email.trim()) {
            setError('Email is required');
            return false;
        }

        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        if (!emailRegex.test(formData.email)) {
            setError('Please enter a valid email address');
            return false;
        }

        if (!formData.password) {
            setError('Password is required');
            return false;
        }

        if (formData.password.length < 8) {
            setError('Password must be at least 8 characters');
            return false;
        }

        if (!isLogin) {
            if (!formData.name.trim()) {
                setError('Name is required');
                return false;
            }
            if (formData.name.trim().length < 2) {
                setError('Name must be at least 2 characters');
                return false;
            }
            if (!/[a-zA-Z]/.test(formData.password)) {
                setError('Password must contain at least one letter');
                return false;
            }
            if (!/\d/.test(formData.password)) {
                setError('Password must contain at least one number');
                return false;
            }
        }

        return true;
    };

    // Handle form submission
    const handleSubmit = async (e) => {
        e.preventDefault();
        if (!validateForm()) return;

        setLoading(true);
        setError('');
        setSuccess('');

        try {
            if (isLogin) {
                await authApi.login(formData.email, formData.password);
            } else {
                await authApi.signup(formData.name, formData.email, formData.password);
            }
            const from = location.state?.from?.pathname || '/dashboard';
            navigate(from, { replace: true });
        } catch (err) {
            const message = err.message || 'Authentication failed. Please try again.';
            setError(message);
        } finally {
            setLoading(false);
        }
    };

    // Switch between login and signup
    const handleModeSwitch = () => {
        setIsLogin(!isLogin);
        setError('');
        setSuccess('');
        setFormData({ name: '', email: '', password: '' });
    };

    return (
        <div className="login-container">
            {/* Theme Toggle - Top Right */}
            <button
                className="theme-toggle"
                onClick={toggleTheme}
                style={{
                    position: 'absolute',
                    top: '24px',
                    right: '24px',
                    zIndex: 10,
                }}
                aria-label={isDark ? 'Switch to light mode' : 'Switch to dark mode'}
            >
                {isDark ? <Sun size={20} /> : <Moon size={20} />}
            </button>

            <div className="login-card">
                {/* Logo/Title */}
                <div className="login-header">
                    <div className="login-logo">🎯</div>
                    <h1>AI Interviewer</h1>
                    <p>Master your interview skills with AI-powered practice</p>
                </div>

                {/* Toggle Tabs */}
                <div className="login-tabs">
                    <button
                        type="button"
                        className={`tab ${isLogin ? 'active' : ''}`}
                        onClick={() => !isLogin && handleModeSwitch()}
                        disabled={loading}
                    >
                        Sign In
                    </button>
                    <button
                        type="button"
                        className={`tab ${!isLogin ? 'active' : ''}`}
                        onClick={() => isLogin && handleModeSwitch()}
                        disabled={loading}
                    >
                        Sign Up
                    </button>
                </div>

                {/* Error Message */}
                {error && (
                    <div className="error-message" role="alert">
                        <AlertCircle size={16} />
                        <span>{error}</span>
                    </div>
                )}

                {/* Success Message */}
                {success && (
                    <div className="success-message" role="status">
                        <CheckCircle size={16} />
                        <span>{success}</span>
                    </div>
                )}

                {/* Form */}
                <form onSubmit={handleSubmit} className="login-form">
                    {/* Name field (signup only) */}
                    {!isLogin && (
                        <div className="form-group">
                            <label htmlFor="name">
                                <User size={14} style={{ marginRight: '6px', opacity: 0.7 }} />
                                Full Name
                            </label>
                            <input
                                type="text"
                                id="name"
                                name="name"
                                value={formData.name}
                                onChange={handleChange}
                                placeholder="Enter your full name"
                                autoComplete="name"
                                disabled={loading}
                                required={!isLogin}
                            />
                        </div>
                    )}

                    {/* Email field */}
                    <div className="form-group">
                        <label htmlFor="email">
                            <Mail size={14} style={{ marginRight: '6px', opacity: 0.7 }} />
                            Email Address
                        </label>
                        <input
                            type="email"
                            id="email"
                            name="email"
                            value={formData.email}
                            onChange={handleChange}
                            placeholder="you@example.com"
                            autoComplete="email"
                            disabled={loading}
                            required
                        />
                    </div>

                    {/* Password field */}
                    <div className="form-group">
                        <label htmlFor="password">
                            <Lock size={14} style={{ marginRight: '6px', opacity: 0.7 }} />
                            Password
                        </label>
                        <input
                            type="password"
                            id="password"
                            name="password"
                            value={formData.password}
                            onChange={handleChange}
                            placeholder={isLogin ? "Enter your password" : "Create a strong password"}
                            autoComplete={isLogin ? "current-password" : "new-password"}
                            disabled={loading}
                            required
                            minLength={8}
                        />
                        {!isLogin && (
                            <small className="form-hint">
                                Min 8 characters with at least 1 letter and 1 number
                            </small>
                        )}
                    </div>

                    {/* Submit button */}
                    <button
                        type="submit"
                        className="btn btn-primary btn-lg submit-button"
                        disabled={loading}
                    >
                        {loading ? (
                            <>
                                <Loader2 size={18} className="spinner-small" style={{ animation: 'spin 1s linear infinite' }} />
                                <span>{isLogin ? 'Signing in...' : 'Creating account...'}</span>
                            </>
                        ) : (
                            isLogin ? 'Sign In' : 'Create Account'
                        )}
                    </button>
                </form>

                {/* Footer */}
                <p className="login-footer">
                    {isLogin ? "Don't have an account? " : 'Already have an account? '}
                    <button
                        type="button"
                        className="link-button"
                        onClick={handleModeSwitch}
                        disabled={loading}
                    >
                        {isLogin ? 'Sign up free' : 'Sign in'}
                    </button>
                </p>

                {/* Security notice */}
                <div className="login-security">
                    <Shield size={14} />
                    <span>Your data is encrypted and secure</span>
                </div>
            </div>
        </div>
    );
}

export default Login;
