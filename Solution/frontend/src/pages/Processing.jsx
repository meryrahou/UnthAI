import React, { useEffect, useState, useMemo } from 'react';
import { useNavigate } from 'react-router-dom';
import { 
    CheckCircle2, 
    Loader2, 
    Sparkles, 
    Database, 
    Cpu, 
    Search, 
    MessageSquare, 
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
    const [stats, setStats] = useState(null);
    const [error, setError] = useState(null);
    const [subMessage, setSubMessage] = useState("");
    const [displayCounts, setDisplayCounts] = useState({ platforms: 0, posts: 0, comments: 0 });

    // Step labels are now fetched via translations in the step rendering logic

    useEffect(() => {
        const processData = async () => {
            try {
                // STAGE 1: SOCIAL SEARCH
                setCurrentStep(0);
                setProgress(10);
                setSubMessage(restaurantName === 'Loading...' ? t('workspaceSubtitle') : t('stepSearch', { name: restaurantName }));
                await new Promise(r => setTimeout(r, 3500));
                setProgress(25);

                const token = localStorage.getItem('token');
                const response = await fetch('http://localhost:8001/api/process-data', {
                    method: 'POST',
                    headers: { 'Authorization': `Bearer ${token}` }
                });
                
                if (!response.ok) throw new Error("Processing failed");
                const result = await response.json();
                const fetchedStats = result.stats;
                setStats(fetchedStats);

                // Incremental count animation
                const duration = 4000;
                const startTime = performance.now();
                const animateCounts = (now) => {
                    const elapsed = now - startTime;
                    const p = Math.min(elapsed / duration, 1);
                    setDisplayCounts({
                        platforms: Math.floor(p * fetchedStats.platforms),
                        posts: Math.floor(p * fetchedStats.posts),
                        comments: Math.floor(p * fetchedStats.comments)
                    });
                    if (p < 1) requestAnimationFrame(animateCounts);
                };
                requestAnimationFrame(animateCounts);

                // STAGE 2: RETRIEVAL
                setCurrentStep(1);
                setProgress(40);
                const platformNames = Object.keys(fetchedStats.breakdown)
                    .map(p => t(p.toLowerCase().replace(' ', '')))
                    .join(', ');
                setSubMessage(t('stepFound', { count: fetchedStats.platforms, list: platformNames }));
                await new Promise(r => setTimeout(r, 3000));
                
                setProgress(60);
                setSubMessage(t('stepRetrieving', { pCount: fetchedStats.posts, cCount: fetchedStats.comments }));
                await new Promise(r => setTimeout(r, 3500));

                // STAGE 3: AI ANALYSIS (THE MAGIC STAGE)
                setCurrentStep(2);
                setProgress(75);
                setSubMessage(t('stepAnalyzing'));
                
                // Simulate "processing comments" detail
                for (let i = 1; i <= 5; i++) {
                    setSubMessage(t('analyzingSentiment', { n: Math.floor((i/5) * fetchedStats.comments), total: fetchedStats.comments }));
                    await new Promise(r => setTimeout(r, 1200));
                }
                
                setProgress(90);
                setSubMessage(t('stepGenerating'));
                await new Promise(r => setTimeout(r, 3000));
                
                // STAGE 4: FINALIZING
                setCurrentStep(3);
                setProgress(100);
                setSubMessage(t('stepAlmost'));
                await new Promise(r => setTimeout(r, 2500));

                setSubMessage(t('workspaceFinalizing'));
                await new Promise(r => setTimeout(r, 2000));
                
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
        { id: 1, icon: <Database />, label: "Data Extraction" },
        { id: 2, icon: <Wand2 />, label: "AI Prediction Engine" },
        { id: 3, icon: <BarChart3 />, label: "Workspace Preparation" }
    ], [t, restaurantName]);

    return (
        <div className="processing-page">
            {/* Background Magic Particles would go here if we had a library, using CSS magic instead */}
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
                        <span className="current-submessage">{subMessage}</span>
                        <span className="percentage">{progress}%</span>
                    </div>
                </div>

                <div className="stats-grid">
                    <div className="mini-stat">
                        <span className="stat-num">{displayCounts.platforms}</span>
                        <span className="stat-label">Platforms</span>
                    </div>
                    <div className="mini-stat">
                        <span className="stat-num">{displayCounts.posts}</span>
                        <span className="stat-label">Posts</span>
                    </div>
                    <div className="mini-stat">
                        <span className="stat-num">{displayCounts.comments}</span>
                        <span className="stat-label">Comments</span>
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
