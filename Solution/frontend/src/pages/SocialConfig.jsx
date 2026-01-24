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
    const { t, restaurantName } = useApp();
    const [pref, setPref] = React.useState('time');
    const [data, setData] = React.useState(null);
    const [loading, setLoading] = React.useState(true);

    React.useEffect(() => {
        const fetchData = async () => {
            try {
                const response = await fetch('http://localhost:8001/api/dashboard/summary', {
                    headers: { 'Authorization': `Bearer ${localStorage.getItem('token')}` }
                });
                if (response.ok) {
                    const result = await response.json();
                    setData(result);
                }
            } catch (err) {
                console.error("Config fetch error:", err);
            } finally {
                setLoading(false);
            }
        };
        fetchData();
    }, []);

    const getPlatformStatus = (platName) => {
        if (!data || !data.platform_dist) return 'pending';
        const plat = data.platform_dist.find(p => p.name.toLowerCase().replace(' ', '') === platName.toLowerCase().replace(' ', ''));
        return plat && plat.value > 0 ? 'connected' : 'pending';
    };

    const accounts = [
        { id: 'tiktok', platform: 'TikTok', username: getPlatformStatus('tiktok') === 'connected' ? `@${restaurantName.toLowerCase().replace(/\s+/g, '_')}` : t('connectToIdentify'), status: getPlatformStatus('tiktok'), icon: <Play /> },
        { id: 'instagram', platform: 'Instagram', username: getPlatformStatus('instagram') === 'connected' ? restaurantName.toLowerCase().replace(/\s+/g, '_') : t('connectToIdentify'), status: getPlatformStatus('instagram'), icon: <Instagram /> },
        { id: 'facebook', platform: 'Facebook', username: getPlatformStatus('facebook') === 'connected' ? restaurantName : t('connectToIdentify'), status: getPlatformStatus('facebook'), icon: <Facebook /> },
        { id: 'googlemaps', platform: 'Google Maps', username: getPlatformStatus('googlemaps') === 'connected' ? restaurantName : t('connectToIdentify'), status: getPlatformStatus('googlemaps'), icon: <MapPin /> },
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
                                    {acc.status === 'connected' ? t('connected') || 'Connected' : t('pending') || 'Pending'}
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
