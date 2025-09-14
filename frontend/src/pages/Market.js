import React, { useState, useEffect } from 'react';
import { TrendingUp, TrendingDown, DollarSign, BarChart3 } from 'lucide-react';

const Market = () => {
  const [marketData, setMarketData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [selectedCrop, setSelectedCrop] = useState('wheat');

  useEffect(() => {
    const fetchMarketData = async () => {
      setLoading(true);
      try {
        await new Promise(resolve => setTimeout(resolve, 1000));
        
        const mockData = {
          crops: [
            {
              name: 'Wheat',
              currentPrice: 2500,
              previousPrice: 2400,
              change: 4.17,
              unit: 'per quintal',
              trend: 'up'
            },
            {
              name: 'Rice',
              currentPrice: 3200,
              previousPrice: 3300,
              change: -3.03,
              unit: 'per quintal',
              trend: 'down'
            },
            {
              name: 'Corn',
              currentPrice: 1800,
              previousPrice: 1750,
              change: 2.86,
              unit: 'per quintal',
              trend: 'up'
            },
            {
              name: 'Soybeans',
              currentPrice: 4200,
              previousPrice: 4100,
              change: 2.44,
              unit: 'per quintal',
              trend: 'up'
            },
            {
              name: 'Cotton',
              currentPrice: 6500,
              previousPrice: 6600,
              change: -1.52,
              unit: 'per quintal',
              trend: 'down'
            },
            {
              name: 'Sugarcane',
              currentPrice: 320,
              previousPrice: 315,
              change: 1.59,
              unit: 'per quintal',
              trend: 'up'
            }
          ],
          marketTrends: [
            { month: 'Jan', price: 2400 },
            { month: 'Feb', price: 2450 },
            { month: 'Mar', price: 2500 },
            { month: 'Apr', price: 2480 },
            { month: 'May', price: 2520 },
            { month: 'Jun', price: 2500 }
          ]
        };
        
        setMarketData(mockData);
      } catch (error) {
        console.error('Failed to fetch market data:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchMarketData();
  }, []);

  if (loading) {
    return (
      <div className="market">
        <div className="page-header">
          <h1>Market Prices</h1>
          <p>Loading market data...</p>
        </div>
        <div className="loading-spinner">Loading...</div>
      </div>
    );
  }

  return (
    <div className="market">
      <div className="page-header">
        <h1>Market Prices</h1>
        <p>Current crop prices and market trends</p>
      </div>

      <div className="market-container">
        <div className="crop-prices">
          <h2>Current Crop Prices</h2>
          <div className="prices-grid">
            {marketData.crops.map((crop, index) => (
              <div key={index} className="price-card">
                <div className="crop-header">
                  <h3>{crop.name}</h3>
                  <div className={`trend ${crop.trend}`}>
                    {crop.trend === 'up' ? (
                      <TrendingUp size={20} />
                    ) : (
                      <TrendingDown size={20} />
                    )}
                    <span>{crop.change > 0 ? '+' : ''}{crop.change}%</span>
                  </div>
                </div>
                
                <div className="price-info">
                  <div className="current-price">
                    <DollarSign size={24} />
                    <span className="price-value">{crop.currentPrice}</span>
                    <span className="price-unit">₹{crop.unit}</span>
                  </div>
                  
                  <div className="price-change">
                    <span className="previous-price">
                      Previous: ₹{crop.previousPrice}
                    </span>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>

        <div className="market-analysis">
          <h2>Market Analysis</h2>
          <div className="analysis-cards">
            <div className="analysis-card">
              <h3>Best Selling Crops</h3>
              <div className="crop-list">
                <div className="crop-item">
                  <span>Wheat</span>
                  <span className="trend-up">+4.17%</span>
                </div>
                <div className="crop-item">
                  <span>Corn</span>
                  <span className="trend-up">+2.86%</span>
                </div>
                <div className="crop-item">
                  <span>Soybeans</span>
                  <span className="trend-up">+2.44%</span>
                </div>
              </div>
            </div>

            <div className="analysis-card">
              <h3>Market Insights</h3>
              <ul className="insights-list">
                <li>Wheat prices showing strong upward trend</li>
                <li>Rice market experiencing slight decline</li>
                <li>Corn demand increasing in feed industry</li>
                <li>Cotton prices stabilizing after recent drop</li>
              </ul>
            </div>
          </div>
        </div>

        <div className="trading-tips">
          <h2>Trading Tips</h2>
          <div className="tips-grid">
            <div className="tip-card">
              <h3>📈 Best Time to Sell</h3>
              <p>Wheat and Corn are at peak prices. Consider selling now.</p>
            </div>
            <div className="tip-card">
              <h3>📉 Wait and Watch</h3>
              <p>Rice prices are declining. Hold your stock for better rates.</p>
            </div>
            <div className="tip-card">
              <h3>🌾 Storage Advice</h3>
              <p>Proper storage can help you wait for better market conditions.</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Market;
