import React, { useState, useEffect, useRef } from 'react';
import * as d3 from 'd3';
import cloud from 'd3-cloud';
import { Zap } from 'lucide-react';
import './Trends.css';

const Trends = () => {
    const [words, setWords] = useState([]);
    const [loading, setLoading] = useState(true);
    const svgRef = useRef(null);

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

    useEffect(() => {
        if (!words.length || !svgRef.current) return;

        const layout = cloud()
            .size([800, 500])
            .words(words.map(d => ({ text: d.text, size: 10 + Math.sqrt(d.value) * 10, sentiment: d.sentiment })))
            .padding(5)
            .rotate(0) // Force horizontal
            .font("Inter")
            .fontSize(d => d.size)
            .on("end", draw);

        layout.start();

        function draw(words) {
            d3.select(svgRef.current).selectAll("*").remove(); // Clear previous
            d3.select(svgRef.current)
                .attr("width", layout.size()[0])
                .attr("height", layout.size()[1])
                .append("g")
                .attr("transform", "translate(" + layout.size()[0] / 2 + "," + layout.size()[1] / 2 + ")")
                .selectAll("text")
                .data(words)
                .enter().append("text")
                .style("font-size", d => d.size + "px")
                .style("font-family", "Inter")
                .style("fill", d => {
                    // Color based on sentiment
                    if (d.sentiment === 'positive') return '#10b981'; // Green
                    if (d.sentiment === 'negative') return '#ef4444'; // Red
                    return '#60a5fa'; // Blue for neutral
                })
                .attr("text-anchor", "middle")
                .attr("transform", d => "translate(" + [d.x, d.y] + ")rotate(" + d.rotate + ")")
                .text(d => d.text);
        }
    }, [words]);

    if (loading) return <div className="loading-container">Generating trend analysis...</div>;

    return (
        <div className="trends-page animate-fade-in">
            <div className="trends-header">
                <div>
                    <h2><Zap size={24} style={{ display: 'inline', marginRight: '8px', color: '#ff9f1c' }} /> Trend Explorer</h2>
                    <p>Discover what people are talking about most.</p>
                </div>
            </div>

            <div className="glass-card cloud-container">
                <svg ref={svgRef} className="word-cloud-svg"></svg>
                {words.length === 0 && <div className="empty-state">No trend data available.</div>}
            </div>

            <div className="trends-header" style={{ marginTop: '40px' }}>
                <h3>Top Keywords</h3>
            </div>

            <div className="trending-list">
                {words.slice(0, 12).map((w, idx) => (
                    <div key={idx} className="trend-item">
                        <span className="trend-word">{w.text}</span>
                        <span className="trend-count">{w.value} mentions</span>
                    </div>
                ))}
            </div>
        </div>
    );
};

export default Trends;
