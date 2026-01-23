import React, { useEffect, useRef } from 'react';
import * as d3 from 'd3';
import cloud from 'd3-cloud';

const WordCloud = ({ words, theme }) => {
    const svgRef = useRef();

    useEffect(() => {
        if (!words || words.length === 0) return;

        // Clear previous SVG
        d3.select(svgRef.current).selectAll("*").remove();

        const width = 1100;
        const height = 480;

        const layout = cloud()
            .size([width, height])
            .words(words.map(d => ({
                text: d.text,
                // Linear scaling with a small base and controlled multiplier
                size: 14 + (d.value / words[0].value) * 45,
                sentiment: d.sentiment
            })))
            .padding(10) // Enough space to prevent crowding
            .rotate(() => 0)
            .font("Inter, sans-serif")
            .fontSize(d => d.size)
            .spiral("archimedean")
            .on("end", draw);

        layout.start();

        function draw(words) {
            const svg = d3.select(svgRef.current)
                .attr("width", width)
                .attr("height", height)
                .html("")
                .append("g")
                .attr("transform", `translate(${width / 2},${height / 2})`);

            svg.selectAll("text")
                .data(words)
                .enter().append("text")
                .style("font-size", d => `${d.size}px`)
                .style("font-weight", "700")
                .style("font-family", "Inter, sans-serif")
                .style("fill", d => {
                    if (d.sentiment === 'positive') return '#10b981';
                    if (d.sentiment === 'negative') return '#ef4444';
                    return '#60a5fa';
                })
                .attr("text-anchor", "middle")
                .attr("transform", d => `translate(${d.x},${d.y})`)
                .text(d => d.text)
                .style("transition", "all 0.3s ease")
                .on("mouseover", function () {
                    d3.select(this)
                        .style("opacity", 0.7)
                        .style("cursor", "default");
                })
                .on("mouseout", function () {
                    d3.select(this)
                        .style("opacity", 1);
                });
        }
    }, [words, theme]);

    return (
        <div className="word-cloud-svg-wrapper" style={{ display: 'flex', justifyContent: 'center', width: '100%' }}>
            <svg ref={svgRef}></svg>
        </div>
    );
};

export default WordCloud;
