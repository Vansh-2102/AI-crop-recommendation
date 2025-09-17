import React, { useState, useEffect } from 'react';
import { Cloud, Sun, CloudRain, Wind, Thermometer, Droplets } from 'lucide-react';
import { weatherAPI } from '../services/api';

const Weather = () => {
  const [weatherData, setWeatherData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [location, setLocation] = useState('Delhi');
  const [query, setQuery] = useState('Delhi');

  useEffect(() => {
    const fetchWeatherData = async () => {
      setLoading(true);
      try {
        const locationToUse = location?.trim() || 'Delhi';
        const res = await weatherAPI.getWeather(locationToUse);
        const payload = res.data?.weather;

        if (!payload) throw new Error('No weather data');

        const current = payload.current || {};
        const forecast = Array.isArray(payload.forecast) ? payload.forecast : [];

        // Group 3-hourly forecast into daily aggregates (high/low and a representative condition)
        const groups = {};
        forecast.forEach((f) => {
          const datePart = (f.date || '').split(' ')[0];
          if (!datePart) return;
          const temp = Number(
            (f.day_temperature ?? f.temperature ?? current.temperature) || 0
          );
          const lowTemp = Number(
            (f.night_temperature ?? temp - 7)
          );
          const cond = (f.conditions || '').toLowerCase();
          if (!groups[datePart]) {
            groups[datePart] = {
              high: -Infinity,
              low: Infinity,
              conditionCounts: {},
            };
          }
          groups[datePart].high = Math.max(groups[datePart].high, temp);
          groups[datePart].low = Math.min(groups[datePart].low, lowTemp);
          groups[datePart].conditionCounts[cond] =
            (groups[datePart].conditionCounts[cond] || 0) + 1;
        });

        const sortedDates = Object.keys(groups).sort();
        const daily = sortedDates.slice(0, 5).map((d) => {
          const g = groups[d];
          const condition = Object.entries(g.conditionCounts)
            .sort((a, b) => b[1] - a[1])[0]?.[0] || 'clouds';
          const icon = condition.includes('rain')
            ? 'rain'
            : condition.includes('sun') || condition.includes('clear')
            ? 'sun'
            : 'cloud';
          return {
            day: d,
            high: Math.round(g.high === -Infinity ? 0 : g.high),
            low: Math.round(g.low === Infinity ? 0 : g.low),
            condition: condition,
            icon,
          };
        });

        const mapped = {
          location: payload.location || locationToUse,
          current: {
            temperature: current.temperature,
            humidity: current.humidity,
            windSpeed: current.wind_speed ?? current.windSpeed,
            condition: current.conditions || current.condition || 'Unknown',
            icon: (current.conditions || '').toLowerCase().includes('rain')
              ? 'rain'
              : (current.conditions || '').toLowerCase().includes('sun') || (current.conditions || '').toLowerCase().includes('clear')
              ? 'sun'
              : 'cloud',
          },
          forecast: daily,
        };

        setWeatherData(mapped);
      } catch (error) {
        console.error('Failed to fetch weather data:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchWeatherData();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [location]);

  const onSubmit = (e) => {
    e.preventDefault();
    if (query && query.trim().length > 0) {
      setLocation(query.trim());
    }
  };

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
        <form onSubmit={onSubmit} style={{ marginTop: 12, display: 'flex', gap: 8 }}>
          <input
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Enter city or location (e.g., Delhi)"
            style={{ padding: 8, minWidth: 240 }}
          />
          <button type="submit" style={{ padding: '8px 14px' }}>Search</button>
        </form>
        {location && (
          <p style={{ marginTop: 8 }}><strong>Location:</strong> {location}</p>
        )}
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
