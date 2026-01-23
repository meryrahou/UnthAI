import React from 'react';
import {
    Lightbulb,
    Target,
    AlertCircle,
    CheckCircle2
} from 'lucide-react';
import { useApp } from '../utils/AppContext';
import './AIInsights.css';

const AIInsights = () => {
    const { t } = useApp();

    const recommendations = [
        {
            id: 1,
            type: 'critical',
            category: t('pillers.service'),
            title: 'Optimize Weekend Staffing',
            description: 'Analysis shows a 65% spike in "Service Complaints" specifically regarding "Waiting Time" on Thursday and Friday nights (8 PM - 11 PM).',
            action: 'Consider adding 2 extra floor staff members during these peak windows to reduce wait times by an estimated 20%.',
            impact: 'High'
        },
        {
            id: 2,
            type: 'positive',
            category: t('pillers.food'),
            title: 'Highlight Premium Ingredients',
            description: 'Customers frequently appreciate the freshness of your "Smash Burger" meat, often mentioning it as the reason for returning.',
            action: 'Launch a short video series on TikTok/IG showing your meat preparation process and local sourcing. This aligns with your 85% food appreciation score.',
            impact: 'Medium'
        }
    ];

    return (
        <div className="insights-page animate-fade-in">
            <div className="page-header">
                <div>
                    <h1>{t('aiInsights')}</h1>
                    <p className="subtitle">Data-driven recommendations to grow your restaurant's reputation.</p>
                </div>
            </div>

            <div className="insights-grid">
                <div className="main-recommendations">
                    {recommendations.map((rec) => (
                        <div key={rec.id} className={`glass-card recommendation-card ${rec.type}`}>
                            <div className="rec-header">
                                <div className="rec-type-tag">
                                    {rec.type === 'critical' && <AlertCircle size={16} />}
                                    {rec.type === 'positive' && <CheckCircle2 size={16} />}
                                    {rec.type === 'suggest' && <Lightbulb size={16} />}
                                    <span>{rec.type.toUpperCase()}</span>
                                </div>
                                <span className="rec-category">{rec.category}</span>
                            </div>

                            <h2 className="rec-title">{rec.title}</h2>
                            <p className="rec-description">{rec.description}</p>

                            <div className="rec-action-box">
                                <div className="action-header">
                                    <Target size={16} />
                                    <span>Recommended Action</span>
                                </div>
                                <p>{rec.action}</p>
                            </div>

                            <div className="rec-footer">
                                <div className="rec-impact">
                                    <span className="impact-label">Expected Impact:</span>
                                    <span className={`impact-value ${rec.impact.toLowerCase()}`}>{rec.impact}</span>
                                </div>
                            </div>
                        </div>
                    ))}
                </div>

                <div className="insights-summary">
                    <div className="glass-card summary-card">
                        <h3>Weekly Summary</h3>
                        <div className="summary-item">
                            <span className="summary-val positive">+12%</span>
                            <span className="summary-txt">{t('positive')} Sentiment</span>
                        </div>
                        <div className="summary-item">
                            <span className="summary-val negative">-5%</span>
                            <span className="summary-txt">Response Time</span>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default AIInsights;
