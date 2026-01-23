import React, { useState, useEffect } from 'react';
import { Zap } from 'lucide-react';
import { useApp } from '../utils/AppContext';
import WordCloud from '../components/WordCloud';
import './Trends.css';

const Trends = () => {
    const { t, theme } = useApp();
    const [words, setWords] = useState([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const fetchTrends = async () => {
            try {
                const response = await fetch('http://localhost:8001/api/trends', {
                    headers: { 'Authorization': `Bearer ${localStorage.getItem('token')}` }
                });
                if (response.ok) {
                    const data = await response.json();
                    setWords(data);
                }
            } catch (err) { console.error(err); }
            setLoading(false);
        };
        fetchTrends();
    }, []);

    if (loading) return (
        <div className="loading-container">
            <div className="spinner"></div>
            <p>{t('gatheringTrends')}</p>
        </div>
    );

    return (
        <div className="trends-page animate-fade-in">
            <div className="trends-header">
                <div>
                    <h2><Zap size={24} style={{ color: 'var(--primary)' }} /> {t('trendExplorer')}</h2>
                    <p>{t('trendsSubtitle')}</p>
                </div>
            </div>

            <div className="trends-section cloud-section">
                <div className="topic-cloud-container">
                    {words.length > 0 && <WordCloud words={words.slice(0, 50)} theme={theme} />}
                </div>
            </div>

            <div className="trends-section">
                <h3 className="section-title-with-border">{t('keywordsTitle')}</h3>
                <div className="vibrant-grid">
                    {words.slice(0, 20).map((w, idx) => (
                        <div key={idx} className="vibrant-trend-card">
                            <div className="trend-main">
                                <span className="trend-word">{w.text}</span>
                                <div className="trend-badge">
                                    <span className="count">{w.value}</span>
                                    <span className="label">{t('comments')}</span>
                                </div>
                            </div>
                            <div className="trend-progress-bar">
                                <div
                                    className="progress-fill"
                                    style={{
                                        width: `${Math.min((w.value / words[0].value) * 100, 100)}%`,
                                        background: w.sentiment === 'positive' ? 'var(--success)' :
                                            w.sentiment === 'negative' ? 'var(--error)' : 'var(--primary)'
                                    }}
                                ></div>
                            </div>
                        </div>
                    ))}
                </div>
            </div>
        </div>
    );
};

export default Trends;
