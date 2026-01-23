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
import { useApp } from '../utils/AppContext';
import './SocialConfig.css';

const SocialConfig = () => {
    const { t } = useApp();
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
                <h1>{t('sourceConfiguration')}</h1>
                <p className="subtitle">{t('configSubtitle')}</p>
            </div>

            <div className="config-grid">
                <div className="glass-card connections-card">
                    <div className="card-header">
                        <h3>{t('activeConnections')}</h3>
                        <button className="add-btn" onClick={() => alert("Connecting new account...")}><Plus size={18} /> {t('connectNew')}</button>
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
                    <h3>{t('collectionPreferences')}</h3>
                    <p className="section-desc">{t('collectionDesc')}</p>

                    <div className="pref-options">
                        <div
                            className={`pref-option ${pref === 'time' ? 'active' : ''}`}
                            onClick={() => setPref('time')}
                        >
                            <div className="pref-icon"><Clock /></div>
                            <div className="pref-text">
                                <h4>{t('timePeriodAnalysis')}</h4>
                                <p>{t('timePeriodDesc')}</p>
                                <span className="rec-badge">{t('recommended')}</span>
                            </div>
                        </div>

                        <div
                            className={`pref-option ${pref === 'posts' ? 'active' : ''}`}
                            onClick={() => setPref('posts')}
                        >
                            <div className="pref-icon"><List /></div>
                            <div className="pref-text">
                                <h4>{t('recentPostsAnalysis')}</h4>
                                <p>{t('recentPostsDesc')}</p>
                            </div>
                        </div>
                    </div>

                    <div className="justification-box">
                        <h4>{pref === 'time' ? t('whyTimePeriod') : t('whyRecentPosts')}?</h4>
                        <p>
                            {pref === 'time'
                                ? t('timePeriodReason')
                                : t('recentPostsReason')}
                        </p>
                    </div>

                    <button className="primary-btn full-width" onClick={() => alert('Preferences Saved!')}>
                        {t('savePreferences')}
                    </button>
                </div>
            </div>
        </div>
    );
};

export default SocialConfig;
