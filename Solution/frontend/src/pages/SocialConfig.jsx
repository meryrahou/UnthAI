import React from 'react';
import {
    Plus,
    Instagram,
    Facebook,
    Play,
    MapPin,
    CheckCircle2,
    RefreshCcw,
    Clock,
    List
} from 'lucide-react';
import './SocialConfig.css';

const SocialConfig = () => {
    const [pref, setPref] = React.useState('time');
    const accounts = [
        { platform: 'TikTok', username: '@uncles_burger_dz', status: 'connected', icon: <Play /> },
        { platform: 'Instagram', username: 'uncles_burger_dz', status: 'connected', icon: <Instagram /> },
        { platform: 'Facebook', username: 'Uncles Burger DZ', status: 'pending', icon: <Facebook /> },
        { platform: 'Google Maps', username: 'Uncles Burger Algiers', status: 'connected', icon: <MapPin /> },
    ];

    return (
        <div className="config-page animate-fade-in">
            <div className="page-header">
                <h1>Source Configuration</h1>
                <p className="subtitle">Connect and manage your restaurant's social media platforms.</p>
            </div>

            <div className="config-grid">
                <div className="glass-card connections-card">
                    <div className="card-header">
                        <h3>Active Connections</h3>
                        <button className="add-btn" onClick={() => alert("Connecting new account...")}><Plus size={18} /> Connect New</button>
                    </div>
                    <div className="accounts-list">
                        {accounts.map((acc, idx) => (
                            <div key={idx} className="account-item">
                                <div className={`platform-icon ${acc.platform.toLowerCase().replace(' ', '-')}`}>
                                    {acc.icon}
                                </div>
                                <div className="account-info">
                                    <p className="acc-platform">{acc.platform}</p>
                                    <p className="acc-username">{acc.username}</p>
                                </div>
                                <div className={`status-badge ${acc.status}`}>
                                    {acc.status === 'connected' ? <CheckCircle2 size={14} /> : <RefreshCcw size={14} className="spin" />}
                                    {acc.status}
                                </div>
                            </div>
                        ))}
                    </div>
                </div>

                <div className="glass-card analysis-prefs">
                    <h3>Collection Preferences</h3>
                    <p className="section-desc">Choose how the AI should gather data from your accounts.</p>

                    <div className="pref-options">
                        <div
                            className={`pref-option ${pref === 'time' ? 'active' : ''}`}
                            onClick={() => setPref('time')}
                        >
                            <div className="pref-icon"><Clock /></div>
                            <div className="pref-text">
                                <h4>Time Period Analysis</h4>
                                <p>Analyze all comments within a specific timeframe (e.g., last 3 months).</p>
                                <span className="rec-badge">Recommended</span>
                            </div>
                        </div>

                        <div
                            className={`pref-option ${pref === 'posts' ? 'active' : ''}`}
                            onClick={() => setPref('posts')}
                        >
                            <div className="pref-icon"><List /></div>
                            <div className="pref-text">
                                <h4>Recent Posts Analysis</h4>
                                <p>Analyze the 10-50 most recent uploads regardless of date.</p>
                            </div>
                        </div>
                    </div>

                    <div className="justification-box">
                        <h4>Why {pref === 'time' ? 'Time Period' : 'Recent Posts'}?</h4>
                        <p>
                            {pref === 'time'
                                ? "Choosing a time period allows the platform to generate Temporal Trend Evolution. It enables the AI to detect if sentiment is improving month-over-month."
                                : "Recent posts analysis is perfect for quick sanity checks after a specific marketing drop or event to see immediate reception."}
                        </p>
                    </div>

                    <button className="primary-btn full-width" onClick={() => alert('Preferences Saved!')}>
                        Save Preferences
                    </button>
                </div>
            </div>
        </div>
    );
};

export default SocialConfig;
