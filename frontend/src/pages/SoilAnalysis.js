import React, { useState } from 'react';
import { toast } from 'react-hot-toast';
import { Droplets, Upload, BarChart3, Sprout } from 'lucide-react';
import { soilAPI, recommendationsAPI } from '../services/api';

const SoilAnalysis = () => {
  const [soilData, setSoilData] = useState({
    ph: '',
    nitrogen: '',
    phosphorus: '',
    potassium: '',
    moisture: '',
    temperature: '',
    clay: '',
    sand: '',
    silt: '',
    organic_matter: ''
  });
  const [loading, setLoading] = useState(false);
  const [results, setResults] = useState(null);
  const [cropRecommendations, setCropRecommendations] = useState(null);
  const [recommendationsLoading, setRecommendationsLoading] = useState(false);

  const handleChange = (e) => {
    setSoilData({
      ...soilData,
      [e.target.name]: e.target.value
    });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setCropRecommendations(null);

    try {
      // Build payload for backend analyze endpoint
      const payload = {
        soil_data: {
          ph: soilData.ph !== '' ? parseFloat(soilData.ph) : undefined,
          nitrogen: soilData.nitrogen !== '' ? parseFloat(soilData.nitrogen) / 1000 : undefined,
          phosphorus: soilData.phosphorus !== '' ? parseFloat(soilData.phosphorus) : undefined,
          potassium: soilData.potassium !== '' ? parseFloat(soilData.potassium) : undefined,
          moisture: soilData.moisture !== '' ? Math.min(1, Math.max(0, parseFloat(soilData.moisture) / 100)) : undefined,
          temperature: soilData.temperature !== '' ? parseFloat(soilData.temperature) : undefined,
          clay: soilData.clay !== '' ? parseFloat(soilData.clay) : undefined,
          sand: soilData.sand !== '' ? parseFloat(soilData.sand) : undefined,
          silt: soilData.silt !== '' ? parseFloat(soilData.silt) : undefined,
          organic_matter: soilData.organic_matter !== '' ? parseFloat(soilData.organic_matter) : undefined
        }
      };

      const { data } = await soilAPI.analyzeSoil(payload);

      // Map backend response to UI-friendly shape
      const analysis = data?.analysis || {};
      const summary = data?.summary || {};
      const ui = {
        soilType: analysis.soil_type || 'N/A',
        fertility: (analysis.fertility_level || 'medium').charAt(0).toUpperCase() + (analysis.fertility_level || 'medium').slice(1),
        recommendations: (analysis.recommendations || []).map(r => r.message || r.action || ''),
        suitableCrops: [],
        score: data?.soil_quality_score,
        overallStatus: summary.overall_status,
        drainage: analysis.drainage,
        texture: analysis.texture,
        nutrientBalance: analysis.nutrient_balance,
        organicMatterStatus: analysis.organic_matter_status,
        phStatus: analysis.ph_status
      };

      setResults(ui);
      toast.success('Soil analysis completed!');

      // Fetch crop recommendations based on soil data
      await fetchCropRecommendations(payload.soil_data, analysis);

    } catch (error) {
      console.error('Soil analysis failed:', error);
      toast.error('Analysis failed. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const fetchCropRecommendations = async (soilData, analysis) => {
    setRecommendationsLoading(true);
    
    try {
      const recommendationPayload = {
        location: 'Your Farm',
        soil_data: {
          ph: soilData.ph || 7.0,
          moisture: soilData.moisture || 0.3,
          organic_matter: soilData.organic_matter || 2.0,
          nitrogen: soilData.nitrogen || 0.2,
          phosphorus: soilData.phosphorus || 20,
          potassium: soilData.potassium || 150,
          soil_type: analysis.soil_type || 'loamy',
          clay: soilData.clay || 30,
          sand: soilData.sand || 40,
          silt: soilData.silt || 30
        },
        weather_data: {
          temperature: soilData.temperature || 25,
          humidity: 60
        },
        farm_size: 1,
        budget: 50000
      };

      const { data } = await recommendationsAPI.getCropRecommendations(recommendationPayload);
      
      setCropRecommendations(data.recommendations || []);
      toast.success('Crop recommendations generated!');
    } catch (error) {
      console.error('Failed to fetch crop recommendations:', error);
      toast.error('Failed to get crop recommendations');
    } finally {
      setRecommendationsLoading(false);
    }
  };

  return (
    <div className="soil-analysis">
      <div className="page-header">
        <h1>Soil Analysis</h1>
        <p>Analyze your soil composition and get recommendations</p>
      </div>

      <div className="analysis-container">
        <div className="input-section">
          <h2>Enter Soil Data</h2>
          <form onSubmit={handleSubmit} className="soil-form">
            <div className="form-row">
              <div className="form-group">
                <label htmlFor="ph">pH Level</label>
                <input
                  type="number"
                  id="ph"
                  name="ph"
                  value={soilData.ph}
                  onChange={handleChange}
                  step="0.1"
                  min="0"
                  max="14"
                  placeholder="6.5"
                />
              </div>
              
              <div className="form-group">
                <label htmlFor="nitrogen">Nitrogen (ppm)</label>
                <input
                  type="number"
                  id="nitrogen"
                  name="nitrogen"
                  value={soilData.nitrogen}
                  onChange={handleChange}
                  placeholder="50"
                />
              </div>
            </div>

            <div className="form-row">
              <div className="form-group">
                <label htmlFor="phosphorus">Phosphorus (ppm)</label>
                <input
                  type="number"
                  id="phosphorus"
                  name="phosphorus"
                  value={soilData.phosphorus}
                  onChange={handleChange}
                  placeholder="25"
                />
              </div>
              
              <div className="form-group">
                <label htmlFor="potassium">Potassium (ppm)</label>
                <input
                  type="number"
                  id="potassium"
                  name="potassium"
                  value={soilData.potassium}
                  onChange={handleChange}
                  placeholder="150"
                />
              </div>
            </div>

            <div className="form-row">
              <div className="form-group">
                <label htmlFor="moisture">Moisture (%)</label>
                <input
                  type="number"
                  id="moisture"
                  name="moisture"
                  value={soilData.moisture}
                  onChange={handleChange}
                  min="0"
                  max="100"
                  placeholder="60"
                />
              </div>
              
              <div className="form-group">
                <label htmlFor="temperature">Temperature (°C)</label>
                <input
                  type="number"
                  id="temperature"
                  name="temperature"
                  value={soilData.temperature}
                  onChange={handleChange}
                  placeholder="25"
                />
              </div>
            </div>

            <div className="form-row">
              <div className="form-group">
                <label htmlFor="clay">Clay (%)</label>
                <input
                  type="number"
                  id="clay"
                  name="clay"
                  value={soilData.clay}
                  onChange={handleChange}
                  min="0"
                  max="100"
                  placeholder="30"
                />
              </div>
              
              <div className="form-group">
                <label htmlFor="sand">Sand (%)</label>
                <input
                  type="number"
                  id="sand"
                  name="sand"
                  value={soilData.sand}
                  onChange={handleChange}
                  min="0"
                  max="100"
                  placeholder="40"
                />
              </div>
            </div>

            <div className="form-row">
              <div className="form-group">
                <label htmlFor="silt">Silt (%)</label>
                <input
                  type="number"
                  id="silt"
                  name="silt"
                  value={soilData.silt}
                  onChange={handleChange}
                  min="0"
                  max="100"
                  placeholder="30"
                />
              </div>
              
              <div className="form-group">
                <label htmlFor="organic_matter">Organic Matter (%)</label>
                <input
                  type="number"
                  id="organic_matter"
                  name="organic_matter"
                  value={soilData.organic_matter}
                  onChange={handleChange}
                  step="0.1"
                  min="0"
                  max="100"
                  placeholder="2.0"
                />
              </div>
            </div>

            <button
              type="submit"
              disabled={loading}
              className="analyze-button"
            >
              {loading ? 'Analyzing...' : 'Analyze Soil'}
            </button>
          </form>
        </div>

        {results && (
          <div className="results-section">
            <h2>Analysis Results</h2>
            <div className="results-grid">
              <div className="result-card">
                <h3>Soil Type</h3>
                <p>{results.soilType}</p>
              </div>
              
              <div className="result-card">
                <h3>Fertility Level</h3>
                <p className={`fertility ${results.fertility.toLowerCase()}`}>
                  {results.fertility}
                </p>
              </div>
              {typeof results.score === 'number' && (
                <div className="result-card">
                  <h3>Soil Quality Score</h3>
                  <p>{results.score}/100</p>
                </div>
              )}
              {results.overallStatus && (
                <div className="result-card">
                  <h3>Overall Status</h3>
                  <p>{results.overallStatus}</p>
                </div>
              )}
            </div>

            <div className="recommendations">
              <h3>Recommendations</h3>
              <ul>
                {results.recommendations.map((rec, index) => (
                  <li key={index}>{rec}</li>
                ))}
              </ul>
            </div>

            {cropRecommendations && cropRecommendations.length > 0 && (
              <div className="crop-recommendations">
                <h3>
                  <Sprout className="icon" />
                  Recommended Crops
                  {recommendationsLoading && <span className="loading-text"> (Loading...)</span>}
                </h3>
                <div className="recommendations-grid">
                  {cropRecommendations.slice(0, 6).map((crop, index) => (
                    <div key={index} className="crop-card">
                      <div className="crop-header">
                        <h4>{crop.crop.charAt(0).toUpperCase() + crop.crop.slice(1)}</h4>
                        <div className="crop-score">
                          <span className="suitability-score">{crop.suitability_score}%</span>
                          <span className="confidence-score">Confidence: {crop.confidence}%</span>
                        </div>
                      </div>
                      <div className="crop-details">
                        <div className="crop-metrics">
                          <div className="metric">
                            <span className="label">Estimated Yield:</span>
                            <span className="value">{crop.estimated_yield?.toLocaleString()} kg</span>
                          </div>
                          <div className="metric">
                            <span className="label">Estimated Cost:</span>
                            <span className="value">₹{crop.estimated_cost?.toLocaleString()}</span>
                          </div>
                          <div className="metric">
                            <span className="label">Estimated Profit:</span>
                            <span className="value profit">₹{crop.estimated_profit?.toLocaleString()}</span>
                          </div>
                          <div className="metric">
                            <span className="label">Profit Margin:</span>
                            <span className="value">{crop.profit_margin}%</span>
                          </div>
                        </div>
                        <div className="crop-factors">
                          <h5>Why this crop?</h5>
                          <ul>
                            {crop.factors?.slice(0, 3).map((factor, idx) => (
                              <li key={idx}>{factor}</li>
                            ))}
                          </ul>
                        </div>
                        <div className="crop-requirements">
                          <h5>Growing Requirements</h5>
                          <div className="requirements-grid">
                            <div className="req-item">
                              <span className="req-label">pH Range:</span>
                              <span className="req-value">{crop.growing_requirements?.optimal_ph?.[0]} - {crop.growing_requirements?.optimal_ph?.[1]}</span>
                            </div>
                            <div className="req-item">
                              <span className="req-label">Temperature:</span>
                              <span className="req-value">{crop.growing_requirements?.optimal_temp?.[0]}°C - {crop.growing_requirements?.optimal_temp?.[1]}°C</span>
                            </div>
                            <div className="req-item">
                              <span className="req-label">Water:</span>
                              <span className="req-value">{crop.growing_requirements?.water_requirement}</span>
                            </div>
                            <div className="req-item">
                              <span className="req-label">Soil Type:</span>
                              <span className="req-value">{crop.growing_requirements?.soil_type?.join(', ')}</span>
                            </div>
                          </div>
              </div>
            </div>
                    </div>
                  ))}
                </div>
                {cropRecommendations.length > 6 && (
                  <p className="more-crops">+ {cropRecommendations.length - 6} more crops available</p>
                )}
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
};

export default SoilAnalysis;
