import React, { useState } from 'react';
import api from '../api';
import './CandidateCreate.css';

const CandidateCreate = ({ open, onClose, onCreated }) => {
  const [formData, setFormData] = useState({
    full_name: '',
    email: '',
    applied_role: '',
  });
  const [resume, setResume] = useState(null);
  const [errors, setErrors] = useState({});
  const [loading, setLoading] = useState(false);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData({
      ...formData,
      [name]: value,
    });
    // Clear error for this field
    if (errors[name]) {
      setErrors({ ...errors, [name]: null });
    }
  };

  const handleFileChange = (e) => {
    const file = e.target.files[0];
    setResume(file);
    if (errors.resume) {
      setErrors({ ...errors, resume: null });
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setErrors({});
    setLoading(true);

    try {
      const formDataToSend = new FormData();
      formDataToSend.append('full_name', formData.full_name);
      formDataToSend.append('email', formData.email);
      formDataToSend.append('applied_role', formData.applied_role);
      if (resume) {
        formDataToSend.append('resume', resume);
      }

      const response = await api.post('candidates/', formDataToSend, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });

      // Reset form
      setFormData({
        full_name: '',
        email: '',
        applied_role: '',
      });
      setResume(null);
      
      // Call onCreated with the new candidate
      if (onCreated) {
        onCreated(response.data);
      }
      
      // Close modal
      onClose();
    } catch (error) {
      if (error.response && error.response.data) {
        setErrors(error.response.data);
      } else {
        setErrors({ general: 'An error occurred. Please try again.' });
      }
    } finally {
      setLoading(false);
    }
  };

  const handleCancel = () => {
    setFormData({
      full_name: '',
      email: '',
      applied_role: '',
    });
    setResume(null);
    setErrors({});
    onClose();
  };

  if (!open) return null;

  return (
    <div className="modal-overlay" onClick={handleCancel}>
      <div className="modal-content" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <h2>Create New Candidate</h2>
          <button className="close-button" onClick={handleCancel}>
            &times;
          </button>
        </div>

        <form onSubmit={handleSubmit} className="candidate-form">
          {errors.general && (
            <div className="error-message general-error">{errors.general}</div>
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
              required
              className={errors.full_name ? 'error' : ''}
            />
            {errors.full_name && (
              <div className="error-message">
                {Array.isArray(errors.full_name) ? errors.full_name[0] : errors.full_name}
              </div>
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
              required
              className={errors.email ? 'error' : ''}
            />
            {errors.email && (
              <div className="error-message">
                {Array.isArray(errors.email) ? errors.email[0] : errors.email}
              </div>
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
              required
              className={errors.applied_role ? 'error' : ''}
            />
            {errors.applied_role && (
              <div className="error-message">
                {Array.isArray(errors.applied_role) ? errors.applied_role[0] : errors.applied_role}
              </div>
            )}
          </div>

          <div className="form-group">
            <label htmlFor="resume">
              Resume <span className="required">*</span>
            </label>
            <input
              type="file"
              id="resume"
              name="resume"
              onChange={handleFileChange}
              accept=".pdf,.doc,.docx"
              required
              className={errors.resume ? 'error' : ''}
            />
            {resume && <div className="file-name">Selected: {resume.name}</div>}
            {errors.resume && (
              <div className="error-message">
                {Array.isArray(errors.resume) ? errors.resume[0] : errors.resume}
              </div>
            )}
          </div>

          <div className="form-actions">
            <button type="button" onClick={handleCancel} className="btn-cancel">
              Cancel
            </button>
            <button type="submit" disabled={loading} className="btn-submit">
              {loading ? 'Creating...' : 'Create Candidate'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default CandidateCreate;
