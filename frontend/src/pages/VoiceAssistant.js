import React, { useState, useEffect } from 'react';
import { Mic, MicOff, Volume2, VolumeX, MessageSquare } from 'lucide-react';

const VoiceAssistant = () => {
  const [isListening, setIsListening] = useState(false);
  const [isSpeaking, setIsSpeaking] = useState(false);
  const [transcript, setTranscript] = useState('');
  const [response, setResponse] = useState('');
  const [conversation, setConversation] = useState([]);
  const [isSupported, setIsSupported] = useState(false);

  useEffect(() => {
    // Check if speech recognition is supported
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    setIsSupported(!!SpeechRecognition);
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
    const userMessage = { type: 'user', text: command, timestamp: new Date() };
    setConversation(prev => [...prev, userMessage]);

    // Simulate AI response
    const aiResponse = generateAIResponse(command);
    const assistantMessage = { type: 'assistant', text: aiResponse, timestamp: new Date() };
    setConversation(prev => [...prev, assistantMessage]);
    
    setResponse(aiResponse);
    speakText(aiResponse);
  };

  const generateAIResponse = (command) => {
    const lowerCommand = command.toLowerCase();
    
    if (lowerCommand.includes('weather')) {
      return "The current weather is partly cloudy with a temperature of 28°C. It's a good day for outdoor farming activities.";
    } else if (lowerCommand.includes('soil')) {
      return "Based on your recent soil analysis, your soil pH is 6.5, which is optimal for most crops. I recommend adding organic compost to improve soil structure.";
    } else if (lowerCommand.includes('crop') || lowerCommand.includes('plant')) {
      return "For your current soil conditions, I recommend planting wheat or corn. These crops are well-suited for your region and current weather patterns.";
    } else if (lowerCommand.includes('irrigation') || lowerCommand.includes('water')) {
      return "Your soil moisture is at 60%. I recommend watering your crops every 2-3 days during this dry season. Monitor the soil moisture regularly.";
    } else if (lowerCommand.includes('disease') || lowerCommand.includes('pest')) {
      return "I can help you identify plant diseases. Please upload an image of the affected plant, and I'll analyze it for you.";
    } else if (lowerCommand.includes('market') || lowerCommand.includes('price')) {
      return "Current market prices: Wheat is at ₹2500 per quintal, Rice at ₹3200, and Corn at ₹1800. Wheat prices are trending upward.";
    } else if (lowerCommand.includes('hello') || lowerCommand.includes('hi')) {
      return "Hello! I'm your AI farming assistant. How can I help you with your farm today?";
    } else {
      return "I understand you're asking about: " + command + ". Could you please be more specific about what farming information you need?";
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
                  disabled={isSpeaking}
                >
                  {isListening ? <MicOff size={32} /> : <Mic size={32} />}
                  <span>{isListening ? 'Stop Listening' : 'Start Listening'}</span>
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
                <div key={index} className={`message ${message.type}`}>
                  <div className="message-content">
                    <p>{message.text}</p>
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
