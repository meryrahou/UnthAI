import React, { useState } from 'react';
import {
    Instagram,
    Facebook,
    Play,
    MapPin,
    Calendar,
    MessageSquare,
    ThumbsUp,
    Filter
} from 'lucide-react';
import './PostAnalysis.css';

const PostAnalysis = () => {
    const [selectedPlatform, setSelectedPlatform] = useState('tiktok');
    const [selectedPost, setSelectedPost] = useState(0);

    // Mock Posts
    const posts = [
        {
            id: 0,
            platform: 'tiktok',
            author: '@uncles_burger_dz',
            date: 'Jan 02, 2026',
            content: 'Our new Smash Burger with extra cheese! 🧀🔥',
            commentCount: 156,
            likes: '3.2k',
            sentiment: { pos: 75, neu: 15, neg: 10 },
            categories: [
                { name: 'Food', score: 92 },
                { name: 'Price', score: 65 },
                { name: 'Service', score: 80 }
            ]
        },
        {
            id: 1,
            platform: 'tiktok',
            author: '@spotter.dz',
            date: 'Dec 28, 2025',
            content: 'Sampling the best grill in Algiers. Worth the hype?',
            commentCount: 89,
            likes: '1.5k',
            sentiment: { pos: 60, neu: 20, neg: 20 },
            categories: [
                { name: 'Food', score: 85 },
                { name: 'Service', score: 45 },
                { name: 'Place', score: 90 }
            ]
        },
        {
            id: 2,
            platform: 'instagram',
            author: 'american.burger_dz',
            date: 'Dec 20, 2025',
            content: 'Weekend vibes at American Burger! 🍔✨',
            commentCount: 45,
            likes: '850',
            sentiment: { pos: 88, neu: 10, neg: 2 },
            categories: [
                { name: 'Place', score: 95 },
                { name: 'Treatment', score: 88 }
            ]
        }
    ];

    const filteredPosts = posts.filter(p => p.platform === selectedPlatform);
    const activePost = posts[selectedPost];

    return (
        <div className="analysis-page animate-fade-in">
            <div className="sidebar-analysis">
                <div className="platform-filter">
                    <button
                        className={`platform-btn ${selectedPlatform === 'tiktok' ? 'active' : ''}`}
                        onClick={() => setSelectedPlatform('tiktok')}
                    >
                        <Play size={18} />
                        <span>TikTok</span>
                    </button>
                    <button
                        className={`platform-btn ${selectedPlatform === 'instagram' ? 'active' : ''}`}
                        onClick={() => setSelectedPlatform('instagram')}
                    >
                        <Instagram size={18} />
                        <span>Instagram</span>
                    </button>
                    <button
                        className={`platform-btn ${selectedPlatform === 'facebook' ? 'active' : ''}`}
                        onClick={() => setSelectedPlatform('facebook')}
                    >
                        <Facebook size={18} />
                        <span>Facebook</span>
                    </button>
                    <button
                        className={`platform-btn ${selectedPlatform === 'google' ? 'active' : ''}`}
                        onClick={() => setSelectedPlatform('google')}
                    >
                        <MapPin size={18} />
                        <span>Maps</span>
                    </button>
                </div>

                <div className="posts-list">
                    <h3>Recent Content</h3>
                    {filteredPosts.map((post) => (
                        <div
                            key={post.id}
                            className={`post-card ${selectedPost === post.id ? 'active' : ''}`}
                            onClick={() => setSelectedPost(post.id)}
                        >
                            <div className="post-header">
                                <span className="post-author">{post.author}</span>
                                <span className="post-date">{post.date}</span>
                            </div>
                            <p className="post-excerpt">{post.content}</p>
                            <div className="post-stats">
                                <span><MessageSquare size={14} /> {post.commentCount}</span>
                                <span><ThumbsUp size={14} /> {post.likes}</span>
                            </div>
                        </div>
                    ))}
                </div>
            </div>

            <div className="main-analysis">
                <div className="analysis-header glass-card">
                    <div className="active-post-preview">
                        <div className="preview-avatar">
                            <Play size={20} color="white" />
                        </div>
                        <div className="preview-info">
                            <h2>Post Analysis</h2>
                            <p>{activePost.author} • {activePost.date}</p>
                        </div>
                    </div>
                    <p className="post-full-content">"{activePost.content}"</p>
                </div>

                <div className="analysis-grid">
                    <div className="glass-card detail-card">
                        <h3>Sentiment Intensity</h3>
                        <div className="sentiment-bars">
                            <div className="sentiment-bar-item">
                                <div className="bar-label">Positive</div>
                                <div className="bar-outer"><div className="bar-inner pos" style={{ width: `${activePost.sentiment.pos}%` }}></div></div>
                                <div className="bar-value">{activePost.sentiment.pos}%</div>
                            </div>
                            <div className="sentiment-bar-item">
                                <div className="bar-label">Neutral</div>
                                <div className="bar-outer"><div className="bar-inner neu" style={{ width: `${activePost.sentiment.neu}%` }}></div></div>
                                <div className="bar-value">{activePost.sentiment.neu}%</div>
                            </div>
                            <div className="sentiment-bar-item">
                                <div className="bar-label">Negative</div>
                                <div className="bar-outer"><div className="bar-inner neg" style={{ width: `${activePost.sentiment.neg}%` }}></div></div>
                                <div className="bar-value">{activePost.sentiment.neg}%</div>
                            </div>
                        </div>
                    </div>

                    <div className="glass-card detail-card">
                        <h3>Category Performance</h3>
                        <div className="category-scores">
                            {activePost.categories.map((cat, idx) => (
                                <div key={idx} className="category-score-item">
                                    <div className="cat-header">
                                        <span>{cat.name}</span>
                                        <span>{cat.score}/100</span>
                                    </div>
                                    <div className="cat-progress">
                                        <div
                                            className="cat-progress-fill"
                                            style={{
                                                width: `${cat.score}%`,
                                                background: cat.score > 70 ? 'var(--success)' : cat.score > 40 ? 'var(--warning)' : 'var(--error)'
                                            }}
                                        ></div>
                                    </div>
                                </div>
                            ))}
                        </div>
                    </div>
                </div>

                <div className="glass-card top-comments">
                    <div className="comments-header">
                        <h3>Representative Comments</h3>
                        <button className="filter-btn"><Filter size={16} /> Filter</button>
                    </div>
                    <ul className="comment-list">
                        <li className="comment-item">
                            <div className="comment-sentiment-dot pos"></div>
                            <div className="comment-content">
                                <p>"The burger was actually insane, best in Algiers so far!"</p>
                                <div className="comment-meta">
                                    <span>Food Appreciation</span> • <span>2h ago</span>
                                </div>
                            </div>
                        </li>
                        <li className="comment-item">
                            <div className="comment-sentiment-dot neg"></div>
                            <div className="comment-content">
                                <p>"Took 45 minutes to arrive. Food was cold."</p>
                                <div className="comment-meta">
                                    <span>Service Complaint</span> • <span>5h ago</span>
                                </div>
                            </div>
                        </li>
                        <li className="comment-item">
                            <div className="comment-sentiment-dot neu"></div>
                            <div className="comment-content">
                                <p>"How much for the double patty?"</p>
                                <div className="comment-meta">
                                    <span>Price Inquiry</span> • <span>1d ago</span>
                                </div>
                            </div>
                        </li>
                    </ul>
                </div>
            </div>
        </div>
    );
};

export default PostAnalysis;
