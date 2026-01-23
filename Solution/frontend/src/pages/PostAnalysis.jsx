import React, { useState, useEffect } from 'react';
import {
    Instagram,
    Facebook,
    Play,
    MapPin,
    Calendar,
    MessageSquare,
    ThumbsUp,
    Filter,
    AlertTriangle,
    Users
} from 'lucide-react';
import './PostAnalysis.css';

const PostAnalysis = () => {
    const [selectedPlatform, setSelectedPlatform] = useState('facebook');
    const [selectedPost, setSelectedPost] = useState(null);
    const [commentFilter, setCommentFilter] = useState('all');
    const [posts, setPosts] = useState([]);
    const [allComments, setAllComments] = useState([]);
    const [loading, setLoading] = useState(false);
    const [postsLoading, setPostsLoading] = useState(true);

    useEffect(() => {
        const fetchPosts = async () => {
            setPostsLoading(true);
            try {
                const response = await fetch('http://localhost:8001/api/posts', {
                    headers: { 'Authorization': `Bearer ${localStorage.getItem('token')}` }
                });
                if (response.ok) {
                    const data = await response.json();
                    setPosts(data);
                    // Select the first post found, whatever platform it is
                    if (data.length > 0) {
                        setSelectedPost(data[0].id);
                        setSelectedPlatform(data[0].platform);
                    }
                }
            } catch (err) { console.error(err); }
            setPostsLoading(false);
        };
        fetchPosts();
    }, []);

    useEffect(() => {
        if (selectedPost === null) return;
        const fetchComments = async () => {
            setLoading(true);
            try {
                const response = await fetch(`http://localhost:8001/api/posts/${selectedPost}/comments`, {
                    headers: { 'Authorization': `Bearer ${localStorage.getItem('token')}` }
                });
                if (response.ok) {
                    const data = await response.json();
                    setAllComments(data);
                }
            } catch (err) { console.error(err); }
            setLoading(false);
        };
        fetchComments();
    }, [selectedPost]);

    const activePost = posts.find(p => p.id === selectedPost) || {
        author: 'N/A',
        date: 'N/A',
        content: '',
        sentiment: { pos: 0, neu: 0, neg: 0 },
        categories: []
    };

    const getPlatformIcon = (plat) => {
        switch (plat) {
            case 'facebook': return <Facebook size={20} color="white" />;
            case 'tiktok': return <Play size={20} color="white" />;
            case 'instagram': return <Instagram size={20} color="white" />;
            default: return <MapPin size={20} color="white" />;
        }
    };

    if (postsLoading) {
        return <div className="loading-container">Gathering social data...</div>;
    }

    return (
        <div className="analysis-page animate-fade-in">
            <div className="sidebar-analysis">
                <div className="platform-filter">
                    {['tiktok', 'instagram', 'facebook', 'googlemaps'].map(p => {
                        const count = posts.filter(post => post.platform === p).length;
                        if (count === 0) return null;

                        return (
                            <button
                                key={p}
                                className={`platform-btn ${selectedPlatform === p ? 'active' : ''}`}
                                onClick={() => setSelectedPlatform(p)}
                            >
                                {p === 'tiktok' ? <Play size={18} /> :
                                    p === 'facebook' ? <Facebook size={18} /> :
                                        p === 'instagram' ? <Instagram size={18} /> :
                                            <MapPin size={18} />}
                                <span style={{ textTransform: 'capitalize' }}>{p === 'googlemaps' ? 'Maps' : p}</span>
                                <span className="platform-count">{count}</span>
                            </button>
                        );
                    })}
                </div>

                <div className="posts-list">
                    <h3>Recent Content</h3>
                    {posts.filter(p => !selectedPlatform || p.platform === selectedPlatform).map((post) => (
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
                        <div className={`preview-avatar platform-${activePost.platform}`}>
                            {getPlatformIcon(activePost.platform)}
                        </div>
                        <div className="preview-info">
                            <h2>Post Analysis</h2>
                            <p>{activePost.author} • {activePost.date}</p>
                        </div>
                    </div>
                    <p className="post-full-content">{activePost.content || "Select a post to view analysis."}</p>
                </div>

                <div className="analysis-grid">
                    <div className="glass-card detail-card">
                        <h3>Sentiment Intensity</h3>
                        <div className="sentiment-bars">
                            <div className="sentiment-bar-item">
                                <div className="bar-label">Positive</div>
                                <div className="bar-outer"><div className="bar-inner pos" style={{ width: `${activePost.sentiment?.pos || 0}%` }}></div></div>
                                <div className="bar-value">{activePost.sentiment?.pos || 0}%</div>
                            </div>
                            <div className="sentiment-bar-item">
                                <div className="bar-label">Neutral</div>
                                <div className="bar-outer"><div className="bar-inner neu" style={{ width: `${activePost.sentiment?.neu || 0}%` }}></div></div>
                                <div className="bar-value">{activePost.sentiment?.neu || 0}%</div>
                            </div>
                            <div className="sentiment-bar-item">
                                <div className="bar-label">Negative</div>
                                <div className="bar-outer"><div className="bar-inner neg" style={{ width: `${activePost.sentiment?.neg || 0}%` }}></div></div>
                                <div className="bar-value">{activePost.sentiment?.neg || 0}%</div>
                            </div>
                        </div>
                    </div>

                    <div className="glass-card detail-card">
                        <h3>Category Performance</h3>
                        <div className="category-scores">
                            {(activePost.categories || []).map((cat, idx) => (
                                <div key={idx} className="category-score-item">
                                    <div className="cat-header">
                                        <div className="cat-name-group">
                                            <span>{cat.name}</span>
                                            {cat.critical && <AlertTriangle size={14} color="var(--error)" title="Critical Platform Disparity" />}
                                            <span className="cat-volume"><Users size={12} /> {cat.volume}</span>
                                        </div>
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
                            {(!activePost.categories || activePost.categories.length === 0) && <p className="empty-text">No category data available.</p>}
                        </div>
                    </div>
                </div>

                <div className="glass-card top-comments">
                    <div className="comments-header">
                        <h3>Representative Comments</h3>
                        <div className="filter-group">
                            <button
                                className={`filter-btn ${commentFilter === 'all' ? 'active' : ''}`}
                                onClick={() => setCommentFilter('all')}
                            >
                                All
                            </button>
                            <button
                                className={`filter-btn ${commentFilter === 'appreciation' ? 'active' : ''}`}
                                onClick={() => setCommentFilter('appreciation')}
                            >
                                <div className="comment-sentiment-dot appreciation"></div>
                                Appreciation
                            </button>
                            <button
                                className={`filter-btn ${commentFilter === 'complaint' ? 'active' : ''}`}
                                onClick={() => setCommentFilter('complaint')}
                            >
                                <div className="comment-sentiment-dot complaint"></div>
                                Complaint
                            </button>
                            <button
                                className={`filter-btn ${commentFilter === 'recommendation' ? 'active' : ''}`}
                                onClick={() => setCommentFilter('recommendation')}
                            >
                                <div className="comment-sentiment-dot recommendation"></div>
                                Recommendation
                            </button>
                            <button
                                className={`filter-btn ${commentFilter === 'inquiry' ? 'active' : ''}`}
                                onClick={() => setCommentFilter('inquiry')}
                            >
                                <div className="comment-sentiment-dot inquiry"></div>
                                Inquiry
                            </button>
                        </div>
                    </div>
                    {loading ? (
                        <div className="loading-small">Loading comments...</div>
                    ) : (
                        <ul className="comment-list">
                            {allComments
                                .filter(c => commentFilter === 'all' || c.type === commentFilter)
                                .map((comment, idx) => (
                                    <li key={idx} className="comment-item animate-fade-in">
                                        <div className={`comment-sentiment-dot ${comment.type}`}></div>
                                        <div className="comment-content">
                                            <p>"{comment.text}"</p>
                                            <div className="comment-meta">
                                                <span className={`meta-cat ${comment.type}`}>{comment.category}</span> • <span>{comment.time}</span>
                                                {comment.likesCount > 0 && (
                                                    <span className="comment-likes" style={{ display: 'inline-flex', alignItems: 'center', gap: '4px', marginLeft: '12px', color: 'var(--text-dim)' }}>
                                                        <ThumbsUp size={12} /> {comment.likesCount}
                                                    </span>
                                                )}
                                            </div>
                                        </div>
                                    </li>
                                ))
                            }
                            {allComments.filter(c => commentFilter === 'all' || c.type === commentFilter).length === 0 && (
                                <li className="empty-comments">No comments found for this filter.</li>
                            )}
                        </ul>
                    )}
                </div>
            </div>
        </div>
    );
};

export default PostAnalysis;
