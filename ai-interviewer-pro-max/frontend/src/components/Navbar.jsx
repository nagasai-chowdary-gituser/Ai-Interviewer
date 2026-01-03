/**
 * Navbar Component - Premium Design
 * 
 * Navigation bar with:
 * - Theme toggle (dark/light mode)
 * - User menu and logout
 * - Glassmorphism effect
 */

import React, { useState } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { authApi, getStoredUser } from '../services/api';
import { useTheme } from '../context/ThemeContext';
import { Sun, Moon, LayoutDashboard, Mic, BarChart2, User, LogOut, FileText, ChevronDown, Sparkles } from 'lucide-react';

function Navbar({ user: propUser, minimal = false }) {
    const navigate = useNavigate();
    const location = useLocation();
    const { isDark, toggleTheme } = useTheme();
    const [menuOpen, setMenuOpen] = useState(false);
    const [loggingOut, setLoggingOut] = useState(false);

    // Get user from props or storage
    const user = propUser || getStoredUser();

    // Check if current route is active
    const isActive = (path) => location.pathname === path;

    /**
     * Handle logout
     */
    const handleLogout = async () => {
        setLoggingOut(true);
        try {
            await authApi.logout();
        } catch (error) {
            console.warn('Logout API error:', error.message);
        } finally {
            navigate('/login', { replace: true });
        }
    };

    const closeMenu = () => setMenuOpen(false);

    const handleNavigate = (path) => {
        closeMenu();
        navigate(path);
    };

    return (
        <nav className="navbar">
            {/* Brand / Logo */}
            <div
                className="navbar-brand"
                onClick={() => navigate('/dashboard')}
                role="button"
                tabIndex={0}
                onKeyPress={(e) => e.key === 'Enter' && navigate('/dashboard')}
            >
                <span className="logo-icon">
                    <Sparkles size={24} className="logo-sparkle" />
                </span>
                <span className="brand-text">AI Interviewer</span>
            </div>

            {/* Full Menu (non-minimal mode) */}
            {!minimal && (
                <div className="navbar-menu">
                    <button
                        className={`nav-link ${isActive('/dashboard') ? 'active' : ''}`}
                        onClick={() => navigate('/dashboard')}
                    >
                        <LayoutDashboard size={18} />
                        <span>Dashboard</span>
                    </button>
                    <button
                        className={`nav-link ${isActive('/interview-prep') || isActive('/select-domain') ? 'active' : ''}`}
                        onClick={() => navigate('/select-domain')}
                    >
                        <Mic size={18} />
                        <span>Interview</span>
                    </button>
                    <button
                        className={`nav-link ${isActive('/analytics') ? 'active' : ''}`}
                        onClick={() => navigate('/analytics')}
                    >
                        <BarChart2 size={18} />
                        <span>Analytics</span>
                    </button>

                    {/* Theme Toggle Button */}
                    <button
                        className="theme-toggle"
                        onClick={toggleTheme}
                        aria-label={isDark ? 'Switch to light mode' : 'Switch to dark mode'}
                        title={isDark ? 'Light Mode' : 'Dark Mode'}
                    >
                        <span className="theme-icon">
                            {isDark ? <Sun size={20} /> : <Moon size={20} />}
                        </span>
                    </button>

                    {/* User Dropdown Menu */}
                    <div className="user-menu">
                        <button
                            className="user-button"
                            onClick={() => setMenuOpen(!menuOpen)}
                            aria-expanded={menuOpen}
                            aria-haspopup="true"
                            aria-label="User menu"
                        >
                            <span className="user-avatar">
                                {user?.name?.charAt(0)?.toUpperCase() || <User size={18} />}
                            </span>
                            <span className="user-name">{user?.name || 'User'}</span>
                            <ChevronDown size={14} className={`chevron ${menuOpen ? 'open' : ''}`} />
                        </button>

                        {menuOpen && (
                            <>
                                {/* Backdrop to close menu when clicking outside */}
                                <div
                                    className="menu-backdrop"
                                    onClick={closeMenu}
                                    aria-hidden="true"
                                />

                                <div className="dropdown-menu" role="menu">
                                    {/* User info header */}
                                    <div className="dropdown-header">
                                        <strong>{user?.name || 'User'}</strong>
                                        <small>{user?.email || ''}</small>
                                    </div>
                                    <hr />

                                    {/* Menu items */}
                                    <button
                                        onClick={() => handleNavigate('/profile')}
                                        role="menuitem"
                                    >
                                        <User size={16} /> My Profile
                                    </button>
                                    <button
                                        onClick={() => handleNavigate('/dashboard')}
                                        role="menuitem"
                                    >
                                        <LayoutDashboard size={16} /> Dashboard
                                    </button>
                                    <button
                                        onClick={() => handleNavigate('/analytics')}
                                        role="menuitem"
                                    >
                                        <BarChart2 size={16} /> Analytics
                                    </button>
                                    <button
                                        onClick={() => handleNavigate('/resumes')}
                                        role="menuitem"
                                    >
                                        <FileText size={16} /> Resumes
                                    </button>
                                    <hr />

                                    {/* Logout */}
                                    <button
                                        onClick={handleLogout}
                                        disabled={loggingOut}
                                        className="logout-button"
                                        role="menuitem"
                                    >
                                        <LogOut size={16} />
                                        {loggingOut ? 'Logging out...' : 'Logout'}
                                    </button>
                                </div>
                            </>
                        )}
                    </div>
                </div>
            )}

            {/* Minimal mode - just exit button */}
            {minimal && (
                <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                    <button
                        className="theme-toggle"
                        onClick={toggleTheme}
                        aria-label={isDark ? 'Switch to light mode' : 'Switch to dark mode'}
                    >
                        {isDark ? <Sun size={18} /> : <Moon size={18} />}
                    </button>
                    <button
                        className="btn btn-secondary btn-sm"
                        onClick={handleLogout}
                        disabled={loggingOut}
                    >
                        {loggingOut ? 'Exiting...' : 'Exit'}
                    </button>
                </div>
            )}
        </nav>
    );
}

export default Navbar;
