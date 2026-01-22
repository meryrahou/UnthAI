import React from 'react';
import { User, Mail, Building2, Bell, Shield, LogOut } from 'lucide-react';
import './Profile.css';

const Profile = () => {
    return (
        <div className="profile-page animate-fade-in">
            <div className="page-header">
                <h1>Account Profile</h1>
                <p className="subtitle">Manage your personal information and application preferences.</p>
            </div>

            <div className="profile-content">
                <div className="profile-sidebar">
                    <div className="glass-card user-main-card">
                        <div className="avatar-large">M</div>
                        <h2>Mery's Restaurant</h2>
                        <p className="user-email">mery@unthai.dz</p>
                        <button className="edit-btn">Edit Profile</button>
                    </div>

                    <div className="glass-card account-stats">
                        <div className="a-stat">
                            <span className="label">Plan</span>
                            <span className="value">Enterprise</span>
                        </div>
                        <div className="a-stat">
                            <span className="label">Analyzed</span>
                            <span className="value">12.5k Comments</span>
                        </div>
                    </div>
                </div>

                <div className="profile-main">
                    <div className="glass-card settings-section">
                        <h3>General Settings</h3>
                        <div className="settings-list">
                            <div className="setting-item">
                                <div className="setting-icon"><Building2 size={20} /></div>
                                <div className="setting-info">
                                    <h4>Restaurant Details</h4>
                                    <p>Mery's Grill & Bar, Algiers Center</p>
                                </div>
                                <button className="text-btn">Manage</button>
                            </div>
                            <div className="setting-item">
                                <div className="setting-icon"><Bell size={20} /></div>
                                <div className="setting-info">
                                    <h4>Notification Preferences</h4>
                                    <p>Email alerts for negative sentiment spikes</p>
                                </div>
                                <button className="text-btn">Configure</button>
                            </div>
                            <div className="setting-item">
                                <div className="setting-icon"><Shield size={20} /></div>
                                <div className="setting-info">
                                    <h4>Security & Privacy</h4>
                                    <p>Two-factor authentication enabled</p>
                                </div>
                                <button className="text-btn">Manage</button>
                            </div>
                        </div>
                    </div>

                    <div className="glass-card Danger Zone">
                        <h3 className="error-text">Danger Zone</h3>
                        <p className="section-desc">Irreversible account actions.</p>
                        <div className="danger-actions">
                            <button className="secondary-btn logout">
                                <LogOut size={18} /> Logout from all devices
                            </button>
                            <button className="outline-btn delete">Delete Account</button>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default Profile;
