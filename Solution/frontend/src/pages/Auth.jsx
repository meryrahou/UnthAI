import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Sparkles, Mail, Lock, ArrowRight, Chrome, Sun, Moon } from 'lucide-react';
import { useApp } from '../utils/AppContext';
import './Auth.css';

const Auth = ({ onLogin }) => {
    const { theme, toggleTheme, t } = useApp();
    const navigate = useNavigate();
    const [isLogin, setIsLogin] = useState(true);
    const [restaurantName, setRestaurantName] = useState('');
    const [password, setPassword] = useState('');
    const [error, setError] = useState('');
    const [loading, setLoading] = useState(false);

    const handleLogin = async (e) => {
        if (e) e.preventDefault();
        setError('');
        setLoading(true);

        // For the demo, if clicking Google without inputs, we fill it
        const loginName = restaurantName || 'favorite restaurant';
        const loginPassword = password || '1234';

        try {
            const formData = new URLSearchParams();
            formData.append('username', loginName);
            formData.append('password', loginPassword);

            const response = await fetch('http://localhost:8001/token', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded',
                },
                body: formData.toString(),
            });

            if (response.ok) {
                const data = await response.json();
                localStorage.setItem('token', data.access_token);
                onLogin();
            } else {
                const data = await response.json();
                setError(data.detail || t('loginFailed') || 'Login failed. Please check your credentials.');
            }
        } catch (err) {
            setError('Could not connect to the server. Make sure the backend is running.');
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="auth-container">
            <button onClick={toggleTheme} className="theme-toggle-btn">
                {theme === 'dark' ? <Sun size={20} /> : <Moon size={20} />}
            </button>
            <div className="auth-visual">
                <div className="visual-overlay"></div>
                <div className="visual-content">
                    <div className="logo-large">
                        <Sparkles size={48} color="#ff6b35" />
                        <h1>Unth<span>AI</span></h1>
                    </div>
                    <p>{t('authTagline')}</p>
                    <div className="visual-stats">
                        <div className="v-stat">
                            <span>98%</span>
                            <p>{t('modelAccuracy')}</p>
                        </div>
                        <div className="v-stat">
                            <span>500+</span>
                            <p>{t('activeRestaurants')}</p>
                        </div>
                    </div>
                </div>
            </div>

            <div className="auth-form-side">
                <div className="auth-form-wrapper">
                    <div className="form-header">
                        <h2>{isLogin ? t('welcomeBack') : t('createAccount')}</h2>
                        <p>{isLogin ? t('loginDetails') : t('startAnalyzing')}</p>
                    </div>

                    <button
                        className="google-btn"
                        onClick={() => handleLogin()}
                        disabled={loading}
                    >
                        <Chrome size={20} />
                        <span>{loading ? t('connecting') : t('continueWithGoogle')}</span>
                    </button>

                    <div className="divider">
                        <span>{t('or')}</span>
                    </div>

                    <form className="auth-form" onSubmit={handleLogin}>
                        {error && <div className="error-message">{error}</div>}
                        <div className="input-group">
                            <label>{t('restaurantNameLabel')}</label>
                            <div className="input-wrapper">
                                <Mail size={18} />
                                <input
                                    type="text"
                                    placeholder="e.g. Restaurant San Benito"
                                    value={restaurantName}
                                    onChange={(e) => setRestaurantName(e.target.value)}
                                    required
                                />
                            </div>
                        </div>

                        <div className="input-group">
                            <label>{t('passwordLabel')}</label>
                            <div className="input-wrapper">
                                <Lock size={18} />
                                <input
                                    type="password"
                                    placeholder="••••••••"
                                    value={password}
                                    onChange={(e) => setPassword(e.target.value)}
                                    required
                                />
                            </div>
                        </div>

                        {isLogin && <a href="#" className="forgot-link">{t('forgotPassword')}</a>}

                        <button type="submit" className="submit-btn" disabled={loading}>
                            {loading ? t('signingIn') : (isLogin ? t('signIn') : t('createAccount'))}
                            <ArrowRight size={18} />
                        </button>
                    </form>

                    <p className="toggle-auth">
                        {isLogin ? t('dontHaveAccount') : t('alreadyHaveAccount')}
                        <button onClick={() => setIsLogin(!isLogin)} type="button">
                            {isLogin ? t('signUp') : t('signIn')}
                        </button>
                    </p>
                </div>
            </div>
        </div>
    );
};

export default Auth;
