import { useState, useRef } from 'react'
import './Conversation.css'

interface Message {
  id: string
  role: 'user' | 'assistant'
  content: string
  timestamp: Date
}

function Conversation() {
  const [messages, setMessages] = useState<Message[]>([])
  const [input, setInput] = useState('')
  const [isRecording, setIsRecording] = useState(false)
  const [isSpeaking, setIsSpeaking] = useState(false)
  const audioRef = useRef<MediaRecorder | null>(null)

  const handleSend = () => {
    if (!input.trim()) return

    const userMessage: Message = {
      id: Date.now().toString(),
      role: 'user',
      content: input,
      timestamp: new Date(),
    }

    setMessages([...messages, userMessage])
    setInput('')

    // Simulate assistant response
    setTimeout(() => {
      const assistantMessage: Message = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: 'This is a simulated response. Connect to your agent backend for real interactions.',
        timestamp: new Date(),
      }
      setMessages(prev => [...prev, assistantMessage])
    }, 1000)
  }

  const handleSTT = async () => {
    if (!isRecording) {
      // Start recording
      try {
        const stream = await navigator.mediaDevices.getUserMedia({ audio: true })
        const mediaRecorder = new MediaRecorder(stream)
        audioRef.current = mediaRecorder

        mediaRecorder.start()
        setIsRecording(true)

        mediaRecorder.ondataavailable = (event) => {
          // In production, send to STT service
          console.log('Audio data available', event.data)
        }
      } catch (err) {
        console.error('Error accessing microphone:', err)
        alert('Microphone access denied. Please enable microphone permissions.')
      }
    } else {
      // Stop recording
      if (audioRef.current) {
        audioRef.current.stop()
        audioRef.current.stream.getTracks().forEach(track => track.stop())
        setIsRecording(false)
        setInput('Transcribed text would appear here...')
      }
    }
  }

  const handleTTS = (text: string) => {
    if (!isSpeaking) {
      // Use Web Speech API
      const utterance = new SpeechSynthesisUtterance(text)
      utterance.onstart = () => setIsSpeaking(true)
      utterance.onend = () => setIsSpeaking(false)
      speechSynthesis.speak(utterance)
    } else {
      speechSynthesis.cancel()
      setIsSpeaking(false)
    }
  }

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSend()
    }
  }

  return (
    <div className="conversation">
      <div className="messages-container">
        {messages.length === 0 ? (
          <div className="empty-state">
            <p>Start a conversation with your agent</p>
            <p className="text-muted">Type a message or use voice input</p>
          </div>
        ) : (
          messages.map(message => (
            <div key={message.id} className={`message message-${message.role}`}>
              <div className="message-avatar">
                {message.role === 'user' ? '👤' : '🤖'}
              </div>
              <div className="message-content">
                <div className="message-text">{message.content}</div>
                <div className="message-meta">
                  <span className="message-time">
                    {message.timestamp.toLocaleTimeString()}
                  </span>
                  {message.role === 'assistant' && (
                    <button
                      className="btn-icon"
                      onClick={() => handleTTS(message.content)}
                      title="Text to Speech"
                    >
                      {isSpeaking ? '🔇' : '🔊'}
                    </button>
                  )}
                </div>
              </div>
            </div>
          ))
        )}
      </div>

      <div className="input-container">
        <button
          className={`btn-stt ${isRecording ? 'recording' : ''}`}
          onClick={handleSTT}
          title={isRecording ? 'Stop Recording' : 'Start Recording'}
        >
          {isRecording ? '⏹️' : '🎤'}
        </button>
        <textarea
          className="conversation-input"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyPress={handleKeyPress}
          placeholder="Type your message..."
          rows={2}
        />
        <button
          className="btn btn-accent"
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
