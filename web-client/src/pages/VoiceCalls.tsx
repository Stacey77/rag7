import VoiceCall from '../components/VoiceCall'

function VoiceCalls() {
  return (
    <div className="page-container">
      <div className="page-header">
        <h1>🎤 Voice Calls</h1>
        <p className="subtitle">Real-time voice AI conversations powered by Retell.ai</p>
      </div>

      <div className="voice-calls-content">
        <div className="info-section">
          <h2>About Voice Calls</h2>
          <div className="info-cards">
            <div className="info-card">
              <span className="icon">🤖</span>
              <h3>AI Voice Agents</h3>
              <p>Create intelligent voice agents that can handle natural conversations with users</p>
            </div>
            <div className="info-card">
              <span className="icon">📞</span>
              <h3>Web & Phone Calls</h3>
              <p>Support for browser-based calls and outbound phone calls</p>
            </div>
            <div className="info-card">
              <span className="icon">📝</span>
              <h3>Live Transcription</h3>
              <p>Real-time transcription of all conversations with full history</p>
            </div>
            <div className="info-card">
              <span className="icon">⚡</span>
              <h3>Low Latency</h3>
              <p>Ultra-fast response times for natural conversation flow</p>
            </div>
          </div>
        </div>

        <div className="call-section">
          <VoiceCall />
        </div>

        <div className="features-section">
          <h2>Retell.ai Features</h2>
          <div className="feature-list">
            <div className="feature-item">
              <span className="check">✓</span>
              <span>Conversational AI with natural language understanding</span>
            </div>
            <div className="feature-item">
              <span className="check">✓</span>
              <span>High-quality text-to-speech with multiple voice options</span>
            </div>
            <div className="feature-item">
              <span className="check">✓</span>
              <span>Accurate speech-to-text transcription</span>
            </div>
            <div className="feature-item">
              <span className="check">✓</span>
              <span>Customizable agent personalities and behaviors</span>
            </div>
            <div className="feature-item">
              <span className="check">✓</span>
              <span>Webhook integration for call events</span>
            </div>
            <div className="feature-item">
              <span className="check">✓</span>
              <span>Post-call analysis and insights</span>
            </div>
            <div className="feature-item">
              <span className="check">✓</span>
              <span>Dynamic variables for personalized conversations</span>
            </div>
            <div className="feature-item">
              <span className="check">✓</span>
              <span>Backchannel responses for natural interaction</span>
            </div>
          </div>
        </div>

        <div className="integration-section">
          <h2>Integration with Ragamuffin</h2>
          <p>
            Voice Calls integrates seamlessly with other Ragamuffin features:
          </p>
          <ul>
            <li><strong>RAG Context:</strong> Voice agents can access your embedded documents for informed responses</li>
            <li><strong>LangFlow Agents:</strong> Connect voice calls to your custom AI workflows</li>
            <li><strong>n8n Automation:</strong> Trigger workflows based on call events</li>
            <li><strong>Call Analytics:</strong> Track and analyze all voice interactions</li>
          </ul>
        </div>
      </div>

      <style>{`
        .voice-calls-content {
          max-width: 1200px;
          margin: 0 auto;
        }

        .info-section {
          margin-bottom: 40px;
        }

        .info-section h2 {
          font-family: 'Orbitron', sans-serif;
          color: #fff;
          margin-bottom: 20px;
        }

        .info-cards {
          display: grid;
          grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
          gap: 20px;
        }

        .info-card {
          background: linear-gradient(135deg, rgba(30, 0, 50, 0.8), rgba(60, 0, 80, 0.8));
          border-radius: 12px;
          padding: 24px;
          border: 1px solid rgba(138, 43, 226, 0.3);
          text-align: center;
          transition: all 0.3s;
        }

        .info-card:hover {
          transform: translateY(-4px);
          border-color: rgba(138, 43, 226, 0.6);
          box-shadow: 0 8px 24px rgba(138, 43, 226, 0.2);
        }

        .info-card .icon {
          font-size: 48px;
          display: block;
          margin-bottom: 16px;
        }

        .info-card h3 {
          font-family: 'Orbitron', sans-serif;
          color: #fff;
          margin-bottom: 8px;
          font-size: 16px;
        }

        .info-card p {
          color: #aaa;
          font-size: 14px;
          line-height: 1.5;
          margin: 0;
        }

        .call-section {
          margin-bottom: 40px;
        }

        .features-section {
          margin-bottom: 40px;
        }

        .features-section h2 {
          font-family: 'Orbitron', sans-serif;
          color: #fff;
          margin-bottom: 20px;
        }

        .feature-list {
          display: grid;
          grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
          gap: 12px;
        }

        .feature-item {
          display: flex;
          align-items: center;
          gap: 12px;
          padding: 12px 16px;
          background: rgba(0, 0, 0, 0.2);
          border-radius: 8px;
          color: #ccc;
        }

        .feature-item .check {
          color: #00ff88;
          font-size: 18px;
        }

        .integration-section {
          background: linear-gradient(135deg, rgba(0, 50, 80, 0.5), rgba(0, 80, 100, 0.5));
          border-radius: 12px;
          padding: 24px;
          border: 1px solid rgba(0, 150, 200, 0.3);
        }

        .integration-section h2 {
          font-family: 'Orbitron', sans-serif;
          color: #fff;
          margin-bottom: 16px;
        }

        .integration-section p {
          color: #ccc;
          margin-bottom: 16px;
        }

        .integration-section ul {
          list-style: none;
          padding: 0;
          margin: 0;
        }

        .integration-section li {
          padding: 8px 0;
          color: #aaa;
          border-bottom: 1px solid rgba(255, 255, 255, 0.1);
        }

        .integration-section li:last-child {
          border-bottom: none;
        }

        .integration-section strong {
          color: #00ff88;
        }
      `}</style>
    </div>
  )
}

export default VoiceCalls
