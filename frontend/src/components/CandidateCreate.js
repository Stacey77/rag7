import React, { useState } from 'react';
import api from '../api';

function CandidateCreate({ open, onClose, onCreated }) {
  const [formData, setFormData] = useState({
    full_name: '',
    email: '',
    applied_role: '',
  });
  const [resume, setResume] = useState(null);
  const [errors, setErrors] = useState({});
  const [submitting, setSubmitting] = useState(false);

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData({ ...formData, [name]: value });
    // Clear error for this field when user types
    if (errors[name]) {
      setErrors({ ...errors, [name]: undefined });
    }
  };

  const handleFileChange = (e) => {
    const file = e.target.files[0];
    if (file) {
      // Validate file type
      const allowedTypes = [
        'application/pdf',
        'text/plain',
        'application/msword',
        'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
      ];
      if (!allowedTypes.includes(file.type)) {
        setErrors({ ...errors, resume: 'Only .pdf, .txt, .doc, .docx files are allowed' });
        setResume(null);
        e.target.value = null;
        return;
      }
      setResume(file);
      if (errors.resume) {
        setErrors({ ...errors, resume: undefined });
      }
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setErrors({});
    setSubmitting(true);

    try {
      // Create FormData for multipart/form-data
      const data = new FormData();
      data.append('full_name', formData.full_name);
      data.append('email', formData.email);
      data.append('applied_role', formData.applied_role);
      if (resume) {
        data.append('resume', resume);
      }

      const response = await api.post('candidates/', data, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });

      // Success - call onCreated with the created candidate
      onCreated(response.data);
      
      // Reset form
      setFormData({
        full_name: '',
        email: '',
        applied_role: '',
      });
      setResume(null);
    } catch (err) {
      // Handle DRF-style validation errors
      if (err.response?.data) {
        setErrors(err.response.data);
      } else {
        setErrors({ non_field_errors: ['Failed to create candidate'] });
      }
    } finally {
      setSubmitting(false);
    }
  };

  const handleClose = () => {
    // Reset form and close
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
    <div
      style={{
        position: 'fixed',
        top: 0,
        left: 0,
        width: '100%',
        height: '100%',
        backgroundColor: 'rgba(0, 0, 0, 0.5)',
        display: 'flex',
        justifyContent: 'center',
        alignItems: 'center',
        zIndex: 1000,
      }}
      onClick={handleClose}
    >
      <div
        style={{
          backgroundColor: 'white',
          padding: '30px',
          borderRadius: '8px',
          width: '500px',
          maxWidth: '90%',
          maxHeight: '90%',
          overflow: 'auto',
        }}
        onClick={(e) => e.stopPropagation()}
      >
        <h2 style={{ marginTop: 0 }}>Create New Candidate</h2>
        
        <form onSubmit={handleSubmit}>
          {errors.non_field_errors && (
            <div style={{ color: 'red', marginBottom: '10px' }}>
              {errors.non_field_errors.join(', ')}
            </div>
          )}

          <div style={{ marginBottom: '15px' }}>
            <label style={{ display: 'block', marginBottom: '5px', fontWeight: 'bold' }}>
              Full Name *
            </label>
            <input
              type="text"
              name="full_name"
              value={formData.full_name}
              onChange={handleInputChange}
              required
              style={{
                width: '100%',
                padding: '8px',
                border: errors.full_name ? '1px solid red' : '1px solid #ccc',
                borderRadius: '4px',
              }}
            />
            {errors.full_name && (
              <div style={{ color: 'red', fontSize: '12px', marginTop: '5px' }}>
                {Array.isArray(errors.full_name) ? errors.full_name.join(', ') : errors.full_name}
              </div>
            )}
          </div>

          <div style={{ marginBottom: '15px' }}>
            <label style={{ display: 'block', marginBottom: '5px', fontWeight: 'bold' }}>
              Email *
            </label>
            <input
              type="email"
              name="email"
              value={formData.email}
              onChange={handleInputChange}
              required
              style={{
                width: '100%',
                padding: '8px',
                border: errors.email ? '1px solid red' : '1px solid #ccc',
                borderRadius: '4px',
              }}
            />
            {errors.email && (
              <div style={{ color: 'red', fontSize: '12px', marginTop: '5px' }}>
                {Array.isArray(errors.email) ? errors.email.join(', ') : errors.email}
              </div>
            )}
          </div>

          <div style={{ marginBottom: '15px' }}>
            <label style={{ display: 'block', marginBottom: '5px', fontWeight: 'bold' }}>
              Applied Role *
            </label>
            <input
              type="text"
              name="applied_role"
              value={formData.applied_role}
              onChange={handleInputChange}
              required
              style={{
                width: '100%',
                padding: '8px',
                border: errors.applied_role ? '1px solid red' : '1px solid #ccc',
                borderRadius: '4px',
              }}
            />
            {errors.applied_role && (
              <div style={{ color: 'red', fontSize: '12px', marginTop: '5px' }}>
                {Array.isArray(errors.applied_role) ? errors.applied_role.join(', ') : errors.applied_role}
              </div>
            )}
          </div>

          <div style={{ marginBottom: '15px' }}>
            <label style={{ display: 'block', marginBottom: '5px', fontWeight: 'bold' }}>
              Resume (optional)
            </label>
            <input
              type="file"
              accept=".pdf,.txt,.doc,.docx"
              onChange={handleFileChange}
              style={{
                width: '100%',
                padding: '8px',
                border: errors.resume ? '1px solid red' : '1px solid #ccc',
                borderRadius: '4px',
              }}
            />
            <div style={{ fontSize: '12px', color: '#666', marginTop: '5px' }}>
              Accepted formats: .pdf, .txt, .doc, .docx
            </div>
            {errors.resume && (
              <div style={{ color: 'red', fontSize: '12px', marginTop: '5px' }}>
                {Array.isArray(errors.resume) ? errors.resume.join(', ') : errors.resume}
              </div>
            )}
          </div>

          <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '10px', marginTop: '20px' }}>
            <button
              type="button"
              onClick={handleClose}
              disabled={submitting}
              style={{
                padding: '10px 20px',
                border: '1px solid #ccc',
                borderRadius: '4px',
                backgroundColor: 'white',
                cursor: submitting ? 'not-allowed' : 'pointer',
              }}
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={submitting}
              style={{
                padding: '10px 20px',
                border: 'none',
                borderRadius: '4px',
                backgroundColor: submitting ? '#ccc' : '#28a745',
                color: 'white',
                cursor: submitting ? 'not-allowed' : 'pointer',
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
