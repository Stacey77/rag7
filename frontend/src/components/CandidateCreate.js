import React, { useState } from 'react';
import api from '../api';

function CandidateCreate({ open, onClose, onCreated }) {
  const [formData, setFormData] = useState({
    full_name: '',
    email: '',
    applied_role: '',
    resume: null,
  });
  const [errors, setErrors] = useState({});
  const [loading, setLoading] = useState(false);

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
        [name]: null,
      });
    }
  };

  const handleFileChange = (e) => {
    const file = e.target.files[0];
    if (file) {
      const validTypes = [
        'application/pdf',
        'text/plain',
        'application/msword',
        'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
      ];
      const validExtensions = ['.pdf', '.txt', '.doc', '.docx'];
      const fileExtension = file.name.substring(file.name.lastIndexOf('.')).toLowerCase();

      if (!validTypes.includes(file.type) && !validExtensions.includes(fileExtension)) {
        setErrors({
          ...errors,
          resume: 'Please select a valid file (.pdf, .txt, .doc, .docx)',
        });
        return;
      }

      setFormData({
        ...formData,
        resume: file,
      });
      if (errors.resume) {
        setErrors({
          ...errors,
          resume: null,
        });
      }
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setErrors({});

    try {
      // Create FormData for multipart/form-data submission
      const submitData = new FormData();
      submitData.append('full_name', formData.full_name);
      submitData.append('email', formData.email);
      submitData.append('applied_role', formData.applied_role);
      if (formData.resume) {
        submitData.append('resume', formData.resume);
      }

      // POST to /candidates/ endpoint
      const response = await api.post('candidates/', submitData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });

      // Call onCreated with the created candidate object
      onCreated(response.data);

      // Reset form
      setFormData({
        full_name: '',
        email: '',
        applied_role: '',
        resume: null,
      });
    } catch (err) {
      // Handle DRF validation errors
      if (err.response && err.response.data) {
        setErrors(err.response.data);
      } else {
        setErrors({ non_field_errors: ['Failed to create candidate. Please try again.'] });
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
      onClose();
    }
  };

  if (!open) return null;

  return (
    <div className="modal-overlay" onClick={handleClose}>
      <div className="modal-content" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <h2>Create New Candidate</h2>
          <button
            className="modal-close"
            onClick={handleClose}
            disabled={loading}
            aria-label="Close modal"
          >
            &times;
          </button>
        </div>

        <form onSubmit={handleSubmit} className="candidate-form">
          {errors.non_field_errors && (
            <div className="error-message">
              {errors.non_field_errors.map((error, index) => (
                <p key={index}>{error}</p>
              ))}
            </div>
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
              disabled={loading}
              className={errors.full_name ? 'error' : ''}
            />
            {errors.full_name && (
              <span className="field-error">
                {Array.isArray(errors.full_name) ? errors.full_name[0] : errors.full_name}
              </span>
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
              disabled={loading}
              className={errors.email ? 'error' : ''}
            />
            {errors.email && (
              <span className="field-error">
                {Array.isArray(errors.email) ? errors.email[0] : errors.email}
              </span>
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
              disabled={loading}
              className={errors.applied_role ? 'error' : ''}
            />
            {errors.applied_role && (
              <span className="field-error">
                {Array.isArray(errors.applied_role)
                  ? errors.applied_role[0]
                  : errors.applied_role}
              </span>
            )}
          </div>

          <div className="form-group">
            <label htmlFor="resume">Resume (optional)</label>
            <input
              type="file"
              id="resume"
              name="resume"
              onChange={handleFileChange}
              accept=".pdf,.txt,.doc,.docx"
              disabled={loading}
              className={errors.resume ? 'error' : ''}
            />
            {formData.resume && (
              <span className="file-name">{formData.resume.name}</span>
            )}
            {errors.resume && (
              <span className="field-error">
                {Array.isArray(errors.resume) ? errors.resume[0] : errors.resume}
              </span>
            )}
            <small className="help-text">Accepted formats: .pdf, .txt, .doc, .docx</small>
          </div>

          <div className="modal-footer">
            <button
              type="button"
              onClick={handleClose}
              className="btn btn-secondary"
              disabled={loading}
            >
              Cancel
            </button>
            <button type="submit" className="btn btn-primary" disabled={loading}>
              {loading ? 'Creating...' : 'Create Candidate'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}

export default CandidateCreate;
