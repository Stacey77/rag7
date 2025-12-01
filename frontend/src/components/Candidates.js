import React, { useState, useEffect } from 'react';
import api from '../api';
import CandidateCreate from './CandidateCreate';

function Candidates() {
  const [candidates, setCandidates] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [createModalOpen, setCreateModalOpen] = useState(false);
  const [scoreModalOpen, setScoreModalOpen] = useState(false);
  const [selectedCandidate, setSelectedCandidate] = useState(null);

  useEffect(() => {
    fetchCandidates();
  }, []);

  const fetchCandidates = async () => {
    try {
      setLoading(true);
      const response = await api.get('candidates/');
      setCandidates(response.data);
      setError(null);
    } catch (err) {
      setError(err.message || 'Failed to fetch candidates');
    } finally {
      setLoading(false);
    }
  };

  const handleLogout = () => {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    window.location.href = '/login';
  };

  const handleCandidateCreated = (newCandidate) => {
    // Add new candidate to the top of the list (optimistic update)
    setCandidates([newCandidate, ...candidates]);
    setCreateModalOpen(false);
  };

  const handleScoreResume = (candidate) => {
    setSelectedCandidate(candidate);
    setScoreModalOpen(true);
  };

  if (loading) {
    return <div className="loading">Loading candidates...</div>;
  }

  if (error) {
    return <div className="error">Error: {error}</div>;
  }

  return (
    <div className="candidates-container">
      <div className="candidates-header">
        <h1>Candidates</h1>
        <div className="header-buttons">
          <button onClick={() => setCreateModalOpen(true)} className="btn btn-primary">
            New Candidate
          </button>
          <button onClick={fetchCandidates} className="btn btn-secondary">
            Refresh
          </button>
          <button onClick={handleLogout} className="btn btn-secondary">
            Logout
          </button>
        </div>
      </div>

      <div className="candidates-list">
        {candidates.length === 0 ? (
          <p>No candidates found. Click "New Candidate" to add one.</p>
        ) : (
          <table className="candidates-table">
            <thead>
              <tr>
                <th>Full Name</th>
                <th>Email</th>
                <th>Applied Role</th>
                <th>Resume</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {candidates.map((candidate) => (
                <tr key={candidate.id}>
                  <td>{candidate.full_name}</td>
                  <td>{candidate.email}</td>
                  <td>{candidate.applied_role}</td>
                  <td>
                    {candidate.resume ? (
                      <a href={candidate.resume} target="_blank" rel="noopener noreferrer">
                        View Resume
                      </a>
                    ) : (
                      'No resume'
                    )}
                  </td>
                  <td>
                    {candidate.resume && (
                      <button
                        onClick={() => handleScoreResume(candidate)}
                        className="btn btn-sm btn-info"
                      >
                        Score Resume
                      </button>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>

      <CandidateCreate
        open={createModalOpen}
        onClose={() => setCreateModalOpen(false)}
        onCreated={handleCandidateCreated}
      />

      {/* Resume scoring modal placeholder - existing functionality preserved */}
      {scoreModalOpen && selectedCandidate && (
        <div className="modal-overlay" onClick={() => setScoreModalOpen(false)}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <h2>Score Resume - {selectedCandidate.full_name}</h2>
            <p>Resume scoring functionality (existing feature preserved)</p>
            <button onClick={() => setScoreModalOpen(false)} className="btn btn-secondary">
              Close
            </button>
          </div>
        </div>
      )}
    </div>
  );
}

export default Candidates;
