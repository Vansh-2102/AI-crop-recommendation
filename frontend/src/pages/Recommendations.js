import React, { useState } from 'react';
import { Lightbulb, CheckCircle, AlertCircle, Info } from 'lucide-react';
import { recommendationsAPI } from '../services/api';

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
  const [form, setForm] = useState({
    location: 'Delhi',
    ph: 6.8,
    soil_type: 'loamy',
    moisture: 0.3,
    temperature: 26,
    farm_size: 1,
    budget: 10000,
  });
  const [cropResults, setCropResults] = useState([]);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState('');
  const [debugInfo, setDebugInfo] = useState({ lastCount: 0, lastTime: null });

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
        <div className="personalized-section">
          <h2>Get Personalized Crop Recommendations</h2>
          <form
            className="recommend-form"
            onSubmit={async (e) => {
              e.preventDefault();
              setSubmitting(true);
              setError('');
              try {
                const token = localStorage.getItem('access_token');
                if (!token) {
                  setError('Please log in to get crop recommendations.');
                  setSubmitting(false);
                  return;
                }
                const payload = {
                  location: form.location,
                  soil_data: {
                    ph: Number(form.ph),
                    soil_type: String(form.soil_type).toLowerCase(),
                    moisture: Number(form.moisture),
                  },
                  weather_data: {
                    temperature: Number(form.temperature),
                  },
                  farm_size: Number(form.farm_size),
                  budget: Number(form.budget),
                };
                // Prefer auto endpoint to reuse soil/weather market like Soil Analysis
                const res = await recommendationsAPI.getCropRecommendationsAuto(payload);
                const items = res.data?.recommendations || [];
                console.log('Recommendations response:', res.data);
                setCropResults(items);
                setDebugInfo({ lastCount: items.length, lastTime: new Date().toLocaleTimeString() });
                if (!items.length) setError('No recommendations found for the given inputs. Try adjusting pH or moisture.');
              } catch (err) {
                const status = err.response?.status;
                const backendMsg = err.response?.data?.error || err.message;
                const msg = status === 401
                  ? 'Please log in first to fetch recommendations.'
                  : backendMsg?.includes('timeout')
                    ? 'The server took too long to respond. Please try again in a few seconds.'
                    : `Failed to fetch recommendations${status ? ` (HTTP ${status})` : ''}: ${backendMsg}`;
                setError(msg);
              } finally {
                setSubmitting(false);
              }
            }}
          >
            <div className="recommend-form-row">
              <div className="form-group">
                <label htmlFor="location">Location</label>
                <input id="location" value={form.location} onChange={(e)=>setForm({...form, location:e.target.value})} placeholder="City or area" />
              </div>
              <div className="form-group">
                <label htmlFor="farm_size">Farm size (acres)</label>
                <input id="farm_size" type="number" step="0.1" value={form.farm_size} onChange={(e)=>setForm({...form, farm_size:e.target.value})} />
              </div>
              <div className="form-group">
                <label htmlFor="budget">Budget</label>
                <input id="budget" type="number" step="100" value={form.budget} onChange={(e)=>setForm({...form, budget:e.target.value})} />
              </div>
            </div>

            <div className="recommend-form-row">
              <div className="form-group">
                <label htmlFor="ph">Soil pH</label>
                <input id="ph" type="number" step="0.1" value={form.ph} onChange={(e)=>setForm({...form, ph:e.target.value})} />
              </div>
              <div className="form-group">
                <label htmlFor="soil_type">Soil type</label>
                <select id="soil_type" value={form.soil_type} onChange={(e)=>setForm({...form, soil_type:e.target.value})}>
                  <option value="loamy">Loamy</option>
                  <option value="clay">Clay</option>
                  <option value="sandy">Sandy</option>
                  <option value="silty">Silty</option>
                </select>
              </div>
              <div className="form-group">
                <label htmlFor="moisture">Moisture (0-1)</label>
                <input id="moisture" type="number" step="0.05" min="0" max="1" value={form.moisture} onChange={(e)=>setForm({...form, moisture:e.target.value})} />
              </div>
            </div>

            <div className="recommend-form-row">
              <div className="form-group">
                <label htmlFor="temperature">Temperature (°C)</label>
                <input id="temperature" type="number" step="0.5" value={form.temperature} onChange={(e)=>setForm({...form, temperature:e.target.value})} />
              </div>
              <div className="form-actions">
                <button type="submit" className="analyze-button" disabled={submitting}>
                  {submitting ? 'Analyzing…' : 'Recommend Crops'}
                </button>
              </div>
            </div>

            {error && <div className="error-message" style={{marginTop: '0.75rem'}}>{error}</div>}
            {!error && debugInfo.lastTime && (
              <div className="loading-text" style={{marginTop: '0.5rem'}}>
                Last fetch at {debugInfo.lastTime}: {debugInfo.lastCount} item(s)
              </div>
            )}
          </form>

          {cropResults.length > 0 && (
            <div className="recommendations-list" style={{marginTop: '1.5rem'}}>
              <h2>Recommended Crops</h2>
              <div className="recommendations-grid">
                {cropResults.map((rec, idx) => (
                  <div key={idx} className="crop-card">
                    <div className="crop-header">
                      <h4>{rec.crop}</h4>
                      <div className="crop-score">
                        <span className="suitability-score">{Math.round(rec.suitability_score)}%</span>
                        <span className="confidence-score">Confidence {Math.round(rec.confidence)}%</span>
                      </div>
                    </div>
                    <div className="crop-details">
                      <div className="crop-metrics">
                        <div className="metric"><span className="label">Est. Yield</span><span className="value">{rec.estimated_yield}</span></div>
                        <div className="metric"><span className="label">Est. Profit</span><span className="value profit">₹{rec.estimated_profit?.toLocaleString?.() || rec.estimated_profit}</span></div>
                        <div className="metric"><span className="label">Revenue</span><span className="value">₹{rec.estimated_revenue?.toLocaleString?.() || rec.estimated_revenue}</span></div>
                        <div className="metric"><span className="label">Cost</span><span className="value">₹{rec.estimated_cost?.toLocaleString?.() || rec.estimated_cost}</span></div>
                      </div>
                      <div className="crop-factors">
                        <h5>Why recommended</h5>
                        <ul>
                          {(rec.factors || []).slice(0,4).map((f,i)=> <li key={i}>{f}</li>)}
                        </ul>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>

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
