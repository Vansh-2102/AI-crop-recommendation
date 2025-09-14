import React, { useState, useEffect } from 'react';
import { useQuery } from 'react-query';
import { 
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
  LineChart, Line, PieChart, Pie, Cell
} from 'recharts';
import { 
  Droplet, Sun, TrendingUp, Leaf, AlertTriangle, 
  MapPin, Calendar, Thermometer, CloudRain
} from 'lucide-react';
import { weatherAPI, marketAPI, recommendationsAPI } from '../services/api';
import { useAuth } from '../contexts/AuthContext';
import toast from 'react-hot-toast';

const Dashboard = () => {
  const { user } = useAuth();
  const [location, setLocation] = useState(user?.location || 'Delhi, India');

  // Weather data
  const { data: weatherData, isLoading: weatherLoading } = useQuery(
    ['weather', location],
    () => weatherAPI.getWeather(location),
    { enabled: !!location }
  );

  // Agricultural conditions
  const { data: agConditions } = useQuery(
    ['agConditions', location],
    () => weatherAPI.getAgriculturalConditions(location),
    { enabled: !!location }
  );

  // Market data
  const { data: marketData } = useQuery(
    'marketData',
    () => marketAPI.getTrends()
  );

  // Recent recommendations
  const { data: recentRecommendations } = useQuery(
    'recentRecommendations',
    () => recommendationsAPI.getHistory(1, 5)
  );

  const weather = weatherData?.data?.weather;
  const conditions = agConditions?.data?.agricultural_conditions;

  // Chart data for market trends
  const marketChartData = marketData?.data?.top_performers?.gainers?.slice(0, 5).map(crop => ({
    name: crop.crop,
    price: crop.current_price,
    change: crop.price_change_percent
  })) || [];

  // Weather forecast data
  const forecastData = weather?.forecast?.slice(0, 7).map(day => ({
    date: new Date(day.date).toLocaleDateString('en-US', { weekday: 'short' }),
    temperature: day.day_temperature,
    precipitation: day.precipitation
  })) || [];

  const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042', '#8884D8'];

  if (weatherLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-green-500"></div>
      </div>
    );
  }

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Dashboard</h1>
          <p className="text-gray-600">Welcome back, {user?.name}!</p>
        </div>
        <div className="flex items-center space-x-2">
          <MapPin className="h-5 w-5 text-gray-500" />
          <span className="text-gray-700">{location}</span>
        </div>
      </div>

      {/* Weather Overview */}
      {weather && (
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Current Temperature</p>
                <p className="text-3xl font-bold text-gray-900">
                  {weather.current.temperature}°C
                </p>
              </div>
              <Thermometer className="h-8 w-8 text-blue-500" />
            </div>
          </div>

          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Humidity</p>
                <p className="text-3xl font-bold text-gray-900">
                  {weather.current.humidity}%
                </p>
              </div>
              <Droplet className="h-8 w-8 text-blue-500" />
            </div>
          </div>

          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Precipitation</p>
                <p className="text-3xl font-bold text-gray-900">
                  {weather.current.precipitation}mm
                </p>
              </div>
              <CloudRain className="h-8 w-8 text-blue-500" />
            </div>
          </div>

          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Conditions</p>
                <p className="text-lg font-bold text-gray-900">
                  {weather.current.conditions}
                </p>
              </div>
              <Sun className="h-8 w-8 text-yellow-500" />
            </div>
          </div>
        </div>
      )}

      {/* Agricultural Conditions */}
      {conditions && (
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-xl font-semibold text-gray-900 mb-4">Agricultural Conditions</h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="text-center">
              <div className="text-2xl font-bold text-green-600">
                {conditions.growing_degree_days}
              </div>
              <div className="text-sm text-gray-600">Growing Degree Days</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-blue-600">
                {conditions.soil_moisture_index}
              </div>
              <div className="text-sm text-gray-600">Soil Moisture Index</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-orange-600 capitalize">
                {conditions.growing_condition.replace('_', ' ')}
              </div>
              <div className="text-sm text-gray-600">Growing Condition</div>
            </div>
          </div>
        </div>
      )}

      {/* Charts Row */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Weather Forecast */}
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-xl font-semibold text-gray-900 mb-4">7-Day Weather Forecast</h2>
          <ResponsiveContainer width="100%" height={300}>
            <LineChart data={forecastData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="date" />
              <YAxis />
              <Tooltip />
              <Line 
                type="monotone" 
                dataKey="temperature" 
                stroke="#3B82F6" 
                strokeWidth={2}
                name="Temperature (°C)"
              />
              <Line 
                type="monotone" 
                dataKey="precipitation" 
                stroke="#10B981" 
                strokeWidth={2}
                name="Precipitation (mm)"
              />
            </LineChart>
          </ResponsiveContainer>
        </div>

        {/* Market Trends */}
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-xl font-semibold text-gray-900 mb-4">Top Performing Crops</h2>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={marketChartData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="name" />
              <YAxis />
              <Tooltip />
              <Bar dataKey="price" fill="#10B981" />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Recent Recommendations */}
      {recentRecommendations && (
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-xl font-semibold text-gray-900 mb-4">Recent Recommendations</h2>
          <div className="space-y-4">
            {recentRecommendations.data?.recommendations?.slice(0, 3).map((rec, index) => (
              <div key={index} className="border rounded-lg p-4">
                <div className="flex justify-between items-start">
                  <div>
                    <h3 className="font-medium text-gray-900">
                      {rec.location}
                    </h3>
                    <p className="text-sm text-gray-600">
                      {new Date(rec.created_at).toLocaleDateString()}
                    </p>
                  </div>
                  <div className="text-right">
                    <div className="text-lg font-bold text-green-600">
                      {rec.confidence_score}%
                    </div>
                    <div className="text-sm text-gray-600">Confidence</div>
                  </div>
                </div>
                {rec.recommendations?.slice(0, 2).map((rec_item, idx) => (
                  <div key={idx} className="mt-2 text-sm">
                    <span className="font-medium">{rec_item.crop}</span>
                    <span className="text-gray-600 ml-2">
                      (Score: {rec_item.suitability_score}%)
                    </span>
                  </div>
                ))}
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Weather Alerts */}
      {weather?.alerts && weather.alerts.length > 0 && (
        <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-6">
          <div className="flex items-center">
            <AlertTriangle className="h-6 w-6 text-yellow-600 mr-3" />
            <h3 className="text-lg font-semibold text-yellow-800">Weather Alerts</h3>
          </div>
          <div className="mt-3 space-y-2">
            {weather.alerts.map((alert, index) => (
              <div key={index} className="text-sm text-yellow-700">
                <strong>{alert.type.replace('_', ' ').toUpperCase()}:</strong> {alert.message}
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

export default Dashboard;
