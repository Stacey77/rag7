import { useState } from 'react'

interface Message {
  id: string
  sender: 'user' | 'agent'
  text: string
  timestamp: Date
}

function Conversation() {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: '1',
      sender: 'agent',
      text: 'Hello! I\'m your AI agent. How can I assist you today?',
      timestamp: new Date(),
    },
  ])
  const [input, setInput] = useState('')

  const handleSend = () => {
    if (!input.trim()) return

    const newMessage: Message = {
      id: Date.now().toString(),
      sender: 'user',
      text: input,
      timestamp: new Date(),
    }

    setMessages([...messages, newMessage])
    setInput('')

    // Simulate agent response
    setTimeout(() => {
      const agentResponse: Message = {
        id: (Date.now() + 1).toString(),
        sender: 'agent',
        text: `I received your message: "${input}". This is a placeholder response. Connect a real agent flow to get actual responses.`,
        timestamp: new Date(),
      }
      setMessages((prev) => [...prev, agentResponse])
    }, 1000)
  }

  return (
    <div>
      <div className="conversation" style={{ marginBottom: '1rem', maxHeight: '500px', overflowY: 'auto' }}>
        {messages.map((message) => (
          <div key={message.id} className={`message ${message.sender}`}>
            <div className="message-avatar">
              {message.sender === 'user' ? '👤' : '🤖'}
            </div>
            <div className="message-content">
              <div className="message-sender">
                {message.sender === 'user' ? 'You' : 'AI Agent'}
              </div>
              <div className="message-text">{message.text}</div>
            </div>
          </div>
        ))}
      </div>

      <div style={{ display: 'flex', gap: '0.75rem' }}>
        <input
          type="text"
          className="form-input"
          placeholder="Type your message..."
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyPress={(e) => e.key === 'Enter' && handleSend()}
          style={{ flex: 1 }}
        />
        <button className="btn btn-primary" onClick={handleSend}>
          Send
        </button>
      </div>
    </div>
  )
}

export default Conversation
