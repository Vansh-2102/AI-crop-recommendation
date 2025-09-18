import React, { useState, useEffect } from 'react';
import { Mic, MicOff, Volume2, VolumeX, MessageSquare } from 'lucide-react';
import axios from 'axios';

const VoiceAssistant = () => {
  const [isListening, setIsListening] = useState(false);
  const [isSpeaking, setIsSpeaking] = useState(false);
  const [transcript, setTranscript] = useState('');
  const [response, setResponse] = useState('');
  const [conversation, setConversation] = useState([]);
  const [isSupported, setIsSupported] = useState(false);
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    // Check if speech recognition is supported
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    setIsSupported(!!SpeechRecognition);
    
    // Check if user is logged in
    const token = localStorage.getItem('access_token');
    setIsLoggedIn(!!token);
  }, []);

  const startListening = () => {
    if (!isSupported) {
      alert('Speech recognition is not supported in this browser');
      return;
    }

    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    const recognition = new SpeechRecognition();
    
    recognition.continuous = false;
    recognition.interimResults = false;
    recognition.lang = 'en-US';

    recognition.onstart = () => {
      setIsListening(true);
    };

    recognition.onresult = (event) => {
      const transcript = event.results[0][0].transcript;
      setTranscript(transcript);
      handleVoiceCommand(transcript);
    };

    recognition.onerror = (event) => {
      console.error('Speech recognition error:', event.error);
      setIsListening(false);
    };

    recognition.onend = () => {
      setIsListening(false);
    };

    recognition.start();
  };

  const stopListening = () => {
    setIsListening(false);
  };

  const handleVoiceCommand = async (command) => {
    if (!isLoggedIn) {
      alert('Please log in to use the Voice Assistant');
      return;
    }

    const userMessage = { type: 'user', text: command, timestamp: new Date() };
    setConversation(prev => [...prev, userMessage]);

    setLoading(true);
    try {
      // Call the backend voice API
      const token = localStorage.getItem('access_token');
      const response = await axios.post('http://localhost:5000/api/voice/query', {
        query: command,
        location: 'User Location',
        language: 'en'
      }, {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });

      const aiResponse = response.data.response_text;
      const assistantMessage = { 
        type: 'assistant', 
        text: aiResponse, 
        timestamp: new Date(),
        intent: response.data.detected_intent,
        confidence: response.data.confidence
      };
      setConversation(prev => [...prev, assistantMessage]);
      
      setResponse(aiResponse);
      speakText(aiResponse);
    } catch (error) {
      console.error('Voice API error:', error);
      let errorMessage = 'Sorry, I could not process your request. Please try again.';
      
      if (error.response?.status === 401) {
        errorMessage = 'Please log in to use the Voice Assistant.';
        setIsLoggedIn(false);
      } else if (error.response?.data?.error) {
        errorMessage = error.response.data.error;
      }
      
      const assistantMessage = { 
        type: 'assistant', 
        text: errorMessage, 
        timestamp: new Date(),
        error: true
      };
      setConversation(prev => [...prev, assistantMessage]);
      setResponse(errorMessage);
    } finally {
      setLoading(false);
    }
  };


  const speakText = (text) => {
    if ('speechSynthesis' in window) {
      setIsSpeaking(true);
      const utterance = new SpeechSynthesisUtterance(text);
      utterance.onend = () => setIsSpeaking(false);
      utterance.onerror = () => setIsSpeaking(false);
      speechSynthesis.speak(utterance);
    }
  };

  const stopSpeaking = () => {
    if ('speechSynthesis' in window) {
      speechSynthesis.cancel();
      setIsSpeaking(false);
    }
  };

  const clearConversation = () => {
    setConversation([]);
    setTranscript('');
    setResponse('');
  };

  return (
    <div className="voice-assistant">
      <div className="page-header">
        <h1>Voice Assistant</h1>
        <p>Talk to your AI farming assistant using voice commands</p>
        {!isLoggedIn && (
          <div className="login-warning">
            <p>⚠️ Please log in to use the Voice Assistant</p>
          </div>
        )}
      </div>

      <div className="assistant-container">
        <div className="voice-controls">
          <h2>Voice Commands</h2>
          
          {!isSupported ? (
            <div className="error-message">
              <p>Speech recognition is not supported in your browser. Please use Chrome or Edge for the best experience.</p>
            </div>
          ) : (
            <div className="control-panel">
              <div className="voice-button-container">
                <button
                  onClick={isListening ? stopListening : startListening}
                  className={`voice-btn ${isListening ? 'listening' : ''}`}
                  disabled={isSpeaking || !isLoggedIn || loading}
                >
                  {isListening ? <MicOff size={32} /> : <Mic size={32} />}
                  <span>
                    {loading ? 'Processing...' : isListening ? 'Stop Listening' : 'Start Listening'}
                  </span>
                </button>
              </div>

              <div className="speech-controls">
                <button
                  onClick={isSpeaking ? stopSpeaking : () => speakText(response)}
                  className={`speak-btn ${isSpeaking ? 'speaking' : ''}`}
                  disabled={!response}
                >
                  {isSpeaking ? <VolumeX size={20} /> : <Volume2 size={20} />}
                  {isSpeaking ? 'Stop Speaking' : 'Repeat Response'}
                </button>
              </div>
            </div>
          )}

          {transcript && (
            <div className="transcript-section">
              <h3>You said:</h3>
              <p className="transcript-text">"{transcript}"</p>
            </div>
          )}

          {response && (
            <div className="response-section">
              <h3>Assistant Response:</h3>
              <p className="response-text">"{response}"</p>
            </div>
          )}
        </div>

        <div className="conversation-section">
          <div className="conversation-header">
            <h2>Conversation History</h2>
            <button onClick={clearConversation} className="clear-btn">
              Clear History
            </button>
          </div>
          
          <div className="conversation-list">
            {conversation.length === 0 ? (
              <div className="empty-conversation">
                <MessageSquare size={48} className="empty-icon" />
                <p>Start a conversation with your AI assistant</p>
              </div>
            ) : (
              conversation.map((message, index) => (
                <div key={index} className={`message ${message.type} ${message.error ? 'error' : ''}`}>
                  <div className="message-content">
                    <p>{message.text}</p>
                    {message.intent && (
                      <div className="message-meta">
                        <span className="intent">Intent: {message.intent}</span>
                        {message.confidence && (
                          <span className="confidence">Confidence: {Math.round(message.confidence * 100)}%</span>
                        )}
                      </div>
                    )}
                    <span className="message-time">
                      {message.timestamp.toLocaleTimeString()}
                    </span>
                  </div>
                </div>
              ))
            )}
          </div>
        </div>

        <div className="voice-commands-help">
          <h2>Voice Commands</h2>
          <div className="commands-grid">
            <div className="command-card">
              <h3>🌤️ Weather</h3>
              <p>"What's the weather like?"</p>
            </div>
            <div className="command-card">
              <h3>🌱 Soil</h3>
              <p>"Tell me about my soil condition"</p>
            </div>
            <div className="command-card">
              <h3>🌾 Crops</h3>
              <p>"What crops should I plant?"</p>
            </div>
            <div className="command-card">
              <h3>💧 Irrigation</h3>
              <p>"When should I water my crops?"</p>
            </div>
            <div className="command-card">
              <h3>🦠 Disease</h3>
              <p>"Help me identify plant diseases"</p>
            </div>
            <div className="command-card">
              <h3>💰 Market</h3>
              <p>"What are the current crop prices?"</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default VoiceAssistant;
