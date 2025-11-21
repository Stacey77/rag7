import { useState, useRef } from 'react'
import './Conversation.css'

interface Message {
  id: string
  role: 'user' | 'assistant'
  content: string
  timestamp: Date
}

const Conversation = () => {
  const [messages, setMessages] = useState<Message[]>([])
  const [input, setInput] = useState('')
  const [isRecording, setIsRecording] = useState(false)
  const [isSpeaking, setIsSpeaking] = useState(false)
  const mediaRecorderRef = useRef<MediaRecorder | null>(null)

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

    // Simulate AI response
    setTimeout(() => {
      const aiMessage: Message = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: 'This is a simulated response. Connect to a real agent for actual conversations.',
        timestamp: new Date(),
      }
      setMessages((prev) => [...prev, aiMessage])
    }, 1000)
  }

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSend()
    }
  }

  const toggleRecording = async () => {
    if (isRecording) {
      // Stop recording
      mediaRecorderRef.current?.stop()
      setIsRecording(false)
    } else {
      // Start recording (STT simulation)
      try {
        const stream = await navigator.mediaDevices.getUserMedia({ audio: true })
        const mediaRecorder = new MediaRecorder(stream)
        mediaRecorderRef.current = mediaRecorder

        mediaRecorder.ondataavailable = () => {
          // In a real implementation, send audio to STT service
          setInput('Voice input would appear here...')
        }

        mediaRecorder.start()
        setIsRecording(true)
      } catch (error) {
        console.error('Microphone access denied:', error)
        alert('Microphone access is required for voice input.')
      }
    }
  }

  const toggleTTS = () => {
    // TTS simulation
    setIsSpeaking(!isSpeaking)
    if (!isSpeaking) {
      // In a real implementation, use Web Speech API or external TTS
      const utterance = new SpeechSynthesisUtterance(
        messages.length > 0 
          ? messages[messages.length - 1].content 
          : 'No messages to speak.'
      )
      utterance.onend = () => setIsSpeaking(false)
      window.speechSynthesis.speak(utterance)
    } else {
      window.speechSynthesis.cancel()
    }
  }

  return (
    <div className="conversation-container">
      <div className="messages-container">
        {messages.length === 0 ? (
          <div className="empty-state">
            <p className="text-muted">Start a conversation with your AI agent...</p>
          </div>
        ) : (
          messages.map((message) => (
            <div key={message.id} className={`message ${message.role}`}>
              <div className="message-avatar">
                {message.role === 'user' ? '👤' : '🤖'}
              </div>
              <div className="message-content">
                <div className="message-text">{message.content}</div>
                <div className="message-time">
                  {message.timestamp.toLocaleTimeString()}
                </div>
              </div>
            </div>
          ))
        )}
      </div>

      <div className="input-container">
        <button
          className={`voice-button ${isRecording ? 'recording' : ''}`}
          onClick={toggleRecording}
          title="Voice Input (STT)"
        >
          {isRecording ? '🔴' : '🎤'}
        </button>

        <textarea
          className="message-input"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyPress={handleKeyPress}
          placeholder="Type your message or use voice input..."
          rows={2}
        />

        <button
          className={`tts-button ${isSpeaking ? 'speaking' : ''}`}
          onClick={toggleTTS}
          title="Text-to-Speech (TTS)"
          disabled={messages.length === 0}
        >
          {isSpeaking ? '🔊' : '🔇'}
        </button>

        <button className="send-button" onClick={handleSend}>
          Send
        </button>
      </div>
    </div>
  )
}

export default Conversation
