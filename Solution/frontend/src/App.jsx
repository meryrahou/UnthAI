import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import Sidebar from './components/Sidebar';
import Header from './components/Header';
import Dashboard from './pages/Dashboard';
import PostAnalysis from './pages/PostAnalysis';
import Trends from './pages/Trends';
import ActionCenter from './pages/ActionCenter';
import AIInsights from './pages/AIInsights';
import SocialConfig from './pages/SocialConfig';
import Profile from './pages/Profile';
import Auth from './pages/Auth';

import './App.css';

function App() {
  // Simple auth mockup
  const [isAuthenticated, setIsAuthenticated] = React.useState(false);

  if (!isAuthenticated) {
    return <Auth onLogin={() => setIsAuthenticated(true)} />;
  }

  return (
    <Router>
      <div className="layout">
        <Sidebar onLogout={() => setIsAuthenticated(false)} />
        <main className="main-content">
          <Header />
          <div className="content-container">
            <Routes>
              <Route path="/" element={<Dashboard />} />
              <Route path="/analysis" element={<PostAnalysis />} />
              <Route path="/trends" element={<Trends />} />
              <Route path="/actions" element={<ActionCenter />} />
              <Route path="/insights" element={<AIInsights />} />
              <Route path="/config" element={<SocialConfig />} />
              <Route path="/profile" element={<Profile />} />
              <Route path="*" element={<Navigate to="/" />} />
            </Routes>
          </div>
        </main>
      </div>
    </Router>
  );
}

export default App;
