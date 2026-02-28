import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import api from '../api';
import CandidateCreate from './CandidateCreate';

function Candidates() {
  const [candidates, setCandidates] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [createModalOpen, setCreateModalOpen] = useState(false);
  const navigate = useNavigate();

  const fetchCandidates = async () => {
    try {
      setLoading(true);
      const response = await api.get('candidates/');
      setCandidates(response.data);
      setError('');
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to fetch candidates');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchCandidates();
  }, []);

  const handleLogout = () => {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    navigate('/login');
  };

  const handleCandidateCreated = (newCandidate) => {
    // Optimistic update: add new candidate at top of list
    setCandidates([newCandidate, ...candidates]);
    setCreateModalOpen(false);
  };

  return (
    <div style={{ padding: '20px' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' }}>
        <h1>Candidates</h1>
        <div>
          <button
            onClick={() => setCreateModalOpen(true)}
            style={{ marginRight: '10px', padding: '10px 20px', backgroundColor: '#28a745', color: 'white', border: 'none', cursor: 'pointer' }}
          >
            New Candidate
          </button>
          <button
            onClick={fetchCandidates}
            style={{ marginRight: '10px', padding: '10px 20px' }}
          >
            Refresh
          </button>
          <button
            onClick={handleLogout}
            style={{ padding: '10px 20px' }}
          >
            Logout
          </button>
        </div>
      </div>

      {error && <div style={{ color: 'red', marginBottom: '20px' }}>{error}</div>}
      
      {loading ? (
        <div>Loading...</div>
      ) : (
        <table style={{ width: '100%', borderCollapse: 'collapse' }}>
          <thead>
            <tr style={{ backgroundColor: '#f0f0f0' }}>
              <th style={{ padding: '10px', textAlign: 'left', border: '1px solid #ddd' }}>Name</th>
              <th style={{ padding: '10px', textAlign: 'left', border: '1px solid #ddd' }}>Email</th>
              <th style={{ padding: '10px', textAlign: 'left', border: '1px solid #ddd' }}>Applied Role</th>
              <th style={{ padding: '10px', textAlign: 'left', border: '1px solid #ddd' }}>Resume</th>
              <th style={{ padding: '10px', textAlign: 'left', border: '1px solid #ddd' }}>Created At</th>
            </tr>
          </thead>
          <tbody>
            {candidates.length === 0 ? (
              <tr>
                <td colSpan="5" style={{ padding: '20px', textAlign: 'center' }}>
                  No candidates found. Click "New Candidate" to create one.
                </td>
              </tr>
            ) : (
              candidates.map((candidate) => (
                <tr key={candidate.id}>
                  <td style={{ padding: '10px', border: '1px solid #ddd' }}>{candidate.full_name}</td>
                  <td style={{ padding: '10px', border: '1px solid #ddd' }}>{candidate.email}</td>
                  <td style={{ padding: '10px', border: '1px solid #ddd' }}>{candidate.applied_role}</td>
                  <td style={{ padding: '10px', border: '1px solid #ddd' }}>
                    {candidate.resume ? (
                      <a href={candidate.resume} target="_blank" rel="noopener noreferrer">
                        View Resume
                      </a>
                    ) : (
                      'No resume'
                    )}
                  </td>
                  <td style={{ padding: '10px', border: '1px solid #ddd' }}>
                    {new Date(candidate.created_at).toLocaleString()}
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      )}

      <CandidateCreate
        open={createModalOpen}
        onClose={() => setCreateModalOpen(false)}
        onCreated={handleCandidateCreated}
      />
    </div>
  );
}

export default Candidates;
