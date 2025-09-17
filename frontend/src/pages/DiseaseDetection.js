import React, { useState } from 'react';
import { Camera, Upload, AlertTriangle, CheckCircle, X } from 'lucide-react';
import { diseaseAPI } from '../services/api';

const DiseaseDetection = () => {
  const [selectedImage, setSelectedImage] = useState(null);
  const [analysisResult, setAnalysisResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [dragActive, setDragActive] = useState(false);
  const [cropType, setCropType] = useState('tomato');
  const [isLoggedIn, setIsLoggedIn] = useState(false);

  // Check login status on component mount
  React.useEffect(() => {
    const token = localStorage.getItem('access_token');
    setIsLoggedIn(!!token);
  }, []);

  const handleImageUpload = (file) => {
    console.log('File selected:', file);
    console.log('File type:', file.type);
    console.log('File size:', file.size);
    
    if (file && file.type.startsWith('image/')) {
      setSelectedImage(file);
      setAnalysisResult(null);
      console.log('Image uploaded successfully');
    } else {
      console.error('Invalid file type. Please select an image file.');
      alert('Please select a valid image file.');
    }
  };

  const handleDrag = (e) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setDragActive(true);
    } else if (e.type === 'dragleave') {
      setDragActive(false);
    }
  };

  const handleDrop = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      handleImageUpload(e.dataTransfer.files[0]);
    }
  };

  const handleFileInput = (e) => {
    if (e.target.files && e.target.files[0]) {
      handleImageUpload(e.target.files[0]);
    }
  };

  const analyzeImage = async () => {
    if (!selectedImage) return;
    
    // Check if user is logged in
    const token = localStorage.getItem('access_token');
    if (!token) {
      alert('Please log in to use disease detection.');
      return;
    }

    setLoading(true);
    try {
      console.log('Starting image analysis...');
      console.log('Crop type:', cropType);
      console.log('Selected image:', selectedImage.name);
      
      // Convert image to base64
      const base64Image = await convertToBase64(selectedImage);
      console.log('Image converted to base64, length:', base64Image.length);
      
      // Call the backend API
      console.log('Calling backend API...');
      const response = await diseaseAPI.detectDisease({
        image_data: base64Image,
        crop_type: cropType,
        location: 'User Location'
      });
      
      console.log('API response:', response.data);
      
      if (response.data && response.data.detection_result) {
        const result = response.data.detection_result;
        setAnalysisResult({
          disease: result.name,
          confidence: Math.round(result.confidence * 100),
          severity: result.detected_severity || result.severity_levels?.[0] || 'Unknown',
          description: result.symptoms ? result.symptoms.join('. ') : 'Disease detected in plant.',
          treatment: result.treatment ? [result.treatment] : ['Consult agricultural expert'],
          prevention: result.prevention ? [result.prevention] : ['Maintain good growing conditions'],
          image_analysis: result.image_analysis || {}
        });
      } else {
        throw new Error('Invalid response from server');
      }
    } catch (error) {
      console.error('Analysis failed:', error);
      
      let errorMessage = 'Unable to analyze the image. Please try again.';
      
      if (error.response?.status === 401) {
        errorMessage = 'Please log in to use disease detection.';
      } else if (error.response?.status === 400) {
        errorMessage = 'Invalid image or crop type. Please check your selection.';
      } else if (error.response?.status >= 500) {
        errorMessage = 'Server error. Please try again later.';
      } else if (error.message) {
        errorMessage = error.message;
      }
      
      // Fallback to mock data if API fails
      const mockResult = {
        disease: 'Analysis Failed',
        confidence: 0,
        severity: 'Unknown',
        description: errorMessage,
        treatment: ['Please check your login status and try again'],
        prevention: ['Ensure you are logged in and have a valid image']
      };
      setAnalysisResult(mockResult);
    } finally {
      setLoading(false);
    }
  };

  const convertToBase64 = (file) => {
    return new Promise((resolve, reject) => {
      const reader = new FileReader();
      reader.readAsDataURL(file);
      reader.onload = () => {
        // Remove the data:image/jpeg;base64, prefix
        const base64 = reader.result.split(',')[1];
        resolve(base64);
      };
      reader.onerror = error => reject(error);
    });
  };

  const clearImage = () => {
    setSelectedImage(null);
    setAnalysisResult(null);
  };

  return (
    <div className="disease-detection">
      <div className="page-header">
        <h1>Disease Detection</h1>
        <p>Upload an image of your plant to detect diseases using AI</p>
        {!isLoggedIn && (
          <div className="login-warning">
            <AlertTriangle size={20} />
            <span>Please log in to use disease detection features.</span>
          </div>
        )}
      </div>

      <div className="detection-container">
        <div className="upload-section">
          <h2>Upload Plant Image</h2>
          
          <div className="crop-selector">
            <label htmlFor="crop-type">Select Crop Type:</label>
            <select 
              id="crop-type" 
              value={cropType} 
              onChange={(e) => setCropType(e.target.value)}
              className="crop-select"
            >
              <option value="tomato">Tomato</option>
              <option value="apple">Apple</option>
              <option value="cherry">Cherry</option>
              <option value="corn">Corn</option>
              <option value="grape">Grape</option>
              <option value="orange">Orange</option>
              <option value="peach">Peach</option>
              <option value="bell_pepper">Bell Pepper</option>
              <option value="potato">Potato</option>
              <option value="raspberry">Raspberry</option>
              <option value="soybean">Soybean</option>
              <option value="squash">Squash</option>
              <option value="strawberry">Strawberry</option>
              <option value="wheat">Wheat</option>
              <option value="rice">Rice</option>
            </select>
          </div>
          
          {!selectedImage ? (
            <div
              className={`upload-area ${dragActive ? 'drag-active' : ''}`}
              onDragEnter={handleDrag}
              onDragLeave={handleDrag}
              onDragOver={handleDrag}
              onDrop={handleDrop}
              onClick={() => document.getElementById('file-input').click()}
            >
              <div className="upload-content">
                <Camera size={48} className="upload-icon" />
                <h3>Drag & Drop or Click to Upload</h3>
                <p>Upload an image of your plant leaves, stems, or fruits</p>
                <input
                  type="file"
                  accept="image/*"
                  onChange={handleFileInput}
                  className="file-input"
                  id="file-input"
                />
                <label htmlFor="file-input" className="upload-btn">Choose File</label>
              </div>
            </div>
          ) : (
            <div className="image-preview">
              <div className="preview-header">
                <h3>Selected Image</h3>
                <button onClick={clearImage} className="clear-btn">
                  <X size={20} />
                </button>
              </div>
              <div className="preview-image">
                <img
                  src={URL.createObjectURL(selectedImage)}
                  alt="Plant preview"
                />
              </div>
              <button
                onClick={analyzeImage}
                disabled={loading || !isLoggedIn}
                className="analyze-btn"
              >
                {loading ? 'Analyzing...' : !isLoggedIn ? 'Please Log In' : 'Analyze Image'}
              </button>
            </div>
          )}
        </div>

        {analysisResult && (
          <div className="results-section">
            <h2>Analysis Results</h2>
            <div className="result-card">
              <div className="result-header">
                <div className="disease-info">
                  <h3>{analysisResult.disease}</h3>
                  <div className="confidence">
                    <span>Confidence: {analysisResult.confidence}%</span>
                  </div>
                </div>
                <div className={`severity ${analysisResult.severity.toLowerCase()}`}>
                  {analysisResult.severity}
                </div>
              </div>
              
              <div className="result-description">
                <p>{analysisResult.description}</p>
              </div>

              <div className="treatment-section">
                <h4>Treatment Recommendations</h4>
                <ul>
                  {analysisResult.treatment.map((item, index) => (
                    <li key={index}>{item}</li>
                  ))}
                </ul>
              </div>

              <div className="prevention-section">
                <h4>Prevention Tips</h4>
                <ul>
                  {analysisResult.prevention.map((item, index) => (
                    <li key={index}>{item}</li>
                  ))}
                </ul>
              </div>
            </div>
          </div>
        )}

        <div className="tips-section">
          <h2>Tips for Better Detection</h2>
          <div className="tips-grid">
            <div className="tip-card">
              <h3>📸 Image Quality</h3>
              <p>Use clear, well-lit images with good contrast for better accuracy.</p>
            </div>
            <div className="tip-card">
              <h3>🌿 Focus on Affected Areas</h3>
              <p>Capture the diseased parts of the plant clearly in the image.</p>
            </div>
            <div className="tip-card">
              <h3>🔍 Multiple Angles</h3>
              <p>Take photos from different angles to get a complete view.</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default DiseaseDetection;
