import { useState } from 'react'

function Conversation() {
  const [messages, setMessages] = useState<Array<{ role: 'user' | 'assistant', content: string }>>([])
  const [input, setInput] = useState('')
  const [isRecording, setIsRecording] = useState(false)

  const handleSend = () => {
    if (!input.trim()) return

    setMessages([...messages, { role: 'user', content: input }])
    
    // Simulate AI response
    setTimeout(() => {
      setMessages(prev => [...prev, {
        role: 'assistant',
        content: `I received your message: "${input}". This is a demo response. Connect to the backend API for real responses.`
      }])
    }, 1000)

    setInput('')
  }

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSend()
    }
  }

  const toggleRecording = () => {
    // STT functionality placeholder
    setIsRecording(!isRecording)
    console.log('Speech-to-Text:', isRecording ? 'Stopped' : 'Started')
  }

  const handleSpeak = (text: string) => {
    // TTS functionality placeholder
    console.log('Text-to-Speech:', text)
    if ('speechSynthesis' in window) {
      const utterance = new SpeechSynthesisUtterance(text)
      window.speechSynthesis.speak(utterance)
    }
  }

  return (
    <div className="conversation-container">
      <div className="messages-container">
        {messages.length === 0 ? (
          <div className="empty-state">
            <p>Start a conversation with the AI agent</p>
          </div>
        ) : (
          messages.map((msg, idx) => (
            <div key={idx} className={`message ${msg.role}`}>
              <div className="message-content">
                {msg.content}
              </div>
              {msg.role === 'assistant' && (
                <button 
                  className="speak-btn"
                  onClick={() => handleSpeak(msg.content)}
                  title="Speak message"
                >
                  🔊
                </button>
              )}
            </div>
          ))
        )}
      </div>
      
      <div className="input-container">
        <textarea
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyPress={handleKeyPress}
          placeholder="Type your message... (Enter to send)"
          rows={3}
        />
        <div className="input-actions">
          <button 
            className={`record-btn ${isRecording ? 'recording' : ''}`}
            onClick={toggleRecording}
            title="Voice input"
          >
            {isRecording ? '⏹️' : '🎤'}
          </button>
          <button onClick={handleSend}>Send</button>
        </div>
      </div>
    </div>
  )
}

export default Conversation
