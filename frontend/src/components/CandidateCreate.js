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
  const [submitting, setSubmitting] = useState(false);

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData({ ...formData, [name]: value });
    // Clear error for this field when user starts typing
    if (errors[name]) {
      setErrors({ ...errors, [name]: null });
    }
  };

  const handleFileChange = (e) => {
    setFormData({ ...formData, resume: e.target.files[0] });
    // Clear error for resume field
    if (errors.resume) {
      setErrors({ ...errors, resume: null });
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setSubmitting(true);
    setErrors({});

    // Client-side validation
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
    if (!formData.resume) {
      newErrors.resume = 'Resume file is required';
    }

    if (Object.keys(newErrors).length > 0) {
      setErrors(newErrors);
      setSubmitting(false);
      return;
    }

    // Prepare multipart/form-data
    const fd = new FormData();
    fd.append('full_name', formData.full_name);
    fd.append('email', formData.email);
    fd.append('applied_role', formData.applied_role);
    fd.append('resume', formData.resume);

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

      // Call parent callback with created candidate
      onCreated(response.data);
    } catch (err) {
      console.error('Error creating candidate:', err);
      
      // Handle DRF validation errors
      if (err.response && err.response.data) {
        setErrors(err.response.data);
      } else {
        setErrors({ non_field_errors: ['Failed to create candidate. Please try again.'] });
      }
    } finally {
      setSubmitting(false);
    }
  };

  const handleClose = () => {
    setFormData({
      full_name: '',
      email: '',
      applied_role: '',
      resume: null,
    });
    setErrors({});
    onClose();
  };

  if (!open) return null;

  return (
    <div
      style={{
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
      }}
      onClick={handleClose}
    >
      <div
        style={{
          backgroundColor: 'white',
          padding: '30px',
          borderRadius: '8px',
          width: '90%',
          maxWidth: '500px',
          maxHeight: '90vh',
          overflowY: 'auto',
        }}
        onClick={(e) => e.stopPropagation()}
      >
        <h2 style={{ marginTop: 0, marginBottom: '20px' }}>Create New Candidate</h2>

        <form onSubmit={handleSubmit}>
          {/* Display non-field errors */}
          {errors.non_field_errors && (
            <div style={{ color: 'red', marginBottom: '15px' }}>
              {errors.non_field_errors.map((error, idx) => (
                <div key={idx}>{error}</div>
              ))}
            </div>
          )}

          {/* Full Name */}
          <div style={{ marginBottom: '15px' }}>
            <label style={{ display: 'block', marginBottom: '5px', fontWeight: 'bold' }}>
              Full Name *
            </label>
            <input
              type="text"
              name="full_name"
              value={formData.full_name}
              onChange={handleInputChange}
              style={{
                width: '100%',
                padding: '8px',
                boxSizing: 'border-box',
                border: errors.full_name ? '1px solid red' : '1px solid #ccc',
                borderRadius: '4px',
              }}
            />
            {errors.full_name && (
              <div style={{ color: 'red', fontSize: '14px', marginTop: '5px' }}>
                {Array.isArray(errors.full_name) ? errors.full_name.join(', ') : errors.full_name}
              </div>
            )}
          </div>

          {/* Email */}
          <div style={{ marginBottom: '15px' }}>
            <label style={{ display: 'block', marginBottom: '5px', fontWeight: 'bold' }}>
              Email *
            </label>
            <input
              type="email"
              name="email"
              value={formData.email}
              onChange={handleInputChange}
              style={{
                width: '100%',
                padding: '8px',
                boxSizing: 'border-box',
                border: errors.email ? '1px solid red' : '1px solid #ccc',
                borderRadius: '4px',
              }}
            />
            {errors.email && (
              <div style={{ color: 'red', fontSize: '14px', marginTop: '5px' }}>
                {Array.isArray(errors.email) ? errors.email.join(', ') : errors.email}
              </div>
            )}
          </div>

          {/* Applied Role */}
          <div style={{ marginBottom: '15px' }}>
            <label style={{ display: 'block', marginBottom: '5px', fontWeight: 'bold' }}>
              Applied Role *
            </label>
            <input
              type="text"
              name="applied_role"
              value={formData.applied_role}
              onChange={handleInputChange}
              style={{
                width: '100%',
                padding: '8px',
                boxSizing: 'border-box',
                border: errors.applied_role ? '1px solid red' : '1px solid #ccc',
                borderRadius: '4px',
              }}
            />
            {errors.applied_role && (
              <div style={{ color: 'red', fontSize: '14px', marginTop: '5px' }}>
                {Array.isArray(errors.applied_role) ? errors.applied_role.join(', ') : errors.applied_role}
              </div>
            )}
          </div>

          {/* Resume File */}
          <div style={{ marginBottom: '20px' }}>
            <label style={{ display: 'block', marginBottom: '5px', fontWeight: 'bold' }}>
              Resume *
            </label>
            <input
              type="file"
              name="resume"
              onChange={handleFileChange}
              accept=".pdf,.doc,.docx,.txt"
              style={{
                width: '100%',
                padding: '8px',
                boxSizing: 'border-box',
                border: errors.resume ? '1px solid red' : '1px solid #ccc',
                borderRadius: '4px',
              }}
            />
            {errors.resume && (
              <div style={{ color: 'red', fontSize: '14px', marginTop: '5px' }}>
                {Array.isArray(errors.resume) ? errors.resume.join(', ') : errors.resume}
              </div>
            )}
            <div style={{ fontSize: '12px', color: '#666', marginTop: '5px' }}>
              Accepted formats: PDF, DOC, DOCX, TXT
            </div>
          </div>

          {/* Buttons */}
          <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '10px' }}>
            <button
              type="button"
              onClick={handleClose}
              disabled={submitting}
              style={{
                padding: '10px 20px',
                backgroundColor: '#6c757d',
                color: 'white',
                border: 'none',
                borderRadius: '4px',
                cursor: submitting ? 'not-allowed' : 'pointer',
                opacity: submitting ? 0.6 : 1,
              }}
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={submitting}
              style={{
                padding: '10px 20px',
                backgroundColor: '#28a745',
                color: 'white',
                border: 'none',
                borderRadius: '4px',
                cursor: submitting ? 'not-allowed' : 'pointer',
                opacity: submitting ? 0.6 : 1,
              }}
            >
              {submitting ? 'Creating...' : 'Create'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}

export default CandidateCreate;
