import React from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { 
  BarChart3, 
  Droplets, 
  Cloud, 
  ShoppingCart, 
  Lightbulb, 
  Camera,
  Mic,
  User
} from 'lucide-react';

const Dashboard = () => {
  const { user } = useAuth();

  const features = [
    {
      title: 'Soil Analysis',
      description: 'Analyze your soil composition and get recommendations',
      icon: <Droplets size={24} />,
      link: '/soil',
      color: 'bg-green-500'
    },
    {
      title: 'Weather Forecast',
      description: 'Get accurate weather predictions for your area',
      icon: <Cloud size={24} />,
      link: '/weather',
      color: 'bg-blue-500'
    },
    {
      title: 'Market Prices',
      description: 'Check current crop prices and market trends',
      icon: <ShoppingCart size={24} />,
      link: '/market',
      color: 'bg-yellow-500'
    },
    {
      title: 'Crop Recommendations',
      description: 'Get AI-powered crop suggestions for your farm',
      icon: <Lightbulb size={24} />,
      link: '/recommendations',
      color: 'bg-purple-500'
    },
    {
      title: 'Disease Detection',
      description: 'Identify plant diseases using image analysis',
      icon: <Camera size={24} />,
      link: '/disease',
      color: 'bg-red-500'
    },
    {
      title: 'Voice Assistant',
      description: 'Get help through voice commands',
      icon: <Mic size={24} />,
      link: '/voice',
      color: 'bg-indigo-500'
    }
  ];

  return (
    <div className="dashboard">
      <div className="dashboard-header">
        <h1>Welcome back, {user?.name || 'Farmer'}! 👋</h1>
        <p>Manage your farm with AI-powered insights</p>
      </div>

      <div className="dashboard-stats">
        <div className="stat-card">
          <div className="stat-icon">
            <BarChart3 size={24} />
          </div>
          <div className="stat-content">
            <h3>Farm Analytics</h3>
            <p>Track your farm's performance</p>
          </div>
        </div>
        
        <div className="stat-card">
          <div className="stat-icon">
            <User size={24} />
          </div>
          <div className="stat-content">
            <h3>Profile</h3>
            <p>Manage your account settings</p>
          </div>
        </div>
      </div>

      <div className="features-grid">
        <h2>Available Features</h2>
        <div className="grid">
          {features.map((feature, index) => (
            <Link key={index} to={feature.link} className="feature-card">
              <div className={`feature-icon ${feature.color}`}>
                {feature.icon}
              </div>
              <div className="feature-content">
                <h3>{feature.title}</h3>
                <p>{feature.description}</p>
              </div>
            </Link>
          ))}
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
