import { useState, useRef, useEffect } from 'react'

interface Message {
  id: number
  role: 'user' | 'assistant'
  content: string
  timestamp: Date
}

function Conversation() {
  const [messages, setMessages] = useState<Message[]>([])
  const [input, setInput] = useState('')
  const [isListening, setIsListening] = useState(false)
  const [isSpeaking, setIsSpeaking] = useState(false)
  const messagesEndRef = useRef<HTMLDivElement>(null)

  // Speech recognition (STT)
  const recognition = useRef<SpeechRecognition | null>(null)

  useEffect(() => {
    // Initialize speech recognition if available
    if ('SpeechRecognition' in window || 'webkitSpeechRecognition' in window) {
      const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition
      recognition.current = new SpeechRecognition()
      recognition.current.continuous = false
      recognition.current.interimResults = false

      recognition.current.onresult = (event) => {
        const transcript = event.results[0][0].transcript
        setInput(transcript)
        setIsListening(false)
      }

      recognition.current.onerror = () => {
        setIsListening(false)
      }

      recognition.current.onend = () => {
        setIsListening(false)
      }
    }
  }, [])

  // Text-to-speech (TTS)
  const speak = (text: string) => {
    if ('speechSynthesis' in window) {
      setIsSpeaking(true)
      const utterance = new SpeechSynthesisUtterance(text)
      utterance.onend = () => setIsSpeaking(false)
      window.speechSynthesis.speak(utterance)
    }
  }

  const toggleListening = () => {
    if (recognition.current) {
      if (isListening) {
        recognition.current.stop()
      } else {
        recognition.current.start()
        setIsListening(true)
      }
    }
  }

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  const sendMessage = async () => {
    if (!input.trim()) return

    const userMessage: Message = {
      id: Date.now(),
      role: 'user',
      content: input,
      timestamp: new Date(),
    }

    setMessages((prev) => [...prev, userMessage])
    setInput('')

    // Simulate AI response (replace with actual API call)
    setTimeout(() => {
      const assistantMessage: Message = {
        id: Date.now() + 1,
        role: 'assistant',
        content: `I received your message: "${userMessage.content}". This is a simulated response. Connect to the backend API for real AI responses.`,
        timestamp: new Date(),
      }
      setMessages((prev) => [...prev, assistantMessage])
      
      // Optionally speak the response
      // speak(assistantMessage.content)
    }, 1000)
  }

  return (
    <div className="conversation">
      <div className="conversation-controls">
        <button 
          className={`btn ${isListening ? 'btn-secondary' : ''}`}
          onClick={toggleListening}
          disabled={!recognition.current}
        >
          {isListening ? '🎙️ Listening...' : '🎤 Voice Input'}
        </button>
        <button 
          className="btn"
          onClick={() => {
            if (messages.length > 0) {
              const lastAssistant = messages.filter(m => m.role === 'assistant').pop()
              if (lastAssistant) speak(lastAssistant.content)
            }
          }}
          disabled={isSpeaking}
        >
          {isSpeaking ? '🔊 Speaking...' : '🔈 Read Last'}
        </button>
      </div>

      <div className="card" style={{ height: '400px', overflowY: 'auto' }}>
        {messages.length === 0 ? (
          <p style={{ color: 'var(--text-muted)', textAlign: 'center' }}>
            Start a conversation...
          </p>
        ) : (
          messages.map((message) => (
            <div
              key={message.id}
              className={`conversation-message ${message.role}`}
            >
              <p>{message.content}</p>
              <small style={{ color: 'var(--text-muted)' }}>
                {message.timestamp.toLocaleTimeString()}
              </small>
            </div>
          ))
        )}
        <div ref={messagesEndRef} />
      </div>

      <div style={{ display: 'flex', gap: '1rem', marginTop: '1rem' }}>
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyPress={(e) => e.key === 'Enter' && sendMessage()}
          placeholder="Type your message..."
        />
        <button className="btn" onClick={sendMessage}>
          Send
        </button>
      </div>
    </div>
  )
}

export default Conversation

// Extend Window interface for TypeScript
declare global {
  interface Window {
    SpeechRecognition: typeof SpeechRecognition
    webkitSpeechRecognition: typeof SpeechRecognition
  }
}
