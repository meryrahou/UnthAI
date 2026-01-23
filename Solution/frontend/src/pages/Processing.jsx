import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { CheckCircle2, Circle, Loader2, Sparkles, Database } from 'lucide-react';
import './Processing.css';

const Processing = () => {
    const navigate = useNavigate();
    const [currentStep, setCurrentStep] = useState(0);
    const [error, setError] = useState(null);

    const steps = [
        {
            id: 1,
            label: "Searching Owner's Social Media...",
            icon: <Database size={18} />,
            duration: 1500 // Simulated delay for visual effect
        },
        {
            id: 2,
            label: "Retrieving Comments & Feedback...",
            icon: <Loader2 size={18} className="animate-spin" />,
            duration: 2000
        },
        {
            id: 3,
            label: "Running AI Analysis & Predictions...",
            icon: <Sparkles size={18} />,
            duration: 2000
        }
    ];

    useEffect(() => {
        const processData = async () => {
            try {
                // Step 1: Database/Social Lookup
                setCurrentStep(0);
                await new Promise(r => setTimeout(r, 1500));
                
                // Step 2: Retrieving logic (API Call)
                setCurrentStep(1);
                
                // Trigger the actual backend processing here
                // We do it in step 2 or 3. Let's do it parallel to step 2 animation or wait.
                const token = localStorage.getItem('token');
                const response = await fetch('http://localhost:8001/api/process-data', {
                    method: 'POST',
                    headers: {
                        'Authorization': `Bearer ${token}`
                    }
                });
                
                if (!response.ok) {
                    throw new Error("Failed to process data");
                }
                
                // Wait for animation to finish minimal time
                await new Promise(r => setTimeout(r, 1000));

                // Step 3: AI Magic
                setCurrentStep(2);
                await new Promise(r => setTimeout(r, 2000));
                
                // Done
                navigate('/');
                
            } catch (err) {
                console.error(err);
                setError("Something went wrong processing your data. Please try again.");
                // Optionally navigate anyway or show error
                setTimeout(() => navigate('/'), 3000);
            }
        };

        processData();
    }, [navigate]);

    return (
        <div className="processing-page">
            <div className="processing-container">
                <div className="spinner-ring"></div>
                <h2>Setting up your Workspace</h2>
                <p style={{color: '#888', marginBottom: '30px'}}>Please wait while UnthAI analyzes your data...</p>
                
                {error ? (
                    <div style={{color: 'var(--error, #ef4444)'}}>{error}</div>
                ) : (
                    <div className="steps-list">
                        {steps.map((step, index) => {
                            let status = 'pending';
                            if (index < currentStep) status = 'completed';
                            if (index === currentStep) status = 'active';

                            return (
                                <div key={step.id} className={`step-item ${status}`}>
                                    <div className="step-icon">
                                        {status === 'completed' ? (
                                            <CheckCircle2 size={18} color="#10b981" />
                                        ) : status === 'active' ? (
                                            step.icon
                                        ) : (
                                            <Circle size={18} color="#444" />
                                        )}
                                    </div>
                                    <div className="step-text">{step.label}</div>
                                </div>
                            );
                        })}
                    </div>
                )}
            </div>
        </div>
    );
};

export default Processing;
