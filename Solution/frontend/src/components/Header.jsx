import React, { useState, useEffect } from 'react';
import { Search, MapPin } from 'lucide-react';
import './Header.css';

const Header = () => {
    const [restaurantName, setRestaurantName] = useState('San Benito');

    useEffect(() => {
        const fetchUser = async () => {
            try {
                const response = await fetch('http://localhost:8001/api/user/me', {
                    headers: {
                        'Authorization': `Bearer ${localStorage.getItem('token')}`
                    }
                });
                if (response.ok) {
                    const data = await response.json();
                    setRestaurantName(data.restaurant_name);
                }
            } catch (err) {
                console.error("Error fetching user:", err);
            }
        };
        fetchUser();
    }, []);

    return (
        <header className="header">
            <div className="search-bar">
                <Search size={18} className="search-icon" />
                <input type="text" placeholder="Search comments or posts..." />
            </div>

            <div className="header-actions">
                <div className="restaurant-badge">
                    <div className="badge-icon">
                        <MapPin size={14} />
                    </div>
                    <div className="badge-text">
                        <span className="badge-label">Active Establishment</span>
                        <span className="badge-value">{restaurantName}</span>
                    </div>
                </div>
            </div>
        </header>
    );
};

export default Header;
