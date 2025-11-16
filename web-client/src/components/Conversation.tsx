import { useState } from 'react'
import './Conversation.css'

const Conversation = () => {
  const [messages, setMessages] = useState<Array<{ role: 'user' | 'ai', text: string }>>([])
  const [input, setInput] = useState('')
  const [isListening, setIsListening] = useState(false)

  const handleSend = () => {
    if (!input.trim()) return
    
    setMessages([...messages, { role: 'user', text: input }])
    setInput('')
    
    // Simulate AI response
    setTimeout(() => {
      setMessages(prev => [...prev, { 
        role: 'ai', 
        text: 'This is a simulated AI response. Connect to the backend to enable real responses.' 
      }])
    }, 1000)
  }

  const handleVoiceInput = () => {
    setIsListening(!isListening)
    // TODO: Implement Web Speech API for STT
    console.log('Voice input toggled:', !isListening)
  }

  const handleSpeak = (text: string) => {
    // TODO: Implement Web Speech API for TTS
    console.log('Speaking:', text)
  }

  return (
    <div className="conversation-container">
      <div className="messages-container">
        {messages.length === 0 ? (
          <div className="empty-state">
            <p>Start a conversation...</p>
          </div>
        ) : (
          messages.map((msg, idx) => (
            <div key={idx} className={`message message-${msg.role}`}>
              <div className="message-avatar">
                {msg.role === 'user' ? '👤' : '🤖'}
              </div>
              <div className="message-content">
                <p>{msg.text}</p>
                {msg.role === 'ai' && (
                  <button 
                    className="speak-btn"
                    onClick={() => handleSpeak(msg.text)}
                    title="Speak"
                  >
                    🔊
                  </button>
                )}
              </div>
            </div>
          ))
        )}
      </div>
      
      <div className="input-container">
        <button 
          className={`voice-btn ${isListening ? 'listening' : ''}`}
          onClick={handleVoiceInput}
          title="Voice Input"
        >
          🎤
        </button>
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyPress={(e) => e.key === 'Enter' && handleSend()}
          placeholder="Type your message..."
          className="message-input"
        />
        <button onClick={handleSend} className="send-btn" title="Send">
          ➤
        </button>
      </div>
    </div>
  )
}

export default Conversation
