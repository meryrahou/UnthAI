import React, { useState } from 'react';
import { 
    Send, 
    Sparkles, 
    CheckCircle2, 
    AlertCircle, 
    Brain, 
    MessageSquare,
    Zap,
    Tag,
    ShieldCheck
} from 'lucide-react';
import { useApp } from '../utils/AppContext';
import './Lab.css';

const Lab = () => {
    const { t } = useApp();
    const [comment, setComment] = useState('');
    const [loading, setLoading] = useState(false);
    const [result, setResult] = useState(null);
    const [error, setError] = useState(null);

    const handlePredict = async (e) => {
        e.preventDefault();
        if (!comment.trim()) return;

        setLoading(true);
        setError(null);
        setResult(null);

        try {
            const token = localStorage.getItem('token');
            const response = await fetch('http://localhost:8001/api/lab/predict', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${token}`
                },
                body: JSON.stringify({ comment })
            });

            if (!response.ok) throw new Error("Failed to run AI prediction");

            const data = await response.json();
            setResult(data);
        } catch (err) {
            console.error(err);
            setError(err.message);
        } finally {
            setLoading(false);
        }
    };

    const getSentimentColor = (feeling) => {
        switch (feeling?.toLowerCase()) {
            case 'positive': return '#10b981';
            case 'negative': return '#ef4444';
            default: return 'var(--text-secondary)';
        }
    };

    const getPillarIcon = (pillar) => {
        switch (pillar?.toLowerCase()) {
            case 'food': return <Zap size={14} />;
            case 'service': return <ShieldCheck size={14} />;
            case 'price': return <Tag size={14} />;
            default: return <Tag size={14} />;
        }
    };

    return (
        <div className="lab-page animate-fade-in">
            <div className="lab-header">
                <div className="header-info">
                    <h1>AI Prediction Lab</h1>
                    <p>Experience the power of multi-intent labeling. Input any customer feedback to see how our model decomposes complex sentiments.</p>
                </div>
                <div className="header-icon">
                    <Brain size={48} />
                </div>
            </div>

            <div className="lab-content">
                <div className="input-section glass-card">
                    <h3><MessageSquare size={18} /> Customer Feedback</h3>
                    <form onSubmit={handlePredict}>
                        <textarea
                            placeholder="Example: The burger was amazing but the delivery took forever and was cold..."
                            value={comment}
                            onChange={(e) => setComment(e.target.value)}
                            disabled={loading}
                        />
                        <button type="submit" className={`predict-btn ${loading ? 'loading' : ''}`} disabled={loading}>
                            {loading ? <Brain className="spin-fast" size={20} /> : <Sparkles size={20} />}
                            <span>{loading ? 'Analyzing Content...' : 'Run Analysis'}</span>
                        </button>
                    </form>
                </div>

                {error && (
                    <div className="lab-error animate-slide-up">
                        <AlertCircle size={20} />
                        <span>{error}</span>
                    </div>
                )}

                {result && (
                    <div className="result-section animate-slide-up">
                        <div className="overall-feeling glass-card" style={{ borderLeft: `4px solid ${getSentimentColor(result.feeling)}` }}>
                            <div className="feeling-header">
                                <span className="label">Overall Sentiment</span>
                                <div className={`sentiment-badge ${result.feeling}`}>
                                    {result.feeling?.toUpperCase()}
                                </div>
                            </div>
                            <div className="sentiment-bar">
                                <div 
                                    className={`bar-fill ${result.feeling}`}
                                    style={{ width: result.feeling === 'positive' ? '100%' : result.feeling === 'negative' ? '30%' : '60%' }}
                                ></div>
                            </div>
                        </div>

                        <div className="intents-grid">
                            {result.intents.length > 0 ? (
                                result.intents.map((intent, idx) => (
                                    <div key={idx} className={`intent-card glass-card ${intent.type.toLowerCase()}`}>
                                        <div className="intent-icon">
                                            {getPillarIcon(intent.pillar)}
                                        </div>
                                        <div className="intent-details">
                                            <span className="pillar-name">{intent.pillar}</span>
                                            <span className="intent-type">{intent.type}</span>
                                        </div>
                                        <div className="intent-status">
                                            <CheckCircle2 size={16} />
                                        </div>
                                    </div>
                                ))
                            ) : (
                                <div className="no-intents glass-card">
                                    <AlertCircle size={32} />
                                    <p>No specific intents detected. The model categorized this as general feedback.</p>
                                </div>
                            )}
                        </div>
                    </div>
                )}
            </div>
        </div>
    );
};

export default Lab;
