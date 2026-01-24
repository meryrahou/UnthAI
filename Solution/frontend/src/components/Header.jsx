import React, { useState, useEffect } from 'react';
import { Search, MapPin, Moon, Sun, Languages } from 'lucide-react';
import { useApp } from '../utils/AppContext';
import './Header.css';

const Header = () => {
    const { theme, toggleTheme, language, setLanguage, t, restaurantName } = useApp();

    return (
        <header className="header">
            <div className="search-bar">
                <Search size={18} className="search-icon" />
                <input type="text" placeholder={t('searchPlaceholder')} />
            </div>

            <div className="header-actions">
                <div className="toggle-group">
                    <button onClick={toggleTheme} className="icon-btn theme-toggle" title="Toggle Theme">
                        {theme === 'dark' ? <Sun size={20} /> : <Moon size={20} />}
                    </button>

                    <div className="lang-selector">
                        <Languages size={20} className="lang-icon" />
                        <select
                            value={language}
                            onChange={(e) => setLanguage(e.target.value)}
                            className="lang-select"
                        >
                            <option value="en">EN</option>
                            <option value="fr">FR</option>
                            <option value="ar">AR</option>
                        </select>
                    </div>
                </div>

                <div className="restaurant-badge">
                    <div className="badge-icon">
                        <MapPin size={14} />
                    </div>
                    <div className="badge-text">
                        <span className="badge-label">{t('activeEstablishment')}</span>
                        <span className="badge-value">{restaurantName}</span>
                    </div>
                </div>
            </div>
        </header>
    );
};

export default Header;
