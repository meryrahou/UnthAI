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
import './ActionCenter.css';

const ActionCenter = () => {
    const [activeTab, setActiveTab] = useState('complaints');
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

                    // Load completed status from localStorage
                    const completedIds = JSON.parse(localStorage.getItem('completedActions') || '[]');
                    const actionsWithStatus = data.actions.map(a => ({
                        ...a,
                        status: completedIds.includes(a.id) ? 'completed' : 'pending'
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
    }, []);

    const handleMarkComplete = async (actionId) => {
        // Update localStorage
        const completedIds = JSON.parse(localStorage.getItem('completedActions') || '[]');
        completedIds.push(actionId);
        localStorage.setItem('completedActions', JSON.stringify(completedIds));

        // Optimistic update
        setActions(actions.map(a =>
            a.id === actionId ? { ...a, status: 'completed' } : a
        ));
        setStats({
            ...stats,
            completed: stats.completed + 1,
            total: stats.total - 1
        });
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

    if (loading) return <div className="loading-container">Analyzing actionable insights...</div>;

    return (
        <div className="action-center-page animate-fade-in">
            <div className="action-header">
                <div>
                    <h1>
                        <Target size={28} color="#ff6b35" />
                        Action Center
                    </h1>
                    <p style={{ color: 'var(--text-muted)', marginTop: '8px' }}>
                        Turn insights into improvements
                    </p>
                </div>
                <div className="action-stats">
                    <div className="action-stat">
                        <div className="action-stat-value">{stats.total}</div>
                        <div className="action-stat-label">Active Tasks</div>
                    </div>
                    <div className="action-stat">
                        <div className="action-stat-value" style={{ color: '#ef4444' }}>{stats.urgent}</div>
                        <div className="action-stat-label">Urgent</div>
                    </div>
                    <div className="action-stat">
                        <div className="action-stat-value" style={{ color: '#10b981' }}>{stats.completed}</div>
                        <div className="action-stat-label">Completed</div>
                    </div>
                </div>
            </div>

            <div className="action-tabs">
                <button
                    className={`action-tab ${activeTab === 'all' ? 'active' : ''}`}
                    onClick={() => setActiveTab('all')}
                >
                    All Tasks
                </button>
                <button
                    className={`action-tab ${activeTab === 'complaints' ? 'active' : ''}`}
                    onClick={() => setActiveTab('complaints')}
                >
                    Complaint Clusters
                </button>
                <button
                    className={`action-tab ${activeTab === 'inquiries' ? 'active' : ''}`}
                    onClick={() => setActiveTab('inquiries')}
                >
                    Unanswered Inquiries
                </button>
                <button
                    className={`action-tab ${activeTab === 'recommendations' ? 'active' : ''}`}
                    onClick={() => setActiveTab('recommendations')}
                >
                    Quick Wins
                </button>
                <button
                    className={`action-tab ${activeTab === 'trends' ? 'active' : ''}`}
                    onClick={() => setActiveTab('trends')}
                >
                    Trending Issues
                </button>
                <button 
                    className={`action-tab ${activeTab === 'completed' ? 'active' : ''}`}
                    onClick={() => setActiveTab('completed')}
                >
                    Completed
                </button>            </div>

            <div className="action-grid">
                {filteredActions.length === 0 ? (
                    <div className="empty-state">
                        <CheckCircle size={48} />
                        <h3>All caught up!</h3>
                        <p>No pending actions in this category.</p>
                    </div>
                ) : (
                    filteredActions.map(action => (
                        <div key={action.id} className="action-card glass-card">
                            <div className="action-card-header">
                                <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                                    {getIcon(action.type)}
                                </div>
                                <span className={`action-priority ${action.priority}`}>
                                    {action.priority}
                                </span>
                            </div>

                            <h3 className="action-title">{action.title}</h3>
                            <p className="action-description">{action.description}</p>

                            {action.trend && (
                                <div className={`trend-indicator ${action.trend > 0 ? 'up' : 'down'}`}>
                                    {action.trend > 0 ? <TrendingUp size={14} /> : <TrendingDown size={14} />}
                                    {Math.abs(action.trend)}% this week
                                </div>
                            )}

                            <div className="action-meta">
                                <div className="action-meta-item">
                                    <MessageCircle size={14} />
                                    {action.count} mentions
                                </div>
                                <div className="action-meta-item">
                                    <Clock size={14} />
                                    {action.timeframe}
                                </div>
                            </div>

                            {action.platforms && action.platforms.length > 0 && (
                                <div className="action-platforms">
                                    {action.platforms.map((platform, idx) => (
                                        <span key={idx} className="platform-badge">{platform}</span>
                                    ))}
                                </div>
                            )}

                            {action.samples && action.samples.length > 0 && (
                                <div className="action-samples">
                                    {action.samples.slice(0, 2).map((sample, idx) => (
                                        <div key={idx} className="action-sample">
                                            "{sample}"
                                        </div>
                                    ))}
                                </div>
                            )}

                            <div className="action-footer">
                                <button
                                    className="action-btn action-btn-primary"
                                    onClick={() => handleMarkComplete(action.id)}
                                >
                                    <CheckCircle size={16} />
                                    Mark as Addressed
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
