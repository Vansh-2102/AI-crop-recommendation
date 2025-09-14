import React, { useState } from 'react';
import { Lightbulb, CheckCircle, AlertCircle, Info } from 'lucide-react';

const Recommendations = () => {
  const [recommendations, setRecommendations] = useState([
    {
      id: 1,
      type: 'success',
      title: 'Optimal Planting Time',
      description: 'Based on current weather conditions, this is the perfect time to plant wheat in your region.',
      priority: 'high',
      category: 'Planting'
    },
    {
      id: 2,
      type: 'warning',
      title: 'Soil pH Adjustment Needed',
      description: 'Your soil pH is slightly acidic. Consider adding lime to improve soil conditions.',
      priority: 'medium',
      category: 'Soil Management'
    },
    {
      id: 3,
      type: 'info',
      title: 'Irrigation Schedule',
      description: 'Increase watering frequency during the current dry spell. Monitor soil moisture levels.',
      priority: 'high',
      category: 'Irrigation'
    },
    {
      id: 4,
      type: 'success',
      title: 'Pest Control Success',
      description: 'Your current pest management strategy is working well. Continue with the same approach.',
      priority: 'low',
      category: 'Pest Management'
    },
    {
      id: 5,
      type: 'warning',
      title: 'Fertilizer Application',
      description: 'Time to apply nitrogen fertilizer. Current soil analysis shows low nitrogen levels.',
      priority: 'high',
      category: 'Fertilization'
    }
  ]);

  const [filter, setFilter] = useState('all');

  const filteredRecommendations = recommendations.filter(rec => 
    filter === 'all' || rec.category === filter
  );

  const getIcon = (type) => {
    switch (type) {
      case 'success':
        return <CheckCircle size={20} className="text-green-500" />;
      case 'warning':
        return <AlertCircle size={20} className="text-yellow-500" />;
      case 'info':
        return <Info size={20} className="text-blue-500" />;
      default:
        return <Lightbulb size={20} className="text-gray-500" />;
    }
  };

  const getPriorityColor = (priority) => {
    switch (priority) {
      case 'high':
        return 'priority-high';
      case 'medium':
        return 'priority-medium';
      case 'low':
        return 'priority-low';
      default:
        return '';
    }
  };

  const categories = ['all', 'Planting', 'Soil Management', 'Irrigation', 'Pest Management', 'Fertilization'];

  return (
    <div className="recommendations">
      <div className="page-header">
        <h1>AI Recommendations</h1>
        <p>Personalized farming recommendations based on your data</p>
      </div>

      <div className="recommendations-container">
        <div className="filters-section">
          <h2>Filter by Category</h2>
          <div className="filter-buttons">
            {categories.map(category => (
              <button
                key={category}
                onClick={() => setFilter(category)}
                className={`filter-btn ${filter === category ? 'active' : ''}`}
              >
                {category === 'all' ? 'All' : category}
              </button>
            ))}
          </div>
        </div>

        <div className="recommendations-list">
          <h2>Your Recommendations</h2>
          <div className="recommendations-grid">
            {filteredRecommendations.map(rec => (
              <div key={rec.id} className={`recommendation-card ${rec.type}`}>
                <div className="recommendation-header">
                  <div className="recommendation-icon">
                    {getIcon(rec.type)}
                  </div>
                  <div className="recommendation-meta">
                    <span className={`priority ${getPriorityColor(rec.priority)}`}>
                      {rec.priority} priority
                    </span>
                    <span className="category">{rec.category}</span>
                  </div>
                </div>
                
                <div className="recommendation-content">
                  <h3>{rec.title}</h3>
                  <p>{rec.description}</p>
                </div>
                
                <div className="recommendation-actions">
                  <button className="action-btn primary">
                    Apply Recommendation
                  </button>
                  <button className="action-btn secondary">
                    Learn More
                  </button>
                </div>
              </div>
            ))}
          </div>
        </div>

        <div className="insights-section">
          <h2>Farm Insights</h2>
          <div className="insights-grid">
            <div className="insight-card">
              <h3>🌱 Growth Potential</h3>
              <p>Your farm shows excellent potential for wheat and corn cultivation this season.</p>
            </div>
            <div className="insight-card">
              <h3>💧 Water Efficiency</h3>
              <p>Current irrigation practices are 85% efficient. Room for improvement with smart watering.</p>
            </div>
            <div className="insight-card">
              <h3>🌾 Yield Prediction</h3>
              <p>Based on current conditions, expect 15% higher yield compared to last season.</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Recommendations;
