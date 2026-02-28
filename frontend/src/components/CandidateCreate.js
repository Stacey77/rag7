import React, { useState } from 'react';
import api from '../api';

const CandidateCreate = ({ open, onClose, onCreated }) => {
  const [formData, setFormData] = useState({
    full_name: '',
    email: '',
    applied_role: '',
    resume: null,
  });
  const [errors, setErrors] = useState({});
  const [loading, setLoading] = useState(false);
  const [generalError, setGeneralError] = useState('');

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData((prev) => ({
      ...prev,
      [name]: value,
    }));
    // Clear error for this field when user types
    if (errors[name]) {
      setErrors((prev) => ({ ...prev, [name]: null }));
    }
  };

  const handleFileChange = (e) => {
    const file = e.target.files[0];
    setFormData((prev) => ({
      ...prev,
      resume: file,
    }));
    if (errors.resume) {
      setErrors((prev) => ({ ...prev, resume: null }));
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setErrors({});
    setGeneralError('');
    setLoading(true);

    // Create FormData for multipart upload
    const fd = new FormData();
    fd.append('full_name', formData.full_name);
    fd.append('email', formData.email);
    fd.append('applied_role', formData.applied_role);
    if (formData.resume) {
      fd.append('resume', formData.resume);
    }

    try {
      const response = await api.post('candidates/', fd, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });
      
      // Reset form
      setFormData({
        full_name: '',
        email: '',
        applied_role: '',
        resume: null,
      });
      
      // Call the parent callback with the created candidate
      onCreated(response.data);
    } catch (err) {
      console.error('Error creating candidate:', err);
      
      if (err.response?.data) {
        // Handle field-specific errors from the API
        const apiErrors = err.response.data;
        if (typeof apiErrors === 'object') {
          setErrors(apiErrors);
        } else {
          setGeneralError('Failed to create candidate. Please try again.');
        }
      } else {
        setGeneralError('Network error. Please check your connection.');
      }
    } finally {
      setLoading(false);
    }
  };

  const handleClose = () => {
    if (!loading) {
      setFormData({
        full_name: '',
        email: '',
        applied_role: '',
        resume: null,
      });
      setErrors({});
      setGeneralError('');
      onClose();
    }
  };

  if (!open) return null;

  return (
    <div style={styles.overlay} onClick={handleClose}>
      <div style={styles.modal} onClick={(e) => e.stopPropagation()}>
        <div style={styles.header}>
          <h2 style={styles.title}>New Candidate</h2>
          <button onClick={handleClose} style={styles.closeButton} disabled={loading}>
            ×
          </button>
        </div>

        {generalError && <div style={styles.error}>{generalError}</div>}

        <form onSubmit={handleSubmit} style={styles.form}>
          <div style={styles.formGroup}>
            <label style={styles.label}>
              Full Name <span style={styles.required}>*</span>
            </label>
            <input
              type="text"
              name="full_name"
              value={formData.full_name}
              onChange={handleChange}
              required
              style={styles.input}
              disabled={loading}
            />
            {errors.full_name && (
              <div style={styles.fieldError}>{errors.full_name}</div>
            )}
          </div>

          <div style={styles.formGroup}>
            <label style={styles.label}>
              Email <span style={styles.required}>*</span>
            </label>
            <input
              type="email"
              name="email"
              value={formData.email}
              onChange={handleChange}
              required
              style={styles.input}
              disabled={loading}
            />
            {errors.email && (
              <div style={styles.fieldError}>{errors.email}</div>
            )}
          </div>

          <div style={styles.formGroup}>
            <label style={styles.label}>
              Applied Role <span style={styles.required}>*</span>
            </label>
            <input
              type="text"
              name="applied_role"
              value={formData.applied_role}
              onChange={handleChange}
              required
              style={styles.input}
              disabled={loading}
            />
            {errors.applied_role && (
              <div style={styles.fieldError}>{errors.applied_role}</div>
            )}
          </div>

          <div style={styles.formGroup}>
            <label style={styles.label}>
              Resume <span style={styles.required}>*</span>
            </label>
            <input
              type="file"
              name="resume"
              onChange={handleFileChange}
              accept=".pdf,.doc,.docx,.txt"
              required
              style={styles.fileInput}
              disabled={loading}
            />
            {errors.resume && (
              <div style={styles.fieldError}>{errors.resume}</div>
            )}
            <div style={styles.hint}>
              Accepted formats: PDF, DOC, DOCX, TXT
            </div>
          </div>

          <div style={styles.buttonGroup}>
            <button
              type="button"
              onClick={handleClose}
              style={styles.cancelButton}
              disabled={loading}
            >
              Cancel
            </button>
            <button type="submit" style={styles.submitButton} disabled={loading}>
              {loading ? 'Creating...' : 'Create Candidate'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

const styles = {
  overlay: {
    position: 'fixed',
    top: 0,
    left: 0,
    right: 0,
    bottom: 0,
    backgroundColor: 'rgba(0, 0, 0, 0.5)',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    zIndex: 1000,
  },
  modal: {
    backgroundColor: 'white',
    borderRadius: '8px',
    width: '90%',
    maxWidth: '500px',
    maxHeight: '90vh',
    overflow: 'auto',
    boxShadow: '0 4px 6px rgba(0, 0, 0, 0.1)',
  },
  header: {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
    padding: '1.5rem',
    borderBottom: '1px solid #eee',
  },
  title: {
    margin: 0,
    fontSize: '20px',
    fontWeight: '600',
  },
  closeButton: {
    background: 'none',
    border: 'none',
    fontSize: '28px',
    cursor: 'pointer',
    color: '#666',
    lineHeight: '1',
    padding: '0',
    width: '30px',
    height: '30px',
  },
  error: {
    backgroundColor: '#fee',
    color: '#c33',
    padding: '1rem',
    margin: '1rem 1.5rem 0',
    borderRadius: '4px',
  },
  form: {
    padding: '1.5rem',
  },
  formGroup: {
    marginBottom: '1.5rem',
  },
  label: {
    display: 'block',
    marginBottom: '0.5rem',
    fontWeight: '500',
    color: '#333',
  },
  required: {
    color: '#dc3545',
  },
  input: {
    width: '100%',
    padding: '0.5rem',
    border: '1px solid #ddd',
    borderRadius: '4px',
    fontSize: '16px',
    boxSizing: 'border-box',
  },
  fileInput: {
    width: '100%',
    padding: '0.5rem',
    border: '1px solid #ddd',
    borderRadius: '4px',
    fontSize: '14px',
    boxSizing: 'border-box',
  },
  fieldError: {
    color: '#dc3545',
    fontSize: '14px',
    marginTop: '0.25rem',
  },
  hint: {
    fontSize: '12px',
    color: '#666',
    marginTop: '0.25rem',
  },
  buttonGroup: {
    display: 'flex',
    justifyContent: 'flex-end',
    gap: '0.5rem',
    marginTop: '2rem',
  },
  cancelButton: {
    backgroundColor: '#6c757d',
    color: 'white',
    padding: '0.5rem 1.5rem',
    border: 'none',
    borderRadius: '4px',
    cursor: 'pointer',
    fontWeight: '500',
  },
  submitButton: {
    backgroundColor: '#28a745',
    color: 'white',
    padding: '0.5rem 1.5rem',
    border: 'none',
    borderRadius: '4px',
    cursor: 'pointer',
    fontWeight: '500',
  },
};

export default CandidateCreate;
