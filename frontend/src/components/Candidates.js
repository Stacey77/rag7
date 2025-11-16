import React, { useState, useEffect } from 'react';
import api from '../api';
import CandidateCreate from './CandidateCreate';
import './Candidates.css';

const Candidates = () => {
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
      setError('Failed to load candidates. Please try again.');
      console.error('Error fetching candidates:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleCandidateCreated = (newCandidate) => {
    // Optimistic update: add new candidate to the top of the list
    setCandidates([newCandidate, ...candidates]);
  };

  const handleOpenScoreModal = (candidate) => {
    setSelectedCandidate(candidate);
    setScoreModalOpen(true);
  };

  const handleCloseScoreModal = () => {
    setScoreModalOpen(false);
    setSelectedCandidate(null);
  };

  const handleScoreResume = async (candidateId) => {
    try {
      // Placeholder for resume scoring logic
      const response = await api.post(`candidates/${candidateId}/score/`);
      // Update candidate in the list with new score
      setCandidates(candidates.map(c => 
        c.id === candidateId ? { ...c, score: response.data.score } : c
      ));
      handleCloseScoreModal();
    } catch (err) {
      console.error('Error scoring resume:', err);
      alert('Failed to score resume. Please try again.');
    }
  };

  if (loading) {
    return (
      <div className="candidates-container">
        <div className="loading">Loading candidates...</div>
      </div>
    );
  }

  return (
    <div className="candidates-container">
      <div className="candidates-header">
        <h1>Candidates</h1>
        <button 
          className="btn-new-candidate"
          onClick={() => setCreateModalOpen(true)}
        >
          + New Candidate
        </button>
      </div>

      {error && (
        <div className="error-banner">
          {error}
          <button onClick={fetchCandidates} className="retry-button">
            Retry
          </button>
        </div>
      )}

      {candidates.length === 0 ? (
        <div className="empty-state">
          <p>No candidates found.</p>
          <p>Click "New Candidate" to add your first candidate.</p>
        </div>
      ) : (
        <div className="candidates-list">
          <table className="candidates-table">
            <thead>
              <tr>
                <th>Name</th>
                <th>Email</th>
                <th>Applied Role</th>
                <th>Resume</th>
                <th>Score</th>
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
                      <a 
                        href={candidate.resume} 
                        target="_blank" 
                        rel="noopener noreferrer"
                        className="resume-link"
                      >
                        View Resume
                      </a>
                    ) : (
                      <span className="no-resume">No resume</span>
                    )}
                  </td>
                  <td>
                    {candidate.score !== null && candidate.score !== undefined ? (
                      <span className="score">{candidate.score}</span>
                    ) : (
                      <span className="no-score">Not scored</span>
                    )}
                  </td>
                  <td>
                    <button
                      className="btn-score"
                      onClick={() => handleOpenScoreModal(candidate)}
                      disabled={!candidate.resume}
                    >
                      Score Resume
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {/* Candidate Create Modal */}
      <CandidateCreate
        open={createModalOpen}
        onClose={() => setCreateModalOpen(false)}
        onCreated={handleCandidateCreated}
      />

      {/* Resume Scoring Modal - Placeholder */}
      {scoreModalOpen && selectedCandidate && (
        <div className="modal-overlay" onClick={handleCloseScoreModal}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h2>Score Resume</h2>
              <button className="close-button" onClick={handleCloseScoreModal}>
                &times;
              </button>
            </div>
            <div className="modal-body">
              <p>
                Score resume for <strong>{selectedCandidate.full_name}</strong>?
              </p>
              <div className="form-actions">
                <button 
                  className="btn-cancel"
                  onClick={handleCloseScoreModal}
                >
                  Cancel
                </button>
                <button 
                  className="btn-submit"
                  onClick={() => handleScoreResume(selectedCandidate.id)}
                >
                  Score
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default Candidates;
