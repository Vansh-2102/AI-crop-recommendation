import React, { useState } from 'react';
import { toast } from 'react-hot-toast';
import { Droplets, Upload, BarChart3 } from 'lucide-react';

const SoilAnalysis = () => {
  const [soilData, setSoilData] = useState({
    ph: '',
    nitrogen: '',
    phosphorus: '',
    potassium: '',
    moisture: '',
    temperature: ''
  });
  const [loading, setLoading] = useState(false);
  const [results, setResults] = useState(null);

  const handleChange = (e) => {
    setSoilData({
      ...soilData,
      [e.target.name]: e.target.value
    });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);

    try {
      // Simulate API call
      await new Promise(resolve => setTimeout(resolve, 2000));
      
      const mockResults = {
        soilType: 'Loamy Soil',
        fertility: 'High',
        recommendations: [
          'Add organic compost to improve soil structure',
          'Consider crop rotation with legumes',
          'Monitor pH levels regularly'
        ],
        suitableCrops: ['Wheat', 'Rice', 'Corn', 'Soybeans']
      };
      
      setResults(mockResults);
      toast.success('Soil analysis completed!');
    } catch (error) {
      toast.error('Analysis failed. Please try again.');
    } finally {
      setLoading(false);
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
            </div>

            <div className="recommendations">
              <h3>Recommendations</h3>
              <ul>
                {results.recommendations.map((rec, index) => (
                  <li key={index}>{rec}</li>
                ))}
              </ul>
            </div>

            <div className="suitable-crops">
              <h3>Recommended Crops</h3>
              <div className="crops-grid">
                {results.suitableCrops.map((crop, index) => (
                  <span key={index} className="crop-tag">
                    {crop}
                  </span>
                ))}
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default SoilAnalysis;
