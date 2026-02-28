import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import api from '../api';
import CandidateCreate from './CandidateCreate';

const Candidates = () => {
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
      setError('Failed to load candidates');
      console.error(err);
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
    // Add the new candidate at the beginning of the list
    setCandidates([newCandidate, ...candidates]);
    setCreateModalOpen(false);
  };

  return (
    <div style={styles.container}>
      <div style={styles.header}>
        <h1 style={styles.title}>Candidates</h1>
        <div style={styles.buttonGroup}>
          <button onClick={() => setCreateModalOpen(true)} style={styles.newButton}>
            New Candidate
          </button>
          <button onClick={fetchCandidates} style={styles.refreshButton} disabled={loading}>
            Refresh
          </button>
          <button onClick={handleLogout} style={styles.logoutButton}>
            Logout
          </button>
        </div>
      </div>

      {error && <div style={styles.error}>{error}</div>}

      {loading && <div style={styles.loading}>Loading candidates...</div>}

      {!loading && candidates.length === 0 && (
        <div style={styles.empty}>
          No candidates found. Click "New Candidate" to add one.
        </div>
      )}

      {!loading && candidates.length > 0 && (
        <div style={styles.tableContainer}>
          <table style={styles.table}>
            <thead>
              <tr>
                <th style={styles.th}>Full Name</th>
                <th style={styles.th}>Email</th>
                <th style={styles.th}>Applied Role</th>
                <th style={styles.th}>Resume</th>
                <th style={styles.th}>Created At</th>
              </tr>
            </thead>
            <tbody>
              {candidates.map((candidate) => (
                <tr key={candidate.id} style={styles.tr}>
                  <td style={styles.td}>{candidate.full_name}</td>
                  <td style={styles.td}>{candidate.email}</td>
                  <td style={styles.td}>{candidate.applied_role}</td>
                  <td style={styles.td}>
                    {candidate.resume && (
                      <a
                        href={candidate.resume}
                        target="_blank"
                        rel="noopener noreferrer"
                        style={styles.link}
                      >
                        View Resume
                      </a>
                    )}
                  </td>
                  <td style={styles.td}>
                    {new Date(candidate.created_at).toLocaleDateString()}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      <CandidateCreate
        open={createModalOpen}
        onClose={() => setCreateModalOpen(false)}
        onCreated={handleCandidateCreated}
      />
    </div>
  );
};

const styles = {
  container: {
    padding: '2rem',
    maxWidth: '1200px',
    margin: '0 auto',
  },
  header: {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: '2rem',
  },
  title: {
    fontSize: '28px',
    fontWeight: 'bold',
    margin: 0,
  },
  buttonGroup: {
    display: 'flex',
    gap: '0.5rem',
  },
  newButton: {
    backgroundColor: '#28a745',
    color: 'white',
    padding: '0.5rem 1rem',
    border: 'none',
    borderRadius: '4px',
    cursor: 'pointer',
    fontWeight: '500',
  },
  refreshButton: {
    backgroundColor: '#007bff',
    color: 'white',
    padding: '0.5rem 1rem',
    border: 'none',
    borderRadius: '4px',
    cursor: 'pointer',
    fontWeight: '500',
  },
  logoutButton: {
    backgroundColor: '#dc3545',
    color: 'white',
    padding: '0.5rem 1rem',
    border: 'none',
    borderRadius: '4px',
    cursor: 'pointer',
    fontWeight: '500',
  },
  error: {
    backgroundColor: '#fee',
    color: '#c33',
    padding: '1rem',
    borderRadius: '4px',
    marginBottom: '1rem',
  },
  loading: {
    textAlign: 'center',
    padding: '2rem',
    color: '#666',
  },
  empty: {
    textAlign: 'center',
    padding: '3rem',
    color: '#666',
    backgroundColor: '#f5f5f5',
    borderRadius: '4px',
  },
  tableContainer: {
    overflowX: 'auto',
    backgroundColor: 'white',
    borderRadius: '4px',
    boxShadow: '0 2px 4px rgba(0,0,0,0.1)',
  },
  table: {
    width: '100%',
    borderCollapse: 'collapse',
  },
  th: {
    textAlign: 'left',
    padding: '1rem',
    borderBottom: '2px solid #ddd',
    backgroundColor: '#f8f9fa',
    fontWeight: '600',
  },
  tr: {
    borderBottom: '1px solid #eee',
  },
  td: {
    padding: '1rem',
  },
  link: {
    color: '#007bff',
    textDecoration: 'none',
  },
};

export default Candidates;
