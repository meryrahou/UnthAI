import React from 'react';
import { Search, Bell, UserCircle } from 'lucide-react';
import './Header.css';

const Header = () => {
    return (
        <header className="header">
            <div className="search-bar">
                <Search size={18} className="search-icon" />
                <input type="text" placeholder="Search comments or posts..." />
            </div>

            <div className="header-actions">
                <button className="icon-btn">
                    <Bell size={20} />
                    <span className="notification-dot"></span>
                </button>
                <div className="user-profile">
                    <div className="user-info">
                        <p className="user-name">Mery's Restaurant</p>
                        <p className="user-role">Owner</p>
                    </div>
                    <UserCircle size={32} />
                </div>
            </div>
        </header>
    );
};

export default Header;
