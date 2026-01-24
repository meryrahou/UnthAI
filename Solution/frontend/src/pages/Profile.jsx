import React from 'react';
import { User, Mail, Building2, Bell, Shield, LogOut } from 'lucide-react';
import { useApp } from '../utils/AppContext';
import './Profile.css';

const Profile = () => {
    const { t, restaurantName } = useApp();
    return (
        <div className="profile-page animate-fade-in">
            <div className="page-header">
                <h1>{t('accountProfile')}</h1>
                <p className="subtitle">{t('profileSubtitle')}</p>
            </div>

            <div className="profile-content">
                <div className="profile-sidebar">
                    <div className="glass-card user-main-card">
                        <div className="avatar-large">{restaurantName[0]}</div>
                        <h2>{restaurantName}</h2>
                        <p className="user-email">{restaurantName.toLowerCase().replace(' ', '.')}@unthai.dz</p>
                        <button className="edit-btn">{t('editProfile')}</button>
                    </div>

                    <div className="glass-card account-stats">
                        <div className="a-stat">
                            <span className="label">{t('plan')}</span>
                            <span className="value">Enterprise</span>
                        </div>
                        <div className="a-stat">
                            <span className="label">{t('analyzed')}</span>
                            <span className="value">12.5k {t('comments')}</span>
                        </div>
                    </div>
                </div>

                <div className="profile-main">
                    <div className="glass-card settings-section">
                        <h3>{t('generalSettings')}</h3>
                        <div className="settings-list">
                            <div className="setting-item">
                                <div className="setting-icon"><Building2 size={20} /></div>
                                <div className="setting-info">
                                    <h4>{t('restaurantDetails')}</h4>
                                    <p>Mery's Grill & Bar, Algiers Center</p>
                                </div>
                                <button className="text-btn">{t('manage')}</button>
                            </div>
                            <div className="setting-item">
                                <div className="setting-icon"><Bell size={20} /></div>
                                <div className="setting-info">
                                    <h4>{t('notificationPrefs')}</h4>
                                    <p>Email alerts for negative sentiment spikes</p>
                                </div>
                                <button className="text-btn">{t('configure')}</button>
                            </div>
                            <div className="setting-item">
                                <div className="setting-icon"><Shield size={20} /></div>
                                <div className="setting-info">
                                    <h4>{t('securityPrivacy')}</h4>
                                    <p>Two-factor authentication enabled</p>
                                </div>
                                <button className="text-btn">{t('manage')}</button>
                            </div>
                        </div>
                    </div>

                    <div className="glass-card danger-zone">
                        <h3 className="error-text">{t('dangerZone')}</h3>
                        <p className="section-desc">{t('dangerZoneDesc')}</p>
                        <div className="danger-actions">
                            <button className="secondary-btn logout" onClick={() => {
                                localStorage.removeItem('token');
                                window.location.href = '/auth';
                            }}>
                                <LogOut size={18} /> {t('logout')}
                            </button>
                            <button className="outline-btn delete">{t('deleteAccount')}</button>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default Profile;
