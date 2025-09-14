import React, { useState, useEffect } from 'react';
import { Cloud, Sun, CloudRain, Wind, Thermometer, Droplets } from 'lucide-react';

const Weather = () => {
  const [weatherData, setWeatherData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [location, setLocation] = useState('');

  useEffect(() => {
    // Simulate weather data fetch
    const fetchWeatherData = async () => {
      setLoading(true);
      try {
        await new Promise(resolve => setTimeout(resolve, 1000));
        
        const mockData = {
          location: 'Farm Location',
          current: {
            temperature: 28,
            humidity: 65,
            windSpeed: 12,
            condition: 'Partly Cloudy',
            icon: 'cloud'
          },
          forecast: [
            { day: 'Today', high: 30, low: 22, condition: 'Sunny', icon: 'sun' },
            { day: 'Tomorrow', high: 28, low: 20, condition: 'Cloudy', icon: 'cloud' },
            { day: 'Day 3', high: 25, low: 18, condition: 'Rainy', icon: 'rain' },
            { day: 'Day 4', high: 27, low: 19, condition: 'Partly Cloudy', icon: 'cloud' },
            { day: 'Day 5', high: 29, low: 21, condition: 'Sunny', icon: 'sun' }
          ]
        };
        
        setWeatherData(mockData);
      } catch (error) {
        console.error('Failed to fetch weather data:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchWeatherData();
  }, []);

  const getWeatherIcon = (icon) => {
    switch (icon) {
      case 'sun':
        return <Sun size={24} className="text-yellow-500" />;
      case 'cloud':
        return <Cloud size={24} className="text-gray-500" />;
      case 'rain':
        return <CloudRain size={24} className="text-blue-500" />;
      default:
        return <Cloud size={24} className="text-gray-500" />;
    }
  };

  if (loading) {
    return (
      <div className="weather">
        <div className="page-header">
          <h1>Weather Forecast</h1>
          <p>Loading weather data...</p>
        </div>
        <div className="loading-spinner">Loading...</div>
      </div>
    );
  }

  return (
    <div className="weather">
      <div className="page-header">
        <h1>Weather Forecast</h1>
        <p>Current weather conditions and 5-day forecast</p>
      </div>

      <div className="weather-container">
        <div className="current-weather">
          <h2>Current Conditions</h2>
          <div className="current-card">
            <div className="current-main">
              <div className="temperature">
                <Thermometer size={32} />
                <span className="temp-value">{weatherData.current.temperature}°C</span>
              </div>
              <div className="condition">
                {getWeatherIcon(weatherData.current.icon)}
                <span>{weatherData.current.condition}</span>
              </div>
            </div>
            
            <div className="current-details">
              <div className="detail-item">
                <Droplets size={20} />
                <span>Humidity: {weatherData.current.humidity}%</span>
              </div>
              <div className="detail-item">
                <Wind size={20} />
                <span>Wind: {weatherData.current.windSpeed} km/h</span>
              </div>
            </div>
          </div>
        </div>

        <div className="forecast-section">
          <h2>5-Day Forecast</h2>
          <div className="forecast-grid">
            {weatherData.forecast.map((day, index) => (
              <div key={index} className="forecast-card">
                <h3>{day.day}</h3>
                <div className="forecast-icon">
                  {getWeatherIcon(day.icon)}
                </div>
                <div className="forecast-temps">
                  <span className="high">{day.high}°</span>
                  <span className="low">{day.low}°</span>
                </div>
                <p className="forecast-condition">{day.condition}</p>
              </div>
            ))}
          </div>
        </div>

        <div className="farming-tips">
          <h2>Farming Tips</h2>
          <div className="tips-grid">
            <div className="tip-card">
              <h3>🌱 Planting</h3>
              <p>Good conditions for planting. Soil temperature is optimal.</p>
            </div>
            <div className="tip-card">
              <h3>💧 Irrigation</h3>
              <p>Moderate watering recommended. Check soil moisture levels.</p>
            </div>
            <div className="tip-card">
              <h3>🌾 Harvesting</h3>
              <p>Ideal weather for harvesting. Plan for dry conditions.</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Weather;
