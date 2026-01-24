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
import { useApp } from '../utils/AppContext';
import './PostAnalysis.css';

const PostAnalysis = () => {
    const { t } = useApp();
    const [selectedPlatform, setSelectedPlatform] = useState('facebook');
    const [selectedPost, setSelectedPost] = useState(null);
    const [commentFilter, setCommentFilter] = useState('all');
    const [posts, setPosts] = useState([]);
    const [allComments, setAllComments] = useState([]);
    const [loading, setLoading] = useState(false);
    const [postsLoading, setPostsLoading] = useState(true);
    const [startDate, setStartDate] = useState('');
    const [endDate, setEndDate] = useState('');

    useEffect(() => {
        const fetchDefaultDates = async () => {
            try {
                const response = await fetch('http://localhost:8001/api/dashboard/summary', {
                    headers: { 'Authorization': `Bearer ${localStorage.getItem('token')}` }
                });
                if (response.ok) {
                    const data = await response.json();
                    setStartDate(data.startDate);
                    setEndDate(data.endDate);
                }
            } catch (err) { console.error("Error fetching dates:", err); }
        };
        fetchDefaultDates();
    }, []);

    useEffect(() => {
        const fetchPosts = async () => {
            setPostsLoading(true);
            try {
                const query = startDate && endDate ? `?start_date=${startDate}&end_date=${endDate}` : '';
                const response = await fetch(`http://localhost:8001/api/posts${query}`, {
                    headers: { 'Authorization': `Bearer ${localStorage.getItem('token')}` }
                });
                if (response.ok) {
                    const data = await response.json();
                    setPosts(data);
                    const currentPostExists = data.find(p => p.id === selectedPost);
                    if (!currentPostExists && data.length > 0) {
                        setSelectedPost(data[0].id);
                        setSelectedPlatform(data[0].platform);
                    } else if (data.length === 0) {
                        setSelectedPost(null);
                    }
                }
            } catch (err) { console.error(err); }
            setPostsLoading(false);
        };
        fetchPosts();
    }, [startDate, endDate]);

    useEffect(() => {
        if (selectedPost === null) {
            setAllComments([]);
            return;
        }
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

    if (postsLoading && !posts.length && !startDate) {
        return <div className="loading-container"><div className="spinner"></div><p>Gathering social data...</p></div>;
    }

    return (
        <div className="analysis-page animate-fade-in">
            <div className="sidebar-analysis">
                <div className="date-filter-section">
                    <label>{t('summary').toUpperCase()}</label>
                    <div className="date-inputs">
                        <input
                            type="date"
                            value={startDate}
                            onChange={(e) => setStartDate(e.target.value)}
                        />
                        <input
                            type="date"
                            value={endDate}
                            onChange={(e) => setEndDate(e.target.value)}
                        />
                    </div>
                </div>

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
                                <span>{t(p)}</span>
                                <span className="platform-count">{count}</span>
                            </button>
                        );
                    })}
                </div>

                <div className="posts-list">
                    <h3>{t('postPerformance')}</h3>
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
                            <p className="post-excerpt">{t('analyzingInteractions', { count: post.content })}</p>
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
                            <h2>{t('postAnalysis')}</h2>
                            <p>{activePost.author} • {activePost.date}</p>
                        </div>
                    </div>
                    <p className="post-full-content">{activePost.content ? t('analyzingInteractions', { count: activePost.content }) : "Select a post to view analysis."}</p>
                </div>

                <div className="analysis-grid">
                    <div className="glass-card detail-card">
                        <h3>{t('sentimentDistribution')}</h3>
                        <div className="sentiment-bars">
                            <div className="sentiment-bar-item">
                                <div className="bar-label">{t('positive')}</div>
                                <div className="bar-outer"><div className="bar-inner pos" style={{ width: `${activePost.sentiment?.pos || 0}%` }}></div></div>
                                <div className="bar-value">{activePost.sentiment?.pos || 0}%</div>
                            </div>
                            <div className="sentiment-bar-item">
                                <div className="bar-label">{t('neutral')}</div>
                                <div className="bar-outer"><div className="bar-inner neu" style={{ width: `${activePost.sentiment?.neu || 0}%` }}></div></div>
                                <div className="bar-value">{activePost.sentiment?.neu || 0}%</div>
                            </div>
                            <div className="sentiment-bar-item">
                                <div className="bar-label">{t('negative')}</div>
                                <div className="bar-outer"><div className="bar-inner neg" style={{ width: `${activePost.sentiment?.neg || 0}%` }}></div></div>
                                <div className="bar-value">{activePost.sentiment?.neg || 0}%</div>
                            </div>
                        </div>
                    </div>

                    <div className="glass-card detail-card">
                        <h3>{t('categoryPerformance')}</h3>
                        <div className="category-scores">
                            {(activePost.categories || []).map((cat, idx) => (
                                <div key={idx} className="category-score-item">
                                    <div className="cat-header">
                                        <div className="cat-name-group">
                                            <span>{t(`pillers.${cat.name.toLowerCase()}`)}</span>
                                            {cat.critical && <AlertTriangle size={14} color="var(--error)" />}
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
                        </div>
                    </div>
                </div>

                <div className="glass-card top-comments">
                    <div className="comments-header">
                        <h3>{t('representativeComments')}</h3>
                        <div className="filter-group">
                            {['all', 'appreciation', 'complaint', 'recommendation', 'inquiry'].map(f => (
                                <button
                                    key={f}
                                    className={`filter-btn ${commentFilter === f ? 'active' : ''}`}
                                    onClick={() => setCommentFilter(f)}
                                >
                                    {f !== 'all' && <div className={`comment-sentiment-dot ${f}`}></div>}
                                    {f === 'all' ? t('all') : t(f)}
                                </button>
                            ))}
                        </div>
                    </div>
                    {loading ? (
                        <div className="loading-small">Loading comments...</div>
                    ) : (
                        <div className="comments-content-wrapper">
                            {allComments.filter(c => commentFilter === 'all' || c.type === commentFilter).length > 0 ? (
                                <ul className="comment-list">
                                    {allComments
                                        .filter(c => commentFilter === 'all' || c.type === commentFilter)
                                        .map((comment, idx) => (
                                            <li key={idx} className="comment-item animate-fade-in">
                                                <div className={`comment-sentiment-dot ${comment.type}`}></div>
                                                <div className="comment-content">
                                                    <p>"{comment.text}"</p>
                                                    <div className="comment-meta">
                                                        <span className={`meta-cat ${comment.type}`}>
                                                            {t(`pillers.${comment.category.toLowerCase()}`) || comment.category}
                                                        </span> • <span>{comment.time}</span>
                                                        {comment.likesCount > 0 && (
                                                            <span className="comment-likes">
                                                                <ThumbsUp size={12} /> {comment.likesCount}
                                                            </span>
                                                        )}
                                                    </div>
                                                </div>
                                            </li>
                                        ))
                                    }
                                </ul>
                            ) : (
                                <div className="no-comments-state animate-fade-in">
                                    <MessageSquare size={40} className="empty-icon" />
                                    <p>{t('noComments')}</p>
                                </div>
                            )}
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
};

export default PostAnalysis;
