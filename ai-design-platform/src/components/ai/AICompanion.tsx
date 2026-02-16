import React, { useState, useRef, useEffect } from 'react';
import { 
  MessageCircle, 
  X, 
  Send, 
  Mic, 
  MicOff,
  Settings,
  Volume2,
  VolumeX,
  Minimize2,
  Maximize2,
  User,
  Bot,
  Languages,
  Sparkles,
  Activity
} from 'lucide-react';
import type { ConversationMessage, AIPersonality, VoiceSettings } from '../../types';

export const AICompanion: React.FC = () => {
  const [isOpen, setIsOpen] = useState(false);
  const [isExpanded, setIsExpanded] = useState(false);
  const [showSettings, setShowSettings] = useState(false);
  const [messages, setMessages] = useState<ConversationMessage[]>([
    {
      id: '1',
      role: 'assistant',
      content: 'Hello! I\'m your AI companion. How can I help you today?',
      timestamp: new Date(),
      emotion: 'friendly'
    }
  ]);
  const [inputMessage, setInputMessage] = useState('');
  const [isListening, setIsListening] = useState(false);
  const [isTyping, setIsTyping] = useState(false);
  const [transcription, setTranscription] = useState('');
  
  const [voiceSettings, setVoiceSettings] = useState<VoiceSettings>({
    alwaysOn: false,
    voiceResponse: true,
    personality: 'professional',
    language: 'en-US',
    speechRate: 1.0,
    pitch: 1.0
  });

  const messagesEndRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  const personalities: AIPersonality[] = [
    {
      id: 'professional',
      name: 'Professional',
      description: 'Formal and business-focused',
      traits: ['Concise', 'Accurate', 'Efficient']
    },
    {
      id: 'friendly',
      name: 'Friendly',
      description: 'Warm and conversational',
      traits: ['Approachable', 'Supportive', 'Encouraging']
    },
    {
      id: 'teacher',
      name: 'Teacher',
      description: 'Educational and patient',
      traits: ['Explanatory', 'Patient', 'Detailed']
    },
    {
      id: 'mentor',
      name: 'Mentor',
      description: 'Guiding and strategic',
      traits: ['Strategic', 'Insightful', 'Growth-focused']
    }
  ];

  const languages = [
    { code: 'en-US', name: 'English (US)' },
    { code: 'en-GB', name: 'English (UK)' },
    { code: 'es-ES', name: 'Spanish' },
    { code: 'fr-FR', name: 'French' },
    { code: 'de-DE', name: 'German' },
    { code: 'ja-JP', name: 'Japanese' },
    { code: 'zh-CN', name: 'Chinese' }
  ];

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  useEffect(() => {
    if (isOpen && inputRef.current) {
      inputRef.current.focus();
    }
  }, [isOpen]);

  const handleSendMessage = () => {
    if (!inputMessage.trim()) return;

    const newMessage: ConversationMessage = {
      id: Date.now().toString(),
      role: 'user',
      content: inputMessage,
      timestamp: new Date()
    };

    setMessages(prev => [...prev, newMessage]);
    setInputMessage('');
    setIsTyping(true);

    // Simulate AI response
    setTimeout(() => {
      const aiResponse: ConversationMessage = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: `I understand your question about "${inputMessage}". Let me help you with that...`,
        timestamp: new Date(),
        emotion: voiceSettings.personality
      };
      setMessages(prev => [...prev, aiResponse]);
      setIsTyping(false);
    }, 1500);
  };

  const toggleVoice = () => {
    setIsListening(!isListening);
    if (!isListening) {
      // Simulate voice recognition
      setTranscription('Listening...');
      setTimeout(() => {
        setTranscription('How can I improve model accuracy?');
        setInputMessage('How can I improve model accuracy?');
      }, 2000);
    } else {
      setTranscription('');
    }
  };

  const formatTime = (date: Date) => {
    return date.toLocaleTimeString('en-US', { 
      hour: '2-digit', 
      minute: '2-digit' 
    });
  };

  return (
    <>
      {/* Floating AI Button */}
      {!isOpen && (
        <button
          onClick={() => setIsOpen(true)}
          className="fixed bottom-6 right-6 p-4 rounded-full bg-gradient-to-r from-purple-600 to-blue-500 text-white shadow-2xl hover:scale-110 transition-all duration-300 pulse-glow z-50"
        >
          <div className="relative">
            <MessageCircle className="w-6 h-6" />
            <div className="absolute -top-1 -right-1 w-3 h-3 bg-green-400 rounded-full animate-pulse" />
          </div>
        </button>
      )}

      {/* Chat Window */}
      {isOpen && (
        <div 
          className={`fixed bottom-6 right-6 glass rounded-2xl shadow-2xl z-50 flex flex-col transition-all duration-300 ${
            isExpanded 
              ? 'w-[600px] h-[700px]' 
              : 'w-[400px] h-[600px]'
          }`}
        >
          {/* Header */}
          <div className="flex items-center justify-between p-4 border-b border-white/10">
            <div className="flex items-center gap-3">
              <div className="relative">
                <div className="w-10 h-10 rounded-full bg-gradient-to-br from-purple-500 to-blue-500 flex items-center justify-center pulse-glow">
                  <Sparkles className="w-5 h-5 text-white" />
                </div>
                <div className="absolute -bottom-1 -right-1 w-3 h-3 bg-green-400 rounded-full border-2 border-gray-900" />
              </div>
              <div>
                <h3 className="font-semibold text-white">AI Companion</h3>
                <p className="text-xs text-gray-400">
                  {personalities.find(p => p.id === voiceSettings.personality)?.name} Mode
                </p>
              </div>
            </div>
            <div className="flex items-center gap-2">
              <button
                onClick={() => setShowSettings(!showSettings)}
                className={`p-2 rounded-lg transition-colors ${
                  showSettings 
                    ? 'bg-purple-500/20 text-purple-400' 
                    : 'hover:bg-white/10 text-gray-400'
                }`}
              >
                <Settings className="w-4 h-4" />
              </button>
              <button
                onClick={() => setIsExpanded(!isExpanded)}
                className="p-2 rounded-lg hover:bg-white/10 text-gray-400"
              >
                {isExpanded ? <Minimize2 className="w-4 h-4" /> : <Maximize2 className="w-4 h-4" />}
              </button>
              <button
                onClick={() => setIsOpen(false)}
                className="p-2 rounded-lg hover:bg-white/10 text-gray-400"
              >
                <X className="w-4 h-4" />
              </button>
            </div>
          </div>

          {/* Settings Panel */}
          {showSettings && (
            <div className="p-4 border-b border-white/10 bg-white/5 space-y-4">
              {/* Personality Selection */}
              <div>
                <label className="text-xs text-gray-400 mb-2 block">Personality</label>
                <div className="grid grid-cols-2 gap-2">
                  {personalities.map((personality) => (
                    <button
                      key={personality.id}
                      onClick={() => setVoiceSettings(prev => ({ ...prev, personality: personality.id }))}
                      className={`p-3 rounded-lg text-left transition-all ${
                        voiceSettings.personality === personality.id
                          ? 'bg-purple-500/20 border border-purple-500/50'
                          : 'bg-white/5 border border-white/10 hover:bg-white/10'
                      }`}
                    >
                      <div className="font-medium text-sm text-white mb-1">{personality.name}</div>
                      <div className="text-xs text-gray-400">{personality.description}</div>
                    </button>
                  ))}
                </div>
              </div>

              {/* Language Selection */}
              <div>
                <label className="text-xs text-gray-400 mb-2 flex items-center gap-2">
                  <Languages className="w-3 h-3" />
                  Language
                </label>
                <select
                  value={voiceSettings.language}
                  onChange={(e) => setVoiceSettings(prev => ({ ...prev, language: e.target.value }))}
                  className="w-full bg-white/5 border border-white/10 rounded-lg px-3 py-2 text-sm text-white focus:outline-none focus:ring-2 focus:ring-purple-500"
                >
                  {languages.map((lang) => (
                    <option key={lang.code} value={lang.code}>{lang.name}</option>
                  ))}
                </select>
              </div>

              {/* Voice Controls */}
              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="text-xs text-gray-400 mb-2 block">Speech Rate</label>
                  <input
                    type="range"
                    min="0.5"
                    max="2"
                    step="0.1"
                    value={voiceSettings.speechRate}
                    onChange={(e) => setVoiceSettings(prev => ({ ...prev, speechRate: parseFloat(e.target.value) }))}
                    className="w-full"
                  />
                  <span className="text-xs text-gray-500">{voiceSettings.speechRate}x</span>
                </div>
                <div>
                  <label className="text-xs text-gray-400 mb-2 block">Pitch</label>
                  <input
                    type="range"
                    min="0.5"
                    max="2"
                    step="0.1"
                    value={voiceSettings.pitch}
                    onChange={(e) => setVoiceSettings(prev => ({ ...prev, pitch: parseFloat(e.target.value) }))}
                    className="w-full"
                  />
                  <span className="text-xs text-gray-500">{voiceSettings.pitch}x</span>
                </div>
              </div>

              {/* Toggle Options */}
              <div className="flex items-center justify-between">
                <span className="text-sm text-gray-300">Voice Response</span>
                <button
                  onClick={() => setVoiceSettings(prev => ({ ...prev, voiceResponse: !prev.voiceResponse }))}
                  className={`relative w-12 h-6 rounded-full transition-colors ${
                    voiceSettings.voiceResponse ? 'bg-purple-500' : 'bg-gray-700'
                  }`}
                >
                  <div className={`absolute top-1 w-4 h-4 rounded-full bg-white transition-transform ${
                    voiceSettings.voiceResponse ? 'left-7' : 'left-1'
                  }`} />
                </button>
              </div>
            </div>
          )}

          {/* Messages */}
          <div className="flex-1 overflow-y-auto p-4 space-y-4">
            {messages.map((message) => (
              <div
                key={message.id}
                className={`flex gap-3 ${message.role === 'user' ? 'flex-row-reverse' : 'flex-row'}`}
              >
                <div className={`w-8 h-8 rounded-full flex items-center justify-center flex-shrink-0 ${
                  message.role === 'user'
                    ? 'bg-gradient-to-br from-blue-500 to-cyan-500'
                    : 'bg-gradient-to-br from-purple-500 to-pink-500'
                }`}>
                  {message.role === 'user' ? (
                    <User className="w-4 h-4 text-white" />
                  ) : (
                    <Bot className="w-4 h-4 text-white" />
                  )}
                </div>
                <div className={`flex-1 ${message.role === 'user' ? 'items-end' : 'items-start'} flex flex-col`}>
                  <div className={`px-4 py-2 rounded-2xl max-w-[80%] ${
                    message.role === 'user'
                      ? 'bg-gradient-to-r from-blue-500 to-cyan-500 text-white rounded-tr-none'
                      : 'bg-white/10 text-gray-100 rounded-tl-none'
                  }`}>
                    <p className="text-sm">{message.content}</p>
                  </div>
                  <span className="text-xs text-gray-500 mt-1 px-1">
                    {formatTime(message.timestamp)}
                  </span>
                </div>
              </div>
            ))}
            
            {/* Typing Indicator */}
            {isTyping && (
              <div className="flex gap-3">
                <div className="w-8 h-8 rounded-full bg-gradient-to-br from-purple-500 to-pink-500 flex items-center justify-center">
                  <Bot className="w-4 h-4 text-white" />
                </div>
                <div className="bg-white/10 px-4 py-3 rounded-2xl rounded-tl-none">
                  <div className="flex gap-1">
                    <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0ms' }} />
                    <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '150ms' }} />
                    <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '300ms' }} />
                  </div>
                </div>
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>

          {/* Voice Activity Indicator */}
          {isListening && (
            <div className="px-4 py-3 bg-purple-500/20 border-t border-purple-500/30">
              <div className="flex items-center gap-3">
                <Activity className="w-4 h-4 text-purple-400 animate-pulse" />
                <div className="flex-1">
                  <div className="text-xs text-purple-400 mb-1">Listening...</div>
                  {transcription && (
                    <div className="text-sm text-white">{transcription}</div>
                  )}
                </div>
                <div className="flex gap-1">
                  {[...Array(5)].map((_, i) => (
                    <div 
                      key={i}
                      className="w-1 bg-purple-400 rounded-full animate-pulse"
                      style={{ 
                        height: `${Math.random() * 20 + 10}px`,
                        animationDelay: `${i * 100}ms` 
                      }}
                    />
                  ))}
                </div>
              </div>
            </div>
          )}

          {/* Input */}
          <div className="p-4 border-t border-white/10">
            <div className="flex gap-2">
              <button
                onClick={toggleVoice}
                className={`p-3 rounded-lg transition-all ${
                  isListening
                    ? 'bg-red-500 text-white pulse-glow'
                    : 'bg-white/10 text-gray-400 hover:bg-white/20'
                }`}
              >
                {isListening ? <MicOff className="w-5 h-5" /> : <Mic className="w-5 h-5" />}
              </button>
              <input
                ref={inputRef}
                type="text"
                value={inputMessage}
                onChange={(e) => setInputMessage(e.target.value)}
                onKeyPress={(e) => e.key === 'Enter' && handleSendMessage()}
                placeholder="Type your message..."
                className="flex-1 bg-white/10 border border-white/10 rounded-lg px-4 py-3 text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-purple-500"
              />
              <button
                onClick={handleSendMessage}
                disabled={!inputMessage.trim()}
                className="p-3 rounded-lg bg-gradient-to-r from-purple-600 to-blue-500 text-white disabled:opacity-50 disabled:cursor-not-allowed hover:scale-105 transition-transform"
              >
                <Send className="w-5 h-5" />
              </button>
              <button
                onClick={() => setVoiceSettings(prev => ({ ...prev, voiceResponse: !prev.voiceResponse }))}
                className={`p-3 rounded-lg transition-colors ${
                  voiceSettings.voiceResponse
                    ? 'bg-purple-500/20 text-purple-400'
                    : 'bg-white/10 text-gray-400'
                }`}
              >
                {voiceSettings.voiceResponse ? <Volume2 className="w-5 h-5" /> : <VolumeX className="w-5 h-5" />}
              </button>
            </div>
          </div>
        </div>
      )}
    </>
  );
};
