import { useState } from 'react'
import './Datasets.css'

interface Dataset {
  id: string
  name: string
  size: string
  type: string
  uploaded: string
}

const Datasets = () => {
  const [datasets] = useState<Dataset[]>([])
  const [uploading, setUploading] = useState(false)

  const handleFileUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (!file) return

    setUploading(true)

    // Simulate upload
    setTimeout(() => {
      setUploading(false)
      alert(`File "${file.name}" would be uploaded to the backend`)
    }, 2000)
  }

  return (
    <div className="datasets slide-in">
      <header className="page-header">
        <h1>Datasets</h1>
        <p className="text-muted">Manage Training Data & Knowledge Bases</p>
      </header>

      <section className="upload-section card">
        <h3 className="mb-2">Upload Dataset</h3>
        <p className="text-muted mb-3">
          Upload CSV, JSON, or TXT files to use with your agents
        </p>

        <div className="upload-area">
          <div className="upload-icon">📤</div>
          <label htmlFor="file-upload" className="upload-label">
            {uploading ? 'Uploading...' : 'Click to Upload or Drag & Drop'}
          </label>
          <input
            id="file-upload"
            type="file"
            accept=".csv,.json,.txt"
            onChange={handleFileUpload}
            disabled={uploading}
            style={{ display: 'none' }}
          />
          {uploading && <div className="loading-spinner"></div>}
        </div>
      </section>

      <section className="datasets-list">
        <h2 className="mb-3">Your Datasets</h2>

        {datasets.length === 0 ? (
          <div className="empty-state card">
            <div className="empty-icon">📁</div>
            <h3>No Datasets Yet</h3>
            <p className="text-muted">
              Upload your first dataset to get started
            </p>
          </div>
        ) : (
          <div className="datasets-grid">
            {datasets.map((dataset) => (
              <div key={dataset.id} className="dataset-card card">
                <div className="dataset-header">
                  <h3>{dataset.name}</h3>
                  <span className="dataset-type">{dataset.type}</span>
                </div>
                <div className="dataset-info">
                  <div className="info-item">
                    <span className="info-label">Size:</span>
                    <span className="info-value">{dataset.size}</span>
                  </div>
                  <div className="info-item">
                    <span className="info-label">Uploaded:</span>
                    <span className="info-value">{dataset.uploaded}</span>
                  </div>
                </div>
                <div className="dataset-actions">
                  <button className="secondary">View</button>
                  <button className="secondary">Download</button>
                  <button className="secondary">Delete</button>
                </div>
              </div>
            ))}
          </div>
        )}
      </section>

      <section className="datasets-info card">
        <h3 className="mb-2">Dataset Tips</h3>
        <ul className="tips-list">
          <li>Supported formats: CSV, JSON, TXT</li>
          <li>Maximum file size: 100MB</li>
          <li>Structure your data with clear headers/keys</li>
          <li>Use consistent formatting across datasets</li>
          <li>Consider data privacy and security</li>
        </ul>
      </section>
    </div>
  )
}

export default Datasets
