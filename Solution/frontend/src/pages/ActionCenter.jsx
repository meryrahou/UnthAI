import React, { useState, useEffect } from 'react';
import {
    Target,
    TrendingUp,
    TrendingDown,
    MessageCircle,
    Clock,
    CheckCircle,
    AlertTriangle,
    HelpCircle,
    Lightbulb
} from 'lucide-react';
import { useApp } from '../utils/AppContext';
import './ActionCenter.css';

const ActionCenter = () => {
    const { t } = useApp();
    const [activeTab, setActiveTab] = useState('all');
    const [restaurantName, setRestaurantName] = useState('');
    const [actions, setActions] = useState([]);
    const [loading, setLoading] = useState(true);
    const [stats, setStats] = useState({ total: 0, urgent: 0, completed: 0 });
    const [trendPeriod, setTrendPeriod] = useState('monthly');

    useEffect(() => {
        const fetchActions = async () => {
            setLoading(true);
            try {
                const response = await fetch(`http://localhost:8001/api/actions?trend_period=${trendPeriod}`, {
                    headers: { 'Authorization': `Bearer ${localStorage.getItem('token')}` }
                });
                if (response.ok) {
                    const data = await response.json();
                    const name = data.restaurant_name;
                    setRestaurantName(name);

                    // Load completed status from localStorage (scoped by restaurant)
                    const allCompletions = JSON.parse(localStorage.getItem('completedActionsMap') || '{}');
                    const completedIds = allCompletions[name] || [];

                    const actionsWithStatus = data.actions.map(a => ({
                        ...a,
                        status: completedIds.includes(String(a.id)) ? 'completed' : 'pending'
                    }));

                    setActions(actionsWithStatus);

                    // Recalculate stats
                    const completedCount = actionsWithStatus.filter(a => a.status === 'completed').length;
                    setStats({
                        ...data.stats,
                        total: actionsWithStatus.length - completedCount,
                        completed: completedCount
                    });
                }
            } catch (err) { console.error(err); }
            setLoading(false);
        };
        fetchActions();
    }, [trendPeriod]);

    const handleToggleComplete = (actionId) => {
        if (!restaurantName) return;

        const allCompletions = JSON.parse(localStorage.getItem('completedActionsMap') || '{}');
        const completedIds = allCompletions[restaurantName] || [];
        const actionIdStr = String(actionId);
        const isCompleted = completedIds.includes(actionIdStr);

        let newCompletedIds;
        if (isCompleted) {
            newCompletedIds = completedIds.filter(id => id !== actionIdStr);
        } else {
            newCompletedIds = [...completedIds, actionIdStr];
        }

        allCompletions[restaurantName] = newCompletedIds;
        localStorage.setItem('completedActionsMap', JSON.stringify(allCompletions));

        // Optimistic update
        setActions(actions.map(a =>
            a.id === actionId ? { ...a, status: isCompleted ? 'pending' : 'completed' } : a
        ));

        setStats({
            ...stats,
            completed: isCompleted ? stats.completed - 1 : stats.completed + 1,
            total: isCompleted ? stats.total + 1 : stats.total - 1
        });
    };

    const getPlatformColor = (platform) => {
        const p = platform.toLowerCase();
        if (p.includes('tiktok')) return '#ff0050';
        if (p.includes('maps') || p.includes('google')) return '#4285F4';
        if (p.includes('instagram')) return '#E1306C';
        if (p.includes('facebook')) return '#1877F2';
        return 'var(--border)';
    };

    const filteredActions = actions.filter(action => {
        if (activeTab === 'completed') return action.status === 'completed';
        if (activeTab === 'all') return action.status !== 'completed';
        return action.type === activeTab && action.status !== 'completed';
    });

    const getIcon = (type) => {
        switch (type) {
            case 'complaints': return <AlertTriangle size={20} />;
            case 'inquiries': return <HelpCircle size={20} />;
            case 'recommendations': return <Lightbulb size={20} />;
            case 'trends': return <TrendingUp size={20} />;
            default: return <Target size={20} />;
        }
    };

    if (loading) return (
        <div className="loading-container">
            <div className="spinner"></div>
            <p>{t('analyzingData')}</p>
        </div>
    );

    return (
        <div className="action-center-page animate-fade-in">
            <div className="page-header">
                <div>
                    <h1><Target className="header-icon" size={28} /> {t('actionCenter')}</h1>
                    <p className="subtitle">{t('actionCenterSubtitle')}</p>
                </div>
                <div className="action-stats">
                    <div className="action-stat">
                        <div className="action-stat-value">{stats.total}</div>
                        <div className="action-stat-label">{t('actionableTasks')}</div>
                    </div>
                    <div className="action-stat">
                        <div className="action-stat-value" style={{ color: 'var(--error)' }}>{stats.urgent}</div>
                        <div className="action-stat-label">{t('urgent')}</div>
                    </div>
                    <div className="action-stat">
                        <div className="action-stat-value" style={{ color: 'var(--success)' }}>{stats.completed}</div>
                        <div className="action-stat-label">{t('completed')}</div>
                    </div>
                </div>
            </div>

            <div className="action-tabs">
                <button
                    className={`action-tab ${activeTab === 'all' ? 'active' : ''}`}
                    onClick={() => setActiveTab('all')}
                >
                    <Target size={16} />
                    {t('allTasks')}
                </button>
                <button
                    className={`action-tab ${activeTab === 'complaints' ? 'active' : ''}`}
                    onClick={() => setActiveTab('complaints')}
                >
                    <AlertTriangle size={16} />
                    {t('complaintClusters')}
                </button>
                <button
                    className={`action-tab ${activeTab === 'inquiries' ? 'active' : ''}`}
                    onClick={() => setActiveTab('inquiries')}
                >
                    <HelpCircle size={16} />
                    {t('unansweredInquiries')}
                </button>
                <button
                    className={`action-tab ${activeTab === 'recommendations' ? 'active' : ''}`}
                    onClick={() => setActiveTab('recommendations')}
                >
                    <Lightbulb size={16} />
                    {t('quickWins')}
                </button>
                <button
                    className={`action-tab ${activeTab === 'trends' ? 'active' : ''}`}
                    onClick={() => setActiveTab('trends')}
                >
                    <TrendingUp size={16} />
                    {t('trendingIssues')}
                </button>
                <button
                    className={`action-tab ${activeTab === 'completed' ? 'active' : ''}`}
                    onClick={() => setActiveTab('completed')}
                >
                    <CheckCircle size={16} />
                    {t('completed')}
                </button>
            </div>

            {activeTab === 'trends' && (
                <div className="trend-period-selector" style={{ marginBottom: '24px', display: 'flex', justifyContent: 'flex-end', alignItems: 'center', gap: '12px' }}>
                    <span style={{ fontSize: '13px', color: 'var(--text-muted)', fontWeight: 500 }}>{t('trendPeriod') || 'Trend Period'}:</span>
                    <div className="custom-select-wrapper" style={{ position: 'relative' }}>
                        <select
                            value={trendPeriod}
                            onChange={(e) => setTrendPeriod(e.target.value)}
                            style={{
                                padding: '8px 36px 8px 16px',
                                background: 'var(--card-bg)',
                                border: '1px solid var(--border)',
                                borderRadius: '10px',
                                color: 'var(--text-main)',
                                fontSize: '13px',
                                fontWeight: 500,
                                cursor: 'pointer',
                                appearance: 'none',
                                WebkitAppearance: 'none',
                                outline: 'none',
                                boxShadow: '0 2px 4px rgba(0,0,0,0.02)'
                            }}
                        >
                            <option value="weekly">{t('weekly') || 'Weekly'}</option>
                            <option value="monthly">{t('monthly') || 'Monthly'}</option>
                            <option value="quarterly">{t('quarterly') || 'Quarterly'}</option>
                        </select>
                        <TrendingUp size={14} style={{ position: 'absolute', right: '12px', top: '50%', transform: 'translateY(-50%)', color: 'var(--text-muted)', pointerEvents: 'none' }} />
                    </div>
                </div>
            )}

            <div className="action-grid">
                {filteredActions.length === 0 ? (
                    <div className="empty-state">
                        <CheckCircle size={48} style={{ color: 'var(--success)', opacity: 0.5 }} />
                        <h3>{t('allCaughtUp')}</h3>
                        <p>{t('noPendingActions')}</p>
                    </div>
                ) : (
                    filteredActions.map(action => (
                        <div key={action.id} className="action-card glass-card">
                            <div className="action-card-header">
                                <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                                    {getIcon(action.type)}
                                </div>
                                <span className={`action-priority ${action.priority}`}>
                                    {t(action.priority)}
                                </span>
                            </div>

                            <h3 className="action-title">
                                {action.titleKey ? t(action.titleKey, { topic: t(action.topicKey) }) : action.title}
                            </h3>
                            <p className="action-description">
                                {action.descKey ? t(action.descKey, { count: action.count, topic: t(action.topicKey).toLowerCase(), period: t(action.timeframeType) }) : action.description}
                            </p>

                            {action.trend && (
                                <div className={`trend-indicator ${action.trend > 0 ? 'up' : 'down'}`}>
                                    {action.trend > 0 ? <TrendingUp size={14} /> : <TrendingDown size={14} />}
                                    {Math.abs(action.trend)}% {t(action.timeframeType)}
                                </div>
                            )}

                            <div className="action-meta">
                                <div className="action-meta-item">
                                    <MessageCircle size={14} />
                                    {action.count} {t('mentions')}
                                </div>
                                <div className="action-meta-item">
                                    <Clock size={14} />
                                    {action.timeframeType === 'lastDays' ? t('lastDays', { days: action.timeframeDays }) :
                                        action.timeframeType === 'today' ? t('today') :
                                            action.timeframeType === 'thisWeek' ? t('thisWeek') :
                                                action.timeframeType === 'recurring' ? t('recurring') :
                                                    action.timeframe}
                                </div>
                            </div>

                            {action.platforms && action.platforms.length > 0 && (
                                <div className="action-platforms">
                                    {action.platforms.map((platform, idx) => (
                                        <span
                                            key={idx}
                                            className="platform-badge"
                                            style={{ borderColor: getPlatformColor(platform) }}
                                        >
                                            {t(platform.toLowerCase().split(' ').join(''))}
                                        </span>
                                    ))}
                                </div>
                            )}

                            {action.samples && action.samples.length > 0 && (
                                <div className="action-samples">
                                    {action.samples.slice(0, 5).map((sample, idx) => (
                                        <div key={idx} className="action-sample">
                                            "{sample}"
                                        </div>
                                    ))}
                                </div>
                            )}

                            <div className="action-footer">
                                <button
                                    className={`action-btn ${action.status === 'completed' ? 'action-btn-secondary' : 'action-btn-primary'}`}
                                    onClick={() => handleToggleComplete(action.id)}
                                >
                                    <CheckCircle size={16} />
                                    {action.status === 'completed' ? t('unresolve') : t('markAsAddressed')}
                                </button>
                            </div>
                        </div>
                    ))
                )}
            </div>
        </div>
    );
};

export default ActionCenter;
