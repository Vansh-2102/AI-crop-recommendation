import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:5000';

// Create axios instance
const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor to add auth token
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor for error handling
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('access_token');
      localStorage.removeItem('user');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

// Auth API
export const authAPI = {
  register: (userData) => api.post('/api/auth/register', userData),
  login: (credentials) => api.post('/api/auth/login', credentials),
  getProfile: () => api.get('/api/auth/profile'),
  updateProfile: (userData) => api.put('/api/auth/profile', userData),
  changePassword: (passwordData) => api.post('/api/auth/change-password', passwordData),
};

// Soil API
export const soilAPI = {
  getSoilData: (lat, lng) => api.get(`/api/soil/${lat}/${lng}`),
  getFarmSoilData: () => api.get('/api/soil/farms'),
  analyzeSoil: (soilData) => api.post('/api/soil/analyze', soilData),
};

// Weather API
export const weatherAPI = {
  getWeather: (location) => api.get(`/api/weather/${location}`),
  getForecast: (location, days = 7) => api.get(`/api/weather/forecast/${location}?days=${days}`),
  getAlerts: (location) => api.get(`/api/weather/alerts/${location}`),
  getAgriculturalConditions: (location) => api.get(`/api/weather/agricultural-conditions/${location}`),
};

// Market API
export const marketAPI = {
  getPrices: (params = {}) => api.get('/api/market/prices', { params }),
  getCropPrice: (crop) => api.get(`/api/market/prices/${crop}`),
  getTrends: () => api.get('/api/market/trends'),
  getRecommendations: (data) => api.post('/api/market/recommendations', data),
};

// Recommendations API
export const recommendationsAPI = {
  getCropRecommendations: (data) => api.post('/api/recommend/crops', data),
  getHistory: (page = 1, perPage = 10) => api.get(`/api/recommend/history?page=${page}&per_page=${perPage}`),
  optimizeRecommendations: (data) => api.post('/api/recommend/optimize', data),
};

// Disease Detection API
export const diseaseAPI = {
  detectDisease: (data) => api.post('/api/disease/detect', data),
  detectDiseaseBatch: (data) => api.post('/api/disease/detect-batch', data),
  getCropDiseases: (cropType) => api.get(`/api/disease/diseases/${cropType}`),
  getPreventionGuide: () => api.get('/api/disease/prevention-guide'),
};

// Translation API
export const translationAPI = {
  translate: (data) => api.post('/api/translate/translate', data),
  translateBatch: (data) => api.post('/api/translate/translate-batch', data),
  getLanguages: () => api.get('/api/translate/languages'),
  detectLanguage: (data) => api.post('/api/translate/detect-language', data),
  getAgriculturalTerms: (language = 'en') => api.get(`/api/translate/agricultural-terms?language=${language}`),
  translateRecommendations: (data) => api.post('/api/translate/translate-recommendations', data),
};

// Voice API
export const voiceAPI = {
  processQuery: (data) => api.post('/api/voice/query', data),
  processBatchQuery: (data) => api.post('/api/voice/query-batch', data),
  getIntents: () => api.get('/api/voice/intents'),
  startConversation: (data) => api.post('/api/voice/conversation', data),
  continueConversation: (sessionId, data) => api.post(`/api/voice/conversation/${sessionId}`, data),
};

// System API
export const systemAPI = {
  healthCheck: () => api.get('/api/health'),
};

export default api;
