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
                {/* Profile actions removed as requested */}
            </div>
        </header>
    );
};

export default Header;
