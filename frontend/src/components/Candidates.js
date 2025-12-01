import React, { useState, useEffect } from 'react';
import api from '../api';
import CandidateCreate from './CandidateCreate';
import './Candidates.css';

function Candidates({ onLogout }) {
  const [candidates, setCandidates] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [showCreateModal, setShowCreateModal] = useState(false);

  const fetchCandidates = async () => {
    try {
      setLoading(true);
      const response = await api.get('candidates/');
      setCandidates(response.data);
      setError('');
    } catch (err) {
      setError('Failed to fetch candidates. Please try again.');
      console.error('Error fetching candidates:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchCandidates();
  }, []);

  const handleCandidateCreated = (newCandidate) => {
    setCandidates([newCandidate, ...candidates]);
    setShowCreateModal(false);
  };

  const handleLogout = () => {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    onLogout();
  };

  return (
    <div className="candidates-container">
      <div className="candidates-header">
        <h1>Candidates</h1>
        <div className="header-actions">
          <button onClick={() => setShowCreateModal(true)} className="btn-primary">
            New Candidate
          </button>
          <button onClick={fetchCandidates} className="btn-secondary">
            Refresh
          </button>
          <button onClick={handleLogout} className="btn-danger">
            Logout
          </button>
        </div>
      </div>

      {error && <div className="error-message">{error}</div>}

      {loading ? (
        <div className="loading">Loading candidates...</div>
      ) : (
        <div className="candidates-list">
          {candidates.length === 0 ? (
            <div className="empty-state">
              <p>No candidates found. Click "New Candidate" to add one.</p>
            </div>
          ) : (
            <table className="candidates-table">
              <thead>
                <tr>
                  <th>Full Name</th>
                  <th>Email</th>
                  <th>Applied Role</th>
                  <th>Resume</th>
                  <th>Created At</th>
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
                        <span className="no-resume">No resume</span>
                      )}
                    </td>
                    <td>{new Date(candidate.created_at).toLocaleDateString()}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </div>
      )}

      <CandidateCreate
        open={showCreateModal}
        onClose={() => setShowCreateModal(false)}
        onCreated={handleCandidateCreated}
      />
    </div>
  );
}

export default Candidates;
