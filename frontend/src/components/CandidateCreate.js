import React, { useState } from 'react';
import api from '../utils/api';
import './CandidateCreate.css';

function CandidateCreate({ onCreated, onCancel }) {
  const [formData, setFormData] = useState({
    full_name: '',
    email: '',
    applied_role: '',
  });
  const [resume, setResume] = useState(null);
  const [errors, setErrors] = useState({});
  const [loading, setLoading] = useState(false);
  const [generalError, setGeneralError] = useState('');

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData({
      ...formData,
      [name]: value,
    });
    // Clear error for this field when user starts typing
    if (errors[name]) {
      setErrors({
        ...errors,
        [name]: '',
      });
    }
  };

  const handleFileChange = (e) => {
    const file = e.target.files[0];
    setResume(file);
    if (errors.resume) {
      setErrors({
        ...errors,
        resume: '',
      });
    }
  };

  const validateForm = () => {
    const newErrors = {};
    
    if (!formData.full_name.trim()) {
      newErrors.full_name = 'Full name is required';
    }
    
    if (!formData.email.trim()) {
      newErrors.email = 'Email is required';
    } else if (!/\S+@\S+\.\S+/.test(formData.email)) {
      newErrors.email = 'Email is invalid';
    }
    
    if (!formData.applied_role.trim()) {
      newErrors.applied_role = 'Applied role is required';
    }
    
    return newErrors;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    const validationErrors = validateForm();
    if (Object.keys(validationErrors).length > 0) {
      setErrors(validationErrors);
      return;
    }

    setLoading(true);
    setGeneralError('');
    setErrors({});

    try {
      const fd = new FormData();
      fd.append('full_name', formData.full_name);
      fd.append('email', formData.email);
      fd.append('applied_role', formData.applied_role);
      if (resume) {
        fd.append('resume', resume);
      }

      const response = await api.post('candidates/', fd, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });

      onCreated(response.data);
    } catch (err) {
      if (err.response?.data) {
        // Handle field-specific errors from backend
        const backendErrors = err.response.data;
        if (typeof backendErrors === 'object') {
          setErrors(backendErrors);
        } else {
          setGeneralError('Failed to create candidate. Please try again.');
        }
      } else {
        setGeneralError('Network error. Please check your connection and try again.');
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="modal-overlay" onClick={onCancel}>
      <div className="modal-content" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <h2>New Candidate</h2>
          <button className="close-button" onClick={onCancel}>&times;</button>
        </div>
        
        <form onSubmit={handleSubmit} className="candidate-form">
          {generalError && (
            <div className="error-message general-error">{generalError}</div>
          )}

          <div className="form-group">
            <label htmlFor="full_name">
              Full Name <span className="required">*</span>
            </label>
            <input
              type="text"
              id="full_name"
              name="full_name"
              value={formData.full_name}
              onChange={handleChange}
              disabled={loading}
              className={errors.full_name ? 'error' : ''}
            />
            {errors.full_name && (
              <span className="field-error">{errors.full_name}</span>
            )}
          </div>

          <div className="form-group">
            <label htmlFor="email">
              Email <span className="required">*</span>
            </label>
            <input
              type="email"
              id="email"
              name="email"
              value={formData.email}
              onChange={handleChange}
              disabled={loading}
              className={errors.email ? 'error' : ''}
            />
            {errors.email && (
              <span className="field-error">{errors.email}</span>
            )}
          </div>

          <div className="form-group">
            <label htmlFor="applied_role">
              Applied Role <span className="required">*</span>
            </label>
            <input
              type="text"
              id="applied_role"
              name="applied_role"
              value={formData.applied_role}
              onChange={handleChange}
              disabled={loading}
              className={errors.applied_role ? 'error' : ''}
              placeholder="e.g., Software Engineer, Product Manager"
            />
            {errors.applied_role && (
              <span className="field-error">{errors.applied_role}</span>
            )}
          </div>

          <div className="form-group">
            <label htmlFor="resume">
              Resume (PDF or text file)
            </label>
            <input
              type="file"
              id="resume"
              name="resume"
              onChange={handleFileChange}
              disabled={loading}
              accept=".pdf,.txt,.doc,.docx"
              className={errors.resume ? 'error' : ''}
            />
            {resume && (
              <div className="file-info">
                Selected: {resume.name} ({(resume.size / 1024).toFixed(2)} KB)
              </div>
            )}
            {errors.resume && (
              <span className="field-error">{errors.resume}</span>
            )}
          </div>

          <div className="form-actions">
            <button
              type="button"
              onClick={onCancel}
              disabled={loading}
              className="btn-cancel"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={loading}
              className="btn-submit"
            >
              {loading ? 'Creating...' : 'Create Candidate'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}

export default CandidateCreate;
