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
    const hasStarted = useRef(false);

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
            if (hasStarted.current) return;
            if (restaurantName === 'Loading...') return; // Wait for context
            
            hasStarted.current = true;
            try {
                const token = localStorage.getItem('token');
                
                // STAGE 0: SOCIAL SEARCH
                setCurrentStep(0);
                setSubMessage(restaurantName === 'Loading...' ? t('workspaceSubtitle') : t('stepSearch', { name: restaurantName }));
                await animateSmoothly(2000, 0, 15);

                // --- FAST STATS FETCH ---
                const statsRes = await fetch('http://localhost:8001/api/process-data/stats', {
                    headers: { 'Authorization': `Bearer ${token}` }
                });
                if (!statsRes.ok) throw new Error("Stats fetch failed");
                const stats = await statsRes.json();

                // STAGE 1: DATA EXTRACTION
                setCurrentStep(1);
                setSubMessage(t('dataExtraction'));
                await animateSmoothly(2000, 15, 30, (ratio) => {
                    setDisplayCounts({
                        platforms: Math.floor(ratio * stats.platforms),
                        posts: Math.floor(ratio * stats.posts),
                        comments: Math.floor(ratio * stats.comments)
                    });
                });

                // STAGE 2: AI PREDICTION ENGINE (STRICT WAIT)
                setCurrentStep(2);
                setSubMessage(t('aiPredictionEngine'));
                
                // 1. Kick off backend inference
                const aiProcessPromise = fetch('http://localhost:8001/api/process-data', {
                    method: 'POST',
                    headers: { 'Authorization': `Bearer ${token}` }
                });

                // 2. Run background animation
                const minAnimationTime = Math.max(5000, (stats.comments / 20) * 1000); 
                const showAIProgress = animateSmoothly(minAnimationTime, 30, 85, (ratio) => {
                    const current = Math.min(Math.floor(ratio * stats.comments), stats.comments);
                    setSubMessage(`${t('analyzingSentiment', { n: current, total: stats.comments })}...`);
                });

                // 3. Wait for BOTH (Strict Link)
                let backendRes = await aiProcessPromise;
                if (!backendRes.ok) throw new Error("AI Prediction failed");
                
                let result = await backendRes.json();
                
                // --- POLLING LOOP ---
                // If the backend says it's already processing (e.g. from a double-click or previous tab)
                // we must WAIT here until it finishes, otherwise we'll go to an empty dashboard.
                while (result.status === 'processing') {
                    setSubMessage(t('analyzingSentiment', { n: stats.comments / 2, total: stats.comments }) + " (waiting for worker...)");
                    await new Promise(r => setTimeout(r, 2000)); // Wait 2s
                    backendRes = await fetch('http://localhost:8001/api/process-data', {
                        method: 'POST',
                        headers: { 'Authorization': `Bearer ${token}` }
                    });
                    result = await backendRes.json();
                }

                if (result.status === 'warning' || result.status === 'error') {
                    throw new Error(result.message || "Model failed to find data");
                }
                
                // Wait for animation if it's still running
                await showAIProgress;
                
                // STAGE 3: WORKSPACE PREP (Happens AFTER model is 100% done)
                setCurrentStep(3);
                setSubMessage(t('stepGenerating'));
                await animateSmoothly(3000, 85, 100);

                setSubMessage(t('workspaceFinalizing'));
                await new Promise(r => setTimeout(r, 1500));
                
                // FINALLY NAVIGATE
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
