import React, { useState, useEffect } from 'react';
import {
    TrendingUp,
    MessageCircle,
    ThumbsUp,
    ThumbsDown,
    Activity,
    ArrowUpRight,
    ArrowDownRight,
    Target,
    AlertTriangle,
    Lightbulb
} from 'lucide-react';
import {
    PieChart, Pie, Cell, ResponsiveContainer, Tooltip, Legend,
    BarChart, Bar, XAxis, YAxis, CartesianGrid
} from 'recharts';
import './Dashboard.css';

const Dashboard = () => {
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
                    // Update input dates if they were empty (initial load)
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
        return <div className="loading-container">Analyzing data...</div>;
    }

    return (
        <div className="dashboard-page animate-fade-in">
            <div className="page-header">
                <div>
                    <h1>Global Reputation Dashboard</h1>
                    <p className="subtitle">Real-time analysis of your restaurant's digital footprint.</p>
                </div>
                <div className="date-picker-container">
                    <div className="date-input-group">
                        <label>Start</label>
                        <input
                            type="date"
                            value={startDate}
                            onChange={(e) => setStartDate(e.target.value)}
                        />
                    </div>
                    <div className="date-input-group">
                        <label>End</label>
                        <input
                            type="date"
                            value={endDate}
                            onChange={(e) => setEndDate(e.target.value)}
                        />
                    </div>
                </div>
            </div>

            <div className="stats-grid">
                {data.kpis.map((stat, idx) => (
                    <div key={idx} className="glass-card stat-card">
                        <div className={`stat-icon ${stat.status}`}>
                            {stat.id === 'total' ? <MessageCircle /> :
                                stat.id === 'health' ? <Activity /> :
                                    stat.id === 'pillar' ? <Target /> :
                                        stat.id === 'complaint' ? <AlertTriangle /> :
                                            <Lightbulb />}
                        </div>
                        <div className="stat-info">
                            <p className="stat-label">{stat.label}</p>
                            <h3 className="stat-value">{stat.value}</h3>
                        </div>
                        <div className={`stat-trend ${stat.status}`}>
                            {stat.status === 'up' ? <ArrowUpRight size={16} /> :
                                stat.status === 'down' ? <ArrowDownRight size={16} /> :
                                    <TrendingUp size={16} />}
                            <span>{stat.trend}</span>
                        </div>
                    </div>
                ))}
            </div>

            <div className="charts-row">
                <div className="glass-card chart-container">
                    <h3>Sentiment Distribution</h3>
                    <div className="chart-wrapper">
                        <ResponsiveContainer width="100%" height={300}>
                            <PieChart>
                                <Pie
                                    data={data.sentiment_distribution}
                                    cx="50%"
                                    cy="50%"
                                    innerRadius={60}
                                    outerRadius={80}
                                    paddingAngle={5}
                                    dataKey="value"
                                >
                                    {data.sentiment_distribution.map((entry, index) => (
                                        <Cell key={`cell-${index}`} fill={entry.color} />
                                    ))}
                                </Pie>
                                <Tooltip
                                    contentStyle={{ backgroundColor: '#1e2230', border: 'none', borderRadius: '8px', color: '#fff' }}
                                    itemStyle={{ color: '#fff' }}
                                />
                                <Legend verticalAlign="bottom" height={36} />
                            </PieChart>
                        </ResponsiveContainer>
                    </div>
                </div>

                <div className="glass-card chart-container main-chart">
                    <h3>Category Sentiments</h3>
                    <div className="chart-wrapper">
                        <ResponsiveContainer width="100%" height={300}>
                            <BarChart data={data.category_data}>
                                <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" />
                                <XAxis dataKey="name" stroke="#94a3b8" />
                                <YAxis stroke="#94a3b8" />
                                <Tooltip
                                    cursor={{ fill: 'rgba(255, 255, 255, 0.05)' }}
                                    contentStyle={{ backgroundColor: '#1e2230', border: 'none', borderRadius: '8px', color: '#fff' }}
                                    itemStyle={{ color: '#fff' }}
                                />
                                <Legend />
                                <Bar dataKey="apprec" name="Appreciation" fill="#10b981" radius={[4, 4, 0, 0]} />
                                <Bar dataKey="compl" name="Complaint" fill="#ef4444" radius={[4, 4, 0, 0]} />
                            </BarChart>
                        </ResponsiveContainer>
                    </div>
                </div>
            </div>

            <div className="insights-preview-row">
                <div className="glass-card insights-card">
                    <div className="insights-header">
                        <h3>Quick Insights</h3>
                        <span className="badge">AI Generated</span>
                    </div>
                    {data.insights ? (
                        <ul className="insights-list">
                            {data.insights.map((insight, idx) => (
                                <li key={idx}>
                                    <div className={`insight-bullet ${insight.status}`}></div>
                                    <p dangerouslySetInnerHTML={{ __html: insight.text }}></p>
                                </li>
                            ))}
                        </ul>
                    ) : (
                        <div className="loading-small">Thinking...</div>
                    )}
                </div>

                <div className="glass-card platforms-card">
                    <h3>Platform Activity</h3>
                    <div className="platform-stats">
                        {data.platform_dist.map((plat, idx) => (
                            <div key={idx} className="platform-item">
                                <div className="platform-name">{plat.name}</div>
                                <div className="platform-bar-bg">
                                    <div
                                        className="platform-bar"
                                        style={{
                                            width: `${(plat.value / Math.max(...data.platform_dist.map(p => p.value), 1)) * 100}%`,
                                            background: plat.name === 'TikTok' ? '#ff0050' : plat.name === 'Instagram' ? '#e1306c' : '#4285f4'
                                        }}
                                    ></div>
                                </div>
                                <div className="platform-value">{plat.value}</div>
                            </div>
                        ))}
                    </div>
                </div>
            </div>
        </div>
    );
};

export default Dashboard;
