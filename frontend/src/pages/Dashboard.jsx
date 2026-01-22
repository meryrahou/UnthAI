import React from 'react';
import {
    TrendingUp,
    MessageCircle,
    ThumbsUp,
    ThumbsDown,
    Activity,
    ArrowUpRight,
    ArrowDownRight
} from 'lucide-react';
import {
    PieChart, Pie, Cell, ResponsiveContainer, Tooltip, Legend,
    BarChart, Bar, XAxis, YAxis, CartesianGrid
} from 'recharts';
import './Dashboard.css';

const Dashboard = () => {
    // Mock Data inspired by the CSV
    const sentimentData = [
        { name: 'Appreciation', value: 450, color: '#10b981' },
        { name: 'Neutral', value: 300, color: '#94a3b8' },
        { name: 'Complaint', value: 250, color: '#ef4444' },
    ];

    const categoryData = [
        { name: 'Food', appreciated: 120, complained: 30 },
        { name: 'Service', appreciated: 80, complained: 90 },
        { name: 'Price', appreciated: 40, complained: 110 },
        { name: 'Place', appreciated: 150, complained: 10 },
        { name: 'Treatment', appreciated: 60, complained: 40 },
        { name: 'Delivery', appreciated: 30, complained: 50 },
    ];

    const stats = [
        { label: 'Total Comments', value: '6,831', icon: <MessageCircle />, trendPath: 'up' },
        { label: 'Avg Sentiment', value: '72%', icon: <Activity />, trendPath: 'up' },
        { label: 'Appreciations', value: '2,415', icon: <ThumbsUp />, trendPath: 'up' },
        { label: 'Complaints', value: '842', icon: <ThumbsDown />, trendPath: 'down' },
    ];

    return (
        <div className="dashboard-page animate-fade-in">
            <div className="page-header">
                <div>
                    <h1>Global Reputation Dashboard</h1>
                    <p className="subtitle">Real-time analysis of your restaurant's digital footprint.</p>
                </div>
                <div className="date-picker-mock">
                    <span>Last 30 Days</span>
                </div>
            </div>

            <div className="stats-grid">
                {stats.map((stat, idx) => (
                    <div key={idx} className="glass-card stat-card">
                        <div className={`stat-icon ${stat.trendPath}`}>
                            {stat.icon}
                        </div>
                        <div className="stat-info">
                            <p className="stat-label">{stat.label}</p>
                            <h3 className="stat-value">{stat.value}</h3>
                        </div>
                        <div className={`stat-trend ${stat.trendPath}`}>
                            {stat.trendPath === 'up' ? <ArrowUpRight size={16} /> : <ArrowDownRight size={16} />}
                            <span>12%</span>
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
                                    data={sentimentData}
                                    cx="50%"
                                    cy="50%"
                                    innerRadius={60}
                                    outerRadius={100}
                                    paddingAngle={5}
                                    dataKey="value"
                                >
                                    {sentimentData.map((entry, index) => (
                                        <Cell key={`cell-${index}`} fill={entry.color} />
                                    ))}
                                </Pie>
                                <Tooltip
                                    contentStyle={{ backgroundColor: '#14161e', border: '1px solid rgba(255,255,255,0.1)', borderRadius: '8px' }}
                                    itemStyle={{ color: '#fff' }}
                                />
                                <Legend verticalAlign="bottom" height={36} />
                            </PieChart>
                        </ResponsiveContainer>
                    </div>
                </div>

                <div className="glass-card chart-container main-chart">
                    <h3>Category Breakdown</h3>
                    <div className="chart-wrapper">
                        <ResponsiveContainer width="100%" height={300}>
                            <BarChart data={categoryData}>
                                <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" />
                                <XAxis dataKey="name" stroke="#94a3b8" />
                                <YAxis stroke="#94a3b8" />
                                <Tooltip
                                    cursor={{ fill: 'rgba(255, 255, 255, 0.05)' }}
                                    contentStyle={{ backgroundColor: '#14161e', border: '1px solid rgba(255,255,255,0.1)', borderRadius: '8px' }}
                                />
                                <Legend />
                                <Bar dataKey="appreciated" fill="#10b981" radius={[4, 4, 0, 0]} name="Appreciation" />
                                <Bar dataKey="complained" fill="#ef4444" radius={[4, 4, 0, 0]} name="Complaint" />
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
                    <ul className="insights-list">
                        <li>
                            <div className="insight-bullet warning"></div>
                            <p>People love the <strong>Food Quality</strong>, but <strong>Waiting Times</strong> are causing dissatisfaction on weekends.</p>
                        </li>
                        <li>
                            <div className="insight-bullet success"></div>
                            <p>Your <strong>Instagram</strong> presence is the strongest, with 45% more positive engagement than TikTok.</p>
                        </li>
                        <li>
                            <div className="insight-bullet info"></div>
                            <p>Price perception is improving after the new combo menu launch.</p>
                        </li>
                    </ul>
                </div>

                <div className="glass-card platforms-card">
                    <h3>Platform Activity</h3>
                    <div className="platform-stats">
                        <div className="platform-item">
                            <div className="platform-name">TikTok</div>
                            <div className="platform-bar-bg"><div className="platform-bar" style={{ width: '85%', background: '#ff0050' }}></div></div>
                            <div className="platform-value">3.2k</div>
                        </div>
                        <div className="platform-item">
                            <div className="platform-name">Instagram</div>
                            <div className="platform-bar-bg"><div className="platform-bar" style={{ width: '65%', background: '#e1306c' }}></div></div>
                            <div className="platform-value">2.1k</div>
                        </div>
                        <div className="platform-item">
                            <div className="platform-name">Google Maps</div>
                            <div className="platform-bar-bg"><div className="platform-bar" style={{ width: '40%', background: '#4285f4' }}></div></div>
                            <div className="platform-value">840</div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default Dashboard;
