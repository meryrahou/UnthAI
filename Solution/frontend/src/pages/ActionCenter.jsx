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
    Lightbulb,
    MessageSquare
} from 'lucide-react';
import { useApp } from '../utils/AppContext';
import './ActionCenter.css';

const ActionCenter = () => {
    const { t } = useApp();
    const [activeTab, setActiveTab] = useState('all');
    const [actions, setActions] = useState([]);
    const [loading, setLoading] = useState(true);
    const [stats, setStats] = useState({ total: 0, urgent: 0, completed: 0 });

    useEffect(() => {
        const fetchActions = async () => {
            setLoading(true);
            try {
                const response = await fetch('http://localhost:8001/api/actions', {
                    headers: { 'Authorization': `Bearer ${localStorage.getItem('token')}` }
                });
                if (response.ok) {
                    const data = await response.json();
                    const completedIds = JSON.parse(localStorage.getItem('completedActions') || '[]');
                    const actionsWithStatus = data.actions.map(a => ({
                        ...a,
                        status: completedIds.includes(a.id) ? 'completed' : 'pending'
                    }));
                    setActions(actionsWithStatus);
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
    }, []);

    const handleMarkComplete = (actionId) => {
        const completedIds = JSON.parse(localStorage.getItem('completedActions') || '[]');
        completedIds.push(actionId);
        localStorage.setItem('completedActions', JSON.stringify(completedIds));
        setActions(actions.map(a => a.id === actionId ? { ...a, status: 'completed' } : a));
        setStats(prev => ({ ...prev, completed: prev.completed + 1, total: prev.total - 1 }));
    };

    const filteredActions = actions.filter(action => {
        if (activeTab === 'completed') return action.status === 'completed';
        if (activeTab === 'all') return action.status !== 'completed';
        return action.type === activeTab && action.status !== 'completed';
    });

    const getIcon = (type) => {
        switch (type) {
            case 'complaints': return <AlertTriangle size={24} />;
            case 'inquiries': return <HelpCircle size={24} />;
            case 'recommendations': return <Lightbulb size={24} />;
            case 'trends': return <TrendingUp size={24} />;
            default: return <Target size={24} />;
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
            <div className="action-header">
                <div>
                    <h1><Target size={32} color="var(--primary)" /> {t('actionCenter')}</h1>
                    <p className="subtitle">{t('actionCenterSubtitle')}</p>
                </div>
                <div className="action-summary-cards">
                    <div className="summary-card active">
                        <span className="val">{stats.total}</span>
                        <span className="lbl">{t('actionableTasks')}</span>
                    </div>
                    <div className="summary-card urgent">
                        <span className="val">{stats.urgent}</span>
                        <span className="lbl">{t('urgent')}</span>
                    </div>
                    <div className="summary-card completed">
                        <span className="val">{stats.completed}</span>
                        <span className="lbl">{t('completed')}</span>
                    </div>
                </div>
            </div>

            <div className="action-navigation">
                {[
                    { id: 'all', label: t('allTasks') },
                    { id: 'complaints', label: t('complaints') },
                    { id: 'inquiries', label: t('inquiries') },
                    { id: 'recommendations', label: t('quickWins') },
                    { id: 'trends', label: t('trending') },
                    { id: 'completed', label: t('completed') }
                ].map(tab => (
                    <button
                        key={tab.id}
                        className={`nav-tab ${activeTab === tab.id ? 'active' : ''}`}
                        onClick={() => setActiveTab(tab.id)}
                    >
                        {tab.label}
                    </button>
                ))}
            </div>

            <div className="action-vibrant-grid">
                {filteredActions.length === 0 ? (
                    <div className="empty-action-state">
                        <CheckCircle size={64} color="var(--success)" />
                        <h3>{t('perfectlyManaged')}</h3>
                        <p>{t('noPendingActions')}</p>
                    </div>
                ) : (
                    filteredActions.map(action => (
                        <div key={action.id} className={`vibrant-card ${action.priority}`}>
                            <div className="card-top">
                                <div className="icon-box">
                                    {getIcon(action.type)}
                                </div>
                                <div className="priority-tag">{action.priority} {t('priorityLabel')}</div>
                            </div>

                            <div className="card-body">
                                <h3>{action.title}</h3>
                                <p>{action.description}</p>
                            </div>

                            <div className="card-footer">
                                <div className="meta-info">
                                    <span className="mentions"><MessageSquare size={14} /> {action.count} {t('comments')}</span>
                                    <span className="time"><Clock size={14} /> {action.timeframe}</span>
                                </div>
                                {action.status !== 'completed' && (
                                    <button className="resolve-btn" onClick={() => handleMarkComplete(action.id)}>
                                        <CheckCircle size={18} /> {t('resolve')}
                                    </button>
                                )}
                            </div>
                        </div>
                    ))
                )}
            </div>
        </div>
    );
};

export default ActionCenter;
