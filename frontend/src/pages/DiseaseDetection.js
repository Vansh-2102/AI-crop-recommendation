import React, { useState } from 'react';
import { Camera, Upload, AlertTriangle, CheckCircle, X } from 'lucide-react';

const DiseaseDetection = () => {
  const [selectedImage, setSelectedImage] = useState(null);
  const [analysisResult, setAnalysisResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [dragActive, setDragActive] = useState(false);

  const handleImageUpload = (file) => {
    if (file && file.type.startsWith('image/')) {
      setSelectedImage(file);
      setAnalysisResult(null);
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

    setLoading(true);
    try {
      // Simulate AI analysis
      await new Promise(resolve => setTimeout(resolve, 3000));
      
      const mockResult = {
        disease: 'Leaf Blight',
        confidence: 87,
        severity: 'Moderate',
        description: 'Leaf blight is a common fungal disease that affects plant leaves, causing brown spots and eventual leaf death.',
        treatment: [
          'Remove and destroy infected plant material',
          'Apply fungicide containing copper or chlorothalonil',
          'Improve air circulation around plants',
          'Avoid overhead watering'
        ],
        prevention: [
          'Plant disease-resistant varieties',
          'Maintain proper spacing between plants',
          'Water at the base of plants',
          'Rotate crops annually'
        ]
      };
      
      setAnalysisResult(mockResult);
    } catch (error) {
      console.error('Analysis failed:', error);
    } finally {
      setLoading(false);
    }
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
      </div>

      <div className="detection-container">
        <div className="upload-section">
          <h2>Upload Plant Image</h2>
          
          {!selectedImage ? (
            <div
              className={`upload-area ${dragActive ? 'drag-active' : ''}`}
              onDragEnter={handleDrag}
              onDragLeave={handleDrag}
              onDragOver={handleDrag}
              onDrop={handleDrop}
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
                />
                <button className="upload-btn">Choose File</button>
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
                disabled={loading}
                className="analyze-btn"
              >
                {loading ? 'Analyzing...' : 'Analyze Image'}
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
