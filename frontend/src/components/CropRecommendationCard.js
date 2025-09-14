import React from 'react';
import { TrendingUp, DollarSign, Leaf, Star, MapPin, Calendar } from 'lucide-react';

const CropRecommendationCard = ({ recommendation, onSelect }) => {
  const {
    crop,
    suitability_score,
    confidence,
    estimated_profit,
    estimated_cost,
    profit_margin,
    factors,
    market_data,
    growing_requirements
  } = recommendation;

  const getScoreColor = (score) => {
    if (score >= 80) return 'text-green-600 bg-green-100';
    if (score >= 60) return 'text-yellow-600 bg-yellow-100';
    return 'text-red-600 bg-red-100';
  };

  const getConfidenceColor = (confidence) => {
    if (confidence >= 0.8) return 'text-green-600';
    if (confidence >= 0.6) return 'text-yellow-600';
    return 'text-red-600';
  };

  return (
    <div className="bg-white rounded-lg shadow-md hover:shadow-lg transition-shadow duration-200 p-6 border border-gray-200">
      {/* Header */}
      <div className="flex justify-between items-start mb-4">
        <div>
          <h3 className="text-xl font-semibold text-gray-900 capitalize">{crop}</h3>
          <div className="flex items-center mt-1">
            <MapPin className="h-4 w-4 text-gray-500 mr-1" />
            <span className="text-sm text-gray-600">Suitable for your location</span>
          </div>
        </div>
        <div className="text-right">
          <div className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getScoreColor(suitability_score)}`}>
            <Star className="h-3 w-3 mr-1" />
            {suitability_score}% Match
          </div>
          <div className={`text-sm mt-1 ${getConfidenceColor(confidence)}`}>
            {Math.round(confidence * 100)}% Confidence
          </div>
        </div>
      </div>

      {/* Financial Information */}
      <div className="grid grid-cols-2 gap-4 mb-4">
        <div className="bg-green-50 rounded-lg p-3">
          <div className="flex items-center">
            <DollarSign className="h-5 w-5 text-green-600 mr-2" />
            <div>
              <p className="text-sm font-medium text-green-800">Estimated Profit</p>
              <p className="text-lg font-bold text-green-900">₹{estimated_profit?.toLocaleString()}</p>
            </div>
          </div>
        </div>
        <div className="bg-blue-50 rounded-lg p-3">
          <div className="flex items-center">
            <TrendingUp className="h-5 w-5 text-blue-600 mr-2" />
            <div>
              <p className="text-sm font-medium text-blue-800">Profit Margin</p>
              <p className="text-lg font-bold text-blue-900">{profit_margin}%</p>
            </div>
          </div>
        </div>
      </div>

      {/* Growing Requirements */}
      <div className="mb-4">
        <h4 className="text-sm font-medium text-gray-900 mb-2">Growing Requirements</h4>
        <div className="grid grid-cols-2 gap-2 text-sm">
          <div className="flex justify-between">
            <span className="text-gray-600">pH Range:</span>
            <span className="font-medium">
              {growing_requirements?.optimal_ph?.[0]} - {growing_requirements?.optimal_ph?.[1]}
            </span>
          </div>
          <div className="flex justify-between">
            <span className="text-gray-600">Temperature:</span>
            <span className="font-medium">
              {growing_requirements?.optimal_temp?.[0]}°C - {growing_requirements?.optimal_temp?.[1]}°C
            </span>
          </div>
          <div className="flex justify-between">
            <span className="text-gray-600">Water:</span>
            <span className="font-medium capitalize">{growing_requirements?.water_requirement}</span>
          </div>
          <div className="flex justify-between">
            <span className="text-gray-600">Season:</span>
            <span className="font-medium capitalize">{growing_requirements?.season}</span>
          </div>
        </div>
      </div>

      {/* Key Factors */}
      <div className="mb-4">
        <h4 className="text-sm font-medium text-gray-900 mb-2">Why This Crop?</h4>
        <div className="space-y-1">
          {factors?.slice(0, 3).map((factor, index) => (
            <div key={index} className="flex items-center text-sm text-gray-600">
              <Leaf className="h-3 w-3 text-green-500 mr-2" />
              {factor}
            </div>
          ))}
        </div>
      </div>

      {/* Market Information */}
      {market_data && (
        <div className="mb-4 p-3 bg-gray-50 rounded-lg">
          <h4 className="text-sm font-medium text-gray-900 mb-2">Market Information</h4>
          <div className="grid grid-cols-2 gap-2 text-sm">
            <div className="flex justify-between">
              <span className="text-gray-600">Current Price:</span>
              <span className="font-medium">₹{market_data.current_price}/{market_data.unit}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-600">Demand:</span>
              <span className={`font-medium capitalize ${
                market_data.demand_level === 'high' ? 'text-green-600' :
                market_data.demand_level === 'medium' ? 'text-yellow-600' : 'text-red-600'
              }`}>
                {market_data.demand_level}
              </span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-600">Trend:</span>
              <span className={`font-medium capitalize ${
                market_data.market_trend === 'rising' ? 'text-green-600' :
                market_data.market_trend === 'falling' ? 'text-red-600' : 'text-gray-600'
              }`}>
                {market_data.market_trend}
              </span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-600">Change:</span>
              <span className={`font-medium ${
                market_data.price_change_percent > 0 ? 'text-green-600' : 'text-red-600'
              }`}>
                {market_data.price_change_percent > 0 ? '+' : ''}{market_data.price_change_percent}%
              </span>
            </div>
          </div>
        </div>
      )}

      {/* Action Buttons */}
      <div className="flex space-x-2">
        <button
          onClick={() => onSelect && onSelect(recommendation)}
          className="flex-1 bg-green-600 text-white px-4 py-2 rounded-md text-sm font-medium hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-green-500 focus:ring-offset-2 transition-colors"
        >
          Select This Crop
        </button>
        <button className="px-4 py-2 border border-gray-300 text-gray-700 rounded-md text-sm font-medium hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-green-500 focus:ring-offset-2 transition-colors">
          View Details
        </button>
      </div>

      {/* Recommendation Text */}
      <div className="mt-4 p-3 bg-blue-50 rounded-lg">
        <p className="text-sm text-blue-800">
          <strong>Recommendation:</strong> {recommendation.recommendation}
        </p>
      </div>
    </div>
  );
};

export default CropRecommendationCard;

