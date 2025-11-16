import { useState, useEffect, useRef } from 'react'
import './Conversation.css'

interface Message {
  id: string
  text: string
  sender: 'user' | 'ai'
  timestamp: Date
}

const Conversation = () => {
  const [messages, setMessages] = useState<Message[]>([])
  const [input, setInput] = useState('')
  const [isListening, setIsListening] = useState(false)
  const [isSpeaking, setIsSpeaking] = useState(false)
  const messagesEndRef = useRef<HTMLDivElement>(null)
  
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }
  
  useEffect(() => {
    scrollToBottom()
  }, [messages])
  
  const handleSend = () => {
    if (!input.trim()) return
    
    const userMessage: Message = {
      id: Date.now().toString(),
      text: input,
      sender: 'user',
      timestamp: new Date()
    }
    
    setMessages([...messages, userMessage])
    setInput('')
    
    // Simulate AI response
    setTimeout(() => {
      const aiMessage: Message = {
        id: (Date.now() + 1).toString(),
        text: `AI response to: "${input}"`,
        sender: 'ai',
        timestamp: new Date()
      }
      setMessages(prev => [...prev, aiMessage])
    }, 1000)
  }
  
  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSend()
    }
  }
  
  // Speech-to-Text (STT) simulation
  const toggleSTT = () => {
    setIsListening(!isListening)
    // In a real implementation, this would use Web Speech API
    if (!isListening) {
      // Simulate speech recognition
      setTimeout(() => {
        setInput('Voice input detected...')
        setIsListening(false)
      }, 2000)
    }
  }
  
  // Text-to-Speech (TTS) simulation
  const speakMessage = (text: string) => {
    setIsSpeaking(true)
    // In a real implementation, this would use Web Speech API
    if ('speechSynthesis' in window) {
      const utterance = new SpeechSynthesisUtterance(text)
      utterance.onend = () => setIsSpeaking(false)
      window.speechSynthesis.speak(utterance)
    } else {
      setTimeout(() => setIsSpeaking(false), 2000)
    }
  }
  
  return (
    <div className="conversation-container">
      <div className="messages-container">
        {messages.length === 0 ? (
          <div className="empty-state">
            <p>Start a conversation with the AI...</p>
          </div>
        ) : (
          messages.map(message => (
            <div key={message.id} className={`message ${message.sender}`}>
              <div className="message-content">
                <p>{message.text}</p>
                {message.sender === 'ai' && (
                  <button 
                    className="speak-btn"
                    onClick={() => speakMessage(message.text)}
                    disabled={isSpeaking}
                  >
                    🔊
                  </button>
                )}
              </div>
              <span className="message-time">
                {message.timestamp.toLocaleTimeString()}
              </span>
            </div>
          ))
        )}
        <div ref={messagesEndRef} />
      </div>
      
      <div className="input-container">
        <button 
          className={`stt-btn ${isListening ? 'listening' : ''}`}
          onClick={toggleSTT}
          title="Speech to Text"
        >
          🎤
        </button>
        <textarea
          className="conversation-input"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyPress={handleKeyPress}
          placeholder="Type your message or use voice input..."
          rows={1}
        />
        <button 
          className="send-btn"
          onClick={handleSend}
          disabled={!input.trim()}
        >
          Send
        </button>
      </div>
    </div>
  )
}

export default Conversation
