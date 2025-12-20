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
      setError('Failed to fetch candidates');
      console.error('Error fetching candidates:', err);
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
    // Optimistically insert new candidate at the top of the list
    setCandidates([newCandidate, ...candidates]);
    setCreateModalOpen(false);
  };

  return (
    <div style={{ maxWidth: '1200px', margin: '20px auto', padding: '20px' }}>
      <div style={{ 
        display: 'flex', 
        justifyContent: 'space-between', 
        alignItems: 'center',
        marginBottom: '20px',
        borderBottom: '2px solid #ccc',
        paddingBottom: '10px'
      }}>
        <h1>Candidates</h1>
        <div>
          <button
            onClick={() => setCreateModalOpen(true)}
            style={{
              padding: '10px 20px',
              backgroundColor: '#28a745',
              color: 'white',
              border: 'none',
              borderRadius: '4px',
              cursor: 'pointer',
              marginRight: '10px'
            }}
          >
            New Candidate
          </button>
          <button
            onClick={fetchCandidates}
            style={{
              padding: '10px 20px',
              backgroundColor: '#007bff',
              color: 'white',
              border: 'none',
              borderRadius: '4px',
              cursor: 'pointer',
              marginRight: '10px'
            }}
          >
            Refresh
          </button>
          <button
            onClick={handleLogout}
            style={{
              padding: '10px 20px',
              backgroundColor: '#dc3545',
              color: 'white',
              border: 'none',
              borderRadius: '4px',
              cursor: 'pointer'
            }}
          >
            Logout
          </button>
        </div>
      </div>

      {error && <div style={{ color: 'red', marginBottom: '10px' }}>{error}</div>}

      {loading ? (
        <p>Loading candidates...</p>
      ) : candidates.length === 0 ? (
        <p>No candidates found. Click "New Candidate" to add one.</p>
      ) : (
        <table style={{ width: '100%', borderCollapse: 'collapse' }}>
          <thead>
            <tr style={{ backgroundColor: '#f8f9fa' }}>
              <th style={{ border: '1px solid #dee2e6', padding: '12px', textAlign: 'left' }}>Name</th>
              <th style={{ border: '1px solid #dee2e6', padding: '12px', textAlign: 'left' }}>Email</th>
              <th style={{ border: '1px solid #dee2e6', padding: '12px', textAlign: 'left' }}>Applied Role</th>
              <th style={{ border: '1px solid #dee2e6', padding: '12px', textAlign: 'left' }}>Resume</th>
              <th style={{ border: '1px solid #dee2e6', padding: '12px', textAlign: 'left' }}>Created At</th>
            </tr>
          </thead>
          <tbody>
            {candidates.map((candidate) => (
              <tr key={candidate.id}>
                <td style={{ border: '1px solid #dee2e6', padding: '12px' }}>{candidate.full_name}</td>
                <td style={{ border: '1px solid #dee2e6', padding: '12px' }}>{candidate.email}</td>
                <td style={{ border: '1px solid #dee2e6', padding: '12px' }}>{candidate.applied_role}</td>
                <td style={{ border: '1px solid #dee2e6', padding: '12px' }}>
                  {candidate.resume && (
                    <a href={candidate.resume} target="_blank" rel="noopener noreferrer">
                      View Resume
                    </a>
                  )}
                </td>
                <td style={{ border: '1px solid #dee2e6', padding: '12px' }}>
                  {new Date(candidate.created_at).toLocaleDateString()}
                </td>
              </tr>
            ))}
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
