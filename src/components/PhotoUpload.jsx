import React, { useState, useRef } from 'react'
import apiService from '../services/api'
import '../styles/PhotoUpload.css'

function PhotoUpload({ onPhotoUpload, userPhoto }) {
  const [uploading, setUploading] = useState(false)
  const [error, setError] = useState(null)
  const [preview, setPreview] = useState(null)
  const fileInputRef = useRef(null)

  const handleFileSelect = async (event) => {
    const file = event.target.files[0]
    if (!file) return

    // Validate file type
    if (!file.type.startsWith('image/')) {
      setError('Please select an image file')
      return
    }

    // Create preview
    const reader = new FileReader()
    reader.onloadend = () => {
      setPreview(reader.result)
    }
    reader.readAsDataURL(file)

    // Upload to backend
    setUploading(true)
    setError(null)

    try {
      const response = await apiService.uploadPhoto(file)
      onPhotoUpload(response.filename, response.body_model)
    } catch (err) {
      setError(err.message || 'Failed to upload photo')
    } finally {
      setUploading(false)
    }
  }

  const handleButtonClick = () => {
    fileInputRef.current?.click()
  }

  return (
    <div className="photo-upload">
      <h2>Step 1: Upload Your Photo</h2>
      <p className="upload-instructions">
        Upload a full-body photo for the best virtual try-on experience
      </p>

      <div className="upload-area">
        {preview ? (
          <div className="preview-container">
            <img src={preview} alt="Preview" className="preview-image" />
            <button 
              onClick={handleButtonClick}
              className="change-photo-btn"
            >
              Change Photo
            </button>
          </div>
        ) : (
          <div className="upload-placeholder" onClick={handleButtonClick}>
            <div className="upload-icon">📸</div>
            <p>Click to upload your photo</p>
            <p className="upload-hint">Supports JPG, PNG, GIF</p>
          </div>
        )}

        <input
          ref={fileInputRef}
          type="file"
          accept="image/*"
          onChange={handleFileSelect}
          style={{ display: 'none' }}
        />
      </div>

      {uploading && (
        <div className="upload-status">
          <div className="spinner"></div>
          <p>Analyzing your photo...</p>
        </div>
      )}

      {error && (
        <div className="error-message">
          {error}
        </div>
      )}

      {userPhoto && !uploading && (
        <div className="success-message">
          ✓ Photo uploaded successfully! You can now select garments to try on.
        </div>
      )}
    </div>
  )
}

export default PhotoUpload
