import { useState } from 'react';

interface Message {
  text: string;
  sender: 'user' | 'agent';
}

function Conversation() {
  const [messages, setMessages] = useState<Message[]>([
    { text: 'Hello! I am your AI assistant. How can I help you today?', sender: 'agent' }
  ]);
  const [input, setInput] = useState('');

  const handleSend = () => {
    if (!input.trim()) return;

    // Add user message
    const userMessage: Message = { text: input, sender: 'user' };
    setMessages([...messages, userMessage]);

    // Simulate agent response
    setTimeout(() => {
      const agentMessage: Message = {
        text: `I received your message: "${input}". This is a simulated response.`,
        sender: 'agent'
      };
      setMessages(prev => [...prev, agentMessage]);
    }, 1000);

    setInput('');
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  // Note: STT/TTS functionality would be implemented here
  // using Web Speech API or external services

  return (
    <div className="conversation">
      <div className="messages">
        {messages.map((msg, idx) => (
          <div key={idx} className={`message ${msg.sender}`}>
            {msg.text}
          </div>
        ))}
      </div>
      <div className="conversation-input">
        <input
          type="text"
          className="form-input"
          placeholder="Type your message..."
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyPress={handleKeyPress}
        />
        <button className="btn btn-primary" onClick={handleSend}>
          Send
        </button>
      </div>
    </div>
  );
}

export default Conversation;
