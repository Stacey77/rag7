interface SectionAgentProps {
  name: string;
  status: string;
  avatar?: string;
}

function SectionAgent({ name, status, avatar = '🤖' }: SectionAgentProps) {
  return (
    <div className="section-agent">
      <div className="agent-avatar">{avatar}</div>
      <div className="agent-info">
        <div className="agent-name">{name}</div>
        <div className="agent-status">{status}</div>
      </div>
    </div>
  );
}

export default SectionAgent;
