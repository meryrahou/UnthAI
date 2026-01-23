import React from 'react';
import { NavLink } from 'react-router-dom';
import {
    BarChart3,
    MessageSquareText,
    Sparkles,
    Settings,
    User,
    LogOut,
    LayoutDashboard,
    Zap,
    Target
} from 'lucide-react';
import './Sidebar.css';

const Sidebar = ({ onLogout }) => {
    return (
        <aside className="sidebar">
            <div className="logo-container">
                <div className="logo-icon">
                    <Sparkles size={24} color="#ff6b35" />
                </div>
                <h2 className="logo-text">Unth<span>AI</span></h2>
            </div>

            <nav className="nav-links">
                <NavLink to="/" end className={({ isActive }) => isActive ? 'nav-item active' : 'nav-item'}>
                    <LayoutDashboard size={20} />
                    <span>Dashboard</span>
                </NavLink>
                <NavLink to="/analysis" className={({ isActive }) => isActive ? 'nav-item active' : 'nav-item'}>
                    <BarChart3 size={20} />
                    <span>Post Analysis</span>
                </NavLink>
                <NavLink to="/trends" className={({ isActive }) => isActive ? 'nav-item active' : 'nav-item'}>
                    <Zap size={20} />
                    <span>Trend Explorer</span>
                </NavLink>
                <NavLink to="/actions" className={({ isActive }) => isActive ? 'nav-item active' : 'nav-item'}>
                    <Target size={20} />
                    <span>Action Center</span>
                </NavLink>
                <NavLink to="/insights" className={({ isActive }) => isActive ? 'nav-item active' : 'nav-item'}>
                    <Sparkles size={20} />
                    <span>AI Insights</span>
                </NavLink>
                <NavLink to="/config" className={({ isActive }) => isActive ? 'nav-item active' : 'nav-item'}>
                    <Settings size={20} />
                    <span>Settings</span>
                </NavLink>
            </nav>

            <div className="sidebar-footer">
                <NavLink to="/profile" className="nav-item">
                    <User size={20} />
                    <span>Profile</span>
                </NavLink>
                <button onClick={onLogout} className="logout-btn">
                    <LogOut size={20} />
                    <span>Logout</span>
                </button>
            </div>
        </aside>
    );
};

export default Sidebar;
