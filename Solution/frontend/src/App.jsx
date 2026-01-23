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
import Processing from './pages/Processing';
import { AppProvider } from './utils/AppContext';

import './App.css';

function App() {
  const [isAuthenticated, setIsAuthenticated] = React.useState(!!localStorage.getItem('token'));

  const handleLogin = () => {
    setIsAuthenticated(true);
  };

  const handleLogout = () => {
    localStorage.removeItem('token');
    setIsAuthenticated(false);
  };

  return (
    <AppProvider>
      <Router>
        {!isAuthenticated ? (
          <Routes>
            <Route path="/login" element={<Auth onLogin={handleLogin} />} />
            <Route path="*" element={<Navigate to="/login" replace />} />
          </Routes>
        ) : (
          <Routes>
            <Route path="/login" element={<Navigate to="/processing" replace />} />
            <Route path="/processing" element={<Processing />} />
            <Route path="/*" element={
              <div className="layout">
                <Sidebar onLogout={handleLogout} />
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
                      <Route path="*" element={<Navigate to="/" replace />} />
                    </Routes>
                  </div>
                </main>
              </div>
            } />
          </Routes>
        )}
      </Router>
    </AppProvider>
  );
}

export default App;
