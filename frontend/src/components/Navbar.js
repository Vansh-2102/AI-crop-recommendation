import React from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { useLanguage } from '../contexts/LanguageContext';
import { LogOut, User, Settings } from 'lucide-react';

const Navbar = () => {
  const { user, logout } = useAuth();
  const { language, changeLanguage } = useLanguage();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  return (
    <nav className="navbar">
      <div className="navbar-container">
        <Link to="/dashboard" className="navbar-brand">
          🌱 Crop AI
        </Link>
        
        <div className="navbar-menu">
          {user && (
            <>
              <Link to="/dashboard" className="navbar-link">
                Dashboard
              </Link>
              <Link to="/soil" className="navbar-link">
                Soil Analysis
              </Link>
              <Link to="/weather" className="navbar-link">
                Weather
              </Link>
              <Link to="/market" className="navbar-link">
                Market
              </Link>
              <Link to="/recommendations" className="navbar-link">
                Recommendations
              </Link>
              <Link to="/disease" className="navbar-link">
                Disease Detection
              </Link>
              <Link to="/voice" className="navbar-link">
                Voice Assistant
              </Link>
            </>
          )}
        </div>

        <div className="navbar-actions">
          <select 
            value={language} 
            onChange={(e) => changeLanguage(e.target.value)}
            className="language-selector"
          >
            <option value="en">English</option>
            <option value="hi">हिन्दी</option>
            <option value="es">Español</option>
          </select>
          
          {user ? (
            <div className="user-menu">
              <Link to="/profile" className="user-link">
                <User size={20} />
                {user.name || user.email}
              </Link>
              <button onClick={handleLogout} className="logout-btn">
                <LogOut size={20} />
                Logout
              </button>
            </div>
          ) : (
            <Link to="/login" className="login-link">
              Login
            </Link>
          )}
        </div>
      </div>
    </nav>
  );
};

export default Navbar;
