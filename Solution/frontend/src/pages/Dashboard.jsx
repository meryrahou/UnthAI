import React, { useState, useEffect } from 'react';
import {
    TrendingUp,
    MessageCircle,
    Activity,
    Target,
    AlertTriangle,
    ArrowUpRight,
    ArrowDownRight,
    Zap,
    Calendar
} from 'lucide-react';
import {
    PieChart, Pie, Cell, ResponsiveContainer, Tooltip, Legend,
    BarChart, Bar, XAxis, YAxis, CartesianGrid
} from 'recharts';
import { useApp } from '../utils/AppContext';
import './Dashboard.css';

const Dashboard = () => {
    const { t, theme } = useApp();
    const [startDate, setStartDate] = useState('');
    const [endDate, setEndDate] = useState('');
    const [data, setData] = useState(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const fetchDashboard = async () => {
            setLoading(true);
            try {
                const response = await fetch(`http://localhost:8001/api/dashboard/summary?start_date=${startDate}&end_date=${endDate}`, {
                    headers: {
                        'Authorization': `Bearer ${localStorage.getItem('token')}`
                    }
                });
                if (response.ok) {
                    const result = await response.json();
                    setData(result);
                    if (startDate === '' || endDate === '') {
                        setStartDate(result.startDate);
                        setEndDate(result.endDate);
                    }
                }
            } catch (err) {
                console.error("Dashboard fetch error:", err);
            } finally {
                setLoading(false);
            }
        };

        fetchDashboard();
    }, [startDate, endDate]);

    if (loading || !data) {
        return (
            <div className="loading-container">
                <div className="spinner"></div>
                <p>Analyzing Reputation...</p>
            </div>
        );
    }

    const tooltipStyle = {
        backgroundColor: theme === 'dark' ? '#1a1d26' : '#fff',
        border: 'none',
        borderRadius: '12px',
        boxShadow: '0 10px 30px rgba(0,0,0,0.2)',
        color: theme === 'dark' ? '#fff' : '#1e293b',
        fontSize: '12px'
    };

    const kpiConfig = {
        total: { icon: <MessageCircle size={22} />, status: 'up', label: 'Total Reviews', trend: 'Filtered' },
        health: { icon: <Activity size={22} />, status: 'up', label: 'Brand Health', trend: 'Sentiment' },
        pillar: { icon: <Target size={22} />, status: 'up', label: 'Most Discussed', trend: 'Popular' },
        complaint: { icon: <AlertTriangle size={22} />, status: 'down', label: 'Top Complaint', trend: 'Attention' }
    };

    return (
        <div className="dashboard-page animate-fade-in">
            <div className="page-header">
                <div>
                    <h1>{t('dashboard')}</h1>
                    <p className="subtitle">Real-time analysis of your restaurant's digital footprint.</p>
                </div>
                <div className="date-picker-container">
                    <div className="date-input-group">
                        <label>START</label>
                        <div className="input-with-icon">
                            <input
                                type="date"
                                value={startDate}
                                onChange={(e) => setStartDate(e.target.value)}
                            />
                            <Calendar size={16} className="calendar-icon" />
                        </div>
                    </div>
                    <div className="date-input-group">
                        <label>END</label>
                        <div className="input-with-icon">
                            <input
                                type="date"
                                value={endDate}
                                onChange={(e) => setEndDate(e.target.value)}
                            />
                            <Calendar size={16} className="calendar-icon" />
                        </div>
                    </div>
                </div>
            </div>

            <div className="stats-grid">
                {data.kpis.map((stat, idx) => {
                    const config = kpiConfig[stat.id] || { icon: <Zap />, status: 'up', label: stat.label, trend: 'Updated' };
                    return (
                        <div key={idx} className="glass-card stat-card">
                            <div className={`stat-icon ${stat.id === 'complaint' ? 'down' : stat.id === 'pillar' ? 'info' : 'up'}`}>
                                {config.icon}
                            </div>
                            <div className="stat-info">
                                <p className="stat-label">{config.label}</p>
                                <h3 className="stat-value">{stat.value}</h3>
                            </div>
                            <div className="stat-trend">
                                {config.trend} {stat.id === 'complaint' ? <ArrowDownRight size={14} /> : <ArrowUpRight size={14} />}
                            </div>
                        </div>
                    );
                })}
            </div>

            <div className="charts-row">
                <div className="glass-card chart-container">
                    <h3>{t('sentimentDistribution')}</h3>
                    <div className="chart-wrapper">
                        <ResponsiveContainer width="100%" height={320}>
                            <PieChart>
                                <Pie
                                    data={data.sentiment_distribution}
                                    cx="50%"
                                    cy="50%"
                                    innerRadius={75}
                                    outerRadius={100}
                                    paddingAngle={8}
                                    dataKey="value"
                                    stroke="none"
                                >
                                    {data.sentiment_distribution.map((entry, index) => (
                                        <Cell key={`cell-${index}`} fill={entry.color} />
                                    ))}
                                </Pie>
                                <Tooltip contentStyle={tooltipStyle} />
                                <Legend
                                    verticalAlign="bottom"
                                    height={36}
                                    iconType="circle"
                                    formatter={(value) => {
                                        const label = value === 'Appreciation' ? 'Positive' : value === 'Complaint' ? 'Negative' : value;
                                        return <span style={{ color: 'var(--text-muted)', fontSize: '13px', fontWeight: 500 }}>{label}</span>
                                    }}
                                />
                            </PieChart>
                        </ResponsiveContainer>
                    </div>
                </div>

                <div className="glass-card chart-container main-chart">
                    <h3>{t('categoryPerformance')}</h3>
                    <div className="chart-wrapper">
                        <ResponsiveContainer width="100%" height={320}>
                            <BarChart data={data.category_data} margin={{ top: 20, right: 30, left: 0, bottom: 0 }}>
                                <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" vertical={false} />
                                <XAxis
                                    dataKey="name"
                                    stroke="var(--text-muted)"
                                    fontSize={12}
                                    axisLine={false}
                                    tickLine={false}
                                    tick={{ fill: 'var(--text-muted)' }}
                                />
                                <YAxis
                                    stroke="var(--text-muted)"
                                    fontSize={12}
                                    axisLine={false}
                                    tickLine={false}
                                    tick={{ fill: 'var(--text-muted)' }}
                                />
                                <Tooltip
                                    cursor={{ fill: 'rgba(255, 255, 255, 0.03)' }}
                                    contentStyle={tooltipStyle}
                                />
                                <Legend iconType="rect" verticalAlign="bottom" />
                                <Bar dataKey="apprec" name="Positive" fill="#10b981" radius={[6, 6, 0, 0]} barSize={24} />
                                <Bar dataKey="compl" name="Negative" fill="#ef4444" radius={[6, 6, 0, 0]} barSize={24} />
                            </BarChart>
                        </ResponsiveContainer>
                    </div>
                </div>
            </div>

            <div className="insights-preview-row">
                <div className="glass-card ai-summary-card">
                    <div className="ai-summary-header">
                        <h3>{t('quickInsights')}</h3>
                        <span className="ai-badge-new">AI Generated</span>
                    </div>
                    <div className="ai-content-new">
                        <ul className="ai-facts-new">
                            <li>
                                <span className="dot pos"></span>
                                Found <strong>{data.pos_count || 0} Appreciations</strong> and <strong>{data.recommendation_count || 0} Recommendations</strong>.
                            </li>
                            <li>
                                <span className="dot info"></span>
                                Your most discussed pillar is <strong>{data.kpis.find(k => k.id === 'pillar')?.value || 'N/A'}</strong>.
                            </li>
                            <li>
                                <span className="dot neg"></span>
                                Top Negative source: <strong>{data.kpis.find(k => k.id === 'complaint')?.value || 'N/A'}</strong>.
                            </li>
                        </ul>
                    </div>
                </div>

                <div className="glass-card platforms-card">
                    <h3>{t('platformActivity')}</h3>
                    <div className="platform-stats">
                        {data.platform_dist.map((plat, idx) => {
                            const maxVal = Math.max(...data.platform_dist.map(p => p.value), 1);
                            const color = plat.name === 'TikTok' ? '#ff0050' :
                                plat.name === 'Instagram' ? '#e1306c' :
                                    plat.name === 'Facebook' ? '#1877f2' : '#4285f4';
                            return (
                                <div key={idx} className="platform-item">
                                    <div className="platform-name">{plat.name}</div>
                                    <div className="platform-bar-bg">
                                        <div
                                            className="platform-bar"
                                            style={{
                                                width: `${(plat.value / maxVal) * 100}%`,
                                                background: color,
                                                boxShadow: `0 0 12px ${color}33`
                                            }}
                                        ></div>
                                    </div>
                                    <div className="platform-value">{plat.value}</div>
                                </div>
                            );
                        })}
                    </div>
                </div>
            </div>
        </div>
    );
};

export default Dashboard;
