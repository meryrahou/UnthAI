import React, { useEffect, useState, useMemo, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import { 
    CheckCircle2, 
    Loader2, 
    Sparkles, 
    Database, 
    Cpu, 
    Search, 
    BarChart3,
    Wand2
} from 'lucide-react';
import { useApp } from '../utils/AppContext';
import './Processing.css';

const Processing = () => {
    const navigate = useNavigate();
    const { t, restaurantName } = useApp();
    const [currentStep, setCurrentStep] = useState(0);
    const [progress, setProgress] = useState(0);
    const [error, setError] = useState(null);
    const [subMessage, setSubMessage] = useState("");
    const [displayCounts, setDisplayCounts] = useState({ platforms: 0, posts: 0, comments: 0 });
    
    // Use a ref for progress to avoid closures issues in animation frames
    const progressRef = useRef(0);

    const animateSmoothly = (duration, startP, endP, onFrame) => {
        return new Promise(resolve => {
            const startTime = performance.now();
            const tick = (now) => {
                const elapsed = now - startTime;
                const ratio = Math.min(elapsed / duration, 1);
                
                const frameProgress = startP + (endP - startP) * ratio;
                progressRef.current = frameProgress;
                setProgress(Math.round(frameProgress));
                
                if (onFrame) onFrame(ratio);

                if (ratio < 1) {
                    requestAnimationFrame(tick);
                } else {
                    resolve();
                }
            };
            requestAnimationFrame(tick);
        });
    };

    useEffect(() => {
        const processData = async () => {
            try {
                // STAGE 0: SOCIAL SEARCH
                setCurrentStep(0);
                setSubMessage(restaurantName === 'Loading...' ? t('workspaceSubtitle') : t('stepSearch', { name: restaurantName }));
                await animateSmoothly(3500, 0, 25);

                const token = localStorage.getItem('token');
                const response = await fetch('http://localhost:8001/api/process-data', {
                    method: 'POST',
                    headers: { 'Authorization': `Bearer ${token}` }
                });
                
                if (!response.ok) throw new Error("Processing failed");
                const result = await response.json();
                const stats = result.stats;

                // STAGE 1: DATA EXTRACTION
                setCurrentStep(1);
                const platformNames = Object.keys(stats.breakdown)
                    .map(p => t(p.toLowerCase().replace(' ', '')))
                    .join(', ');
                
                setSubMessage(t('stepFound', { count: stats.platforms, list: platformNames }));
                
                // Extra smooth flow for retrieval and count counting
                await animateSmoothly(4000, 25, 60, (ratio) => {
                    // Update stats counters smoothly in sync with bar
                    setDisplayCounts({
                        platforms: Math.floor(ratio * stats.platforms),
                        posts: Math.floor(ratio * stats.posts),
                        comments: Math.floor(ratio * stats.comments)
                    });
                    if (ratio > 0.5) {
                        setSubMessage(t('stepRetrieving', { pCount: stats.posts, cCount: stats.comments }));
                    }
                });

                // STAGE 2: AI PREDICTION ENGINE
                setCurrentStep(2);
                setSubMessage(t('stepAnalyzing'));
                
                // Scale duration based on comment volume (1s per 20 comments)
                const analysisDuration = Math.max((stats.comments / 20) * 1000, 5000);
                
                await animateSmoothly(analysisDuration, 60, 90, (ratio) => {
                    // Live increment the "analyzed X/Y" number every single frame
                    const currentProcessed = Math.min(Math.floor(ratio * stats.comments), stats.comments);
                    setSubMessage(t('analyzingSentiment', { 
                        n: currentProcessed, 
                        total: stats.comments 
                    }));
                });

                // STAGE 3: WORKSPACE PREP
                setSubMessage(t('stepGenerating'));
                await animateSmoothly(3000, 90, 95);

                setCurrentStep(3);
                setSubMessage(t('stepAlmost'));
                await animateSmoothly(3000, 95, 100);

                setSubMessage(t('workspaceFinalizing'));
                await new Promise(r => setTimeout(r, 1500));
                
                navigate('/');
                
            } catch (err) {
                console.error(err);
                setError(t('processFailed') || "Analysis failed. Please check your data sources.");
                setTimeout(() => navigate('/config'), 4000);
            }
        };

        processData();
    }, [navigate, restaurantName, t]);

    const steps = useMemo(() => [
        { id: 0, icon: <Search />, label: t('stepSearch', { name: restaurantName }) },
        { id: 1, icon: <Database />, label: t('dataExtraction') },
        { id: 2, icon: <Wand2 />, label: t('aiPredictionEngine') },
        { id: 3, icon: <BarChart3 />, label: t('workspacePreparation') }
    ], [t, restaurantName]);

    return (
        <div className="processing-page">
            <div className="magic-bg">
                <div className="blob"></div>
                <div className="blob secondary"></div>
            </div>

            <div className="processing-card glass-card">
                <div className="card-top">
                    <div className="ai-brain-container">
                        <div className={`brain-icon ${currentStep === 2 ? 'pulsing-magic' : ''}`}>
                            {currentStep < 2 ? <Cpu size={40} /> : <Sparkles size={40} className="sparkle-icon" />}
                        </div>
                        <div className="orbital-rings">
                            <div className="ring"></div>
                            <div className="ring"></div>
                        </div>
                    </div>
                    
                    <h2 className="workspace-title">{t('workspaceTitle')}</h2>
                    <p className="workspace-subtitle">{t('workspaceSubtitle')}</p>
                </div>

                <div className="progress-section">
                    <div className="progress-bar-wrapper">
                        <div className="progress-fill" style={{ width: `${progress}%` }}>
                            <div className="progress-glow"></div>
                        </div>
                    </div>
                    <div className="progress-meta">
                        <div className="message-container">
                             <span className="current-submessage">{subMessage}</span>
                        </div>
                        <span className="percentage">{progress}%</span>
                    </div>
                </div>

                <div className="stats-grid-compact">
                    <div className="mini-stat">
                        <span className="stat-num">{displayCounts.platforms}</span>
                        <span className="stat-label">{t('platforms')}</span>
                    </div>
                    <div className="mini-stat">
                        <span className="stat-num">{displayCounts.posts}</span>
                        <span className="stat-label">{t('postsCount')}</span>
                    </div>
                    <div className="mini-stat">
                        <span className="stat-num">{displayCounts.comments}</span>
                        <span className="stat-label">{t('comments')}</span>
                    </div>
                </div>

                <div className="processing-steps">
                    {steps.map((step, idx) => {
                        const status = idx < currentStep ? 'done' : (idx === currentStep ? 'active' : 'waiting');
                        return (
                            <div key={idx} className={`proc-step ${status}`}>
                                <div className="proc-icon">
                                    {status === 'done' ? <CheckCircle2 size={16} /> : step.icon}
                                </div>
                                <div className="proc-label">{step.label}</div>
                                {status === 'active' && <Loader2 size={14} className="spin-fast" />}
                            </div>
                        );
                    })}
                </div>

                {error && (
                    <div className="proc-error fade-in">
                        <span className="error-dot"></span>
                        {error}
                    </div>
                )}
            </div>
        </div>
    );
};

export default Processing;
