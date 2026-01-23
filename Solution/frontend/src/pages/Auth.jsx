import React, { useState } from 'react';
import { Sparkles, Mail, Lock, ArrowRight, Chrome } from 'lucide-react';
import './Auth.css';

const Auth = ({ onLogin }) => {
    const [isLogin, setIsLogin] = useState(true);
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [error, setError] = useState('');
    const [loading, setLoading] = useState(false);

    const handleLogin = async (e) => {
        if (e) e.preventDefault();
        setError('');
        setLoading(true);

        // For the demo, if clicking Google without inputs, we fill it
        const loginEmail = email || 'sanbenito@unthai.dz';
        const loginPassword = password || 'unthai2026';

        try {
            const formData = new URLSearchParams();
            formData.append('username', loginEmail);
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
                setError(data.detail || 'Login failed. Please check your credentials.');
            }
        } catch (err) {
            setError('Could not connect to the server. Make sure the backend is running.');
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="auth-container">
            <div className="auth-visual">
                <div className="visual-overlay"></div>
                <div className="visual-content">
                    <div className="logo-large">
                        <Sparkles size={48} color="#ff6b35" />
                        <h1>Unth<span>AI</span></h1>
                    </div>
                    <p>Unlocking the secrets of your restaurant's reputation through the power of Algerian specialized NLP.</p>
                    <div className="visual-stats">
                        <div className="v-stat">
                            <span>98%</span>
                            <p>Model Accuracy</p>
                        </div>
                        <div className="v-stat">
                            <span>500+</span>
                            <p>Active Restaurants</p>
                        </div>
                    </div>
                </div>
            </div>

            <div className="auth-form-side">
                <div className="auth-form-wrapper">
                    <div className="form-header">
                        <h2>{isLogin ? 'Welcome Back' : 'Create Account'}</h2>
                        <p>{isLogin ? 'Enter your details to access your dashboard.' : 'Start analyzing your restaurant data today.'}</p>
                    </div>

                    <button
                        className="google-btn"
                        onClick={() => handleLogin()}
                        disabled={loading}
                    >
                        <Chrome size={20} />
                        <span>{loading ? 'Connecting...' : 'Continue with Google'}</span>
                    </button>

                    <div className="divider">
                        <span>OR</span>
                    </div>

                    <form className="auth-form" onSubmit={handleLogin}>
                        {error && <div className="error-message">{error}</div>}
                        <div className="input-group">
                            <label>Email Address</label>
                            <div className="input-wrapper">
                                <Mail size={18} />
                                <input
                                    type="email"
                                    placeholder="name@restaurant.com"
                                    value={email}
                                    onChange={(e) => setEmail(e.target.value)}
                                    required
                                />
                            </div>
                        </div>

                        <div className="input-group">
                            <label>Password</label>
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

                        {isLogin && <a href="#" className="forgot-link">Forgot password?</a>}

                        <button type="submit" className="submit-btn" disabled={loading}>
                            {loading ? 'Signing in...' : (isLogin ? 'Sign In' : 'Create Account')}
                            <ArrowRight size={18} />
                        </button>
                    </form>

                    <p className="toggle-auth">
                        {isLogin ? "Don't have an account?" : "Already have an account?"}
                        <button onClick={() => setIsLogin(!isLogin)}>
                            {isLogin ? 'Sign Up' : 'Sign In'}
                        </button>
                    </p>
                </div>
            </div>
        </div>
    );
};

export default Auth;
