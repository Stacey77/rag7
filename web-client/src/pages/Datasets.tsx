import { useState } from 'react'

interface Dataset {
  id: number
  name: string
  size: string
  records: number
  lastModified: string
  status: 'ready' | 'processing' | 'error'
}

function Datasets() {
  const [datasets] = useState<Dataset[]>([
    { id: 1, name: 'customer_support.jsonl', size: '2.3 MB', records: 5420, lastModified: '2024-01-15', status: 'ready' },
    { id: 2, name: 'product_docs.pdf', size: '15.7 MB', records: 342, lastModified: '2024-01-14', status: 'ready' },
    { id: 3, name: 'faq_database.csv', size: '1.1 MB', records: 890, lastModified: '2024-01-12', status: 'ready' },
    { id: 4, name: 'training_data_v2.jsonl', size: '45.2 MB', records: 12500, lastModified: '2024-01-10', status: 'processing' },
  ])

  const [uploadProgress, setUploadProgress] = useState<number | null>(null)

  const handleFileUpload = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0]
    if (file) {
      // Simulate upload progress
      setUploadProgress(0)
      const interval = setInterval(() => {
        setUploadProgress((prev) => {
          if (prev === null || prev >= 100) {
            clearInterval(interval)
            setTimeout(() => setUploadProgress(null), 1000)
            return 100
          }
          return prev + 10
        })
      }, 200)
    }
  }

  return (
    <div>
      <header className="page-header">
        <h1>Datasets</h1>
        <p style={{ color: 'var(--text-muted)' }}>Manage your training data and knowledge bases</p>
      </header>

      <div className="grid grid-3">
        <div className="card">
          <h2>Total Datasets</h2>
          <p style={{ fontSize: '2.5rem', color: 'var(--primary)' }}>{datasets.length}</p>
        </div>
        <div className="card">
          <h2>Total Records</h2>
          <p style={{ fontSize: '2.5rem', color: 'var(--secondary)' }}>
            {datasets.reduce((acc, d) => acc + d.records, 0).toLocaleString()}
          </p>
        </div>
        <div className="card">
          <h2>Total Size</h2>
          <p style={{ fontSize: '2.5rem', color: 'var(--accent)' }}>64.3 MB</p>
        </div>
      </div>

      <div className="card">
        <h2>Upload Dataset</h2>
        <div 
          style={{ 
            border: '2px dashed var(--primary)',
            borderRadius: '12px',
            padding: '2rem',
            textAlign: 'center',
            marginTop: '1rem'
          }}
        >
          <input
            type="file"
            id="file-upload"
            style={{ display: 'none' }}
            onChange={handleFileUpload}
            accept=".json,.jsonl,.csv,.pdf,.txt"
          />
          <label htmlFor="file-upload" style={{ cursor: 'pointer' }}>
            <div style={{ fontSize: '3rem', marginBottom: '1rem' }}>📤</div>
            <p>Drag & drop files here or click to browse</p>
            <p style={{ color: 'var(--text-muted)', marginTop: '0.5rem' }}>
              Supports: JSON, JSONL, CSV, PDF, TXT
            </p>
          </label>
          {uploadProgress !== null && (
            <div style={{ marginTop: '1rem' }}>
              <div 
                style={{ 
                  width: '100%', 
                  height: '10px', 
                  background: 'var(--surface-light)',
                  borderRadius: '5px',
                  overflow: 'hidden'
                }}
              >
                <div 
                  style={{ 
                    width: `${uploadProgress}%`, 
                    height: '100%', 
                    background: 'var(--primary)',
                    transition: 'width 0.2s'
                  }}
                />
              </div>
              <p style={{ marginTop: '0.5rem' }}>{uploadProgress}%</p>
            </div>
          )}
        </div>
      </div>

      <div className="card">
        <h2>Your Datasets</h2>
        <table style={{ width: '100%', borderCollapse: 'collapse', marginTop: '1rem' }}>
          <thead>
            <tr style={{ borderBottom: '1px solid var(--primary)' }}>
              <th style={{ textAlign: 'left', padding: '0.75rem' }}>Name</th>
              <th style={{ textAlign: 'left', padding: '0.75rem' }}>Size</th>
              <th style={{ textAlign: 'left', padding: '0.75rem' }}>Records</th>
              <th style={{ textAlign: 'left', padding: '0.75rem' }}>Modified</th>
              <th style={{ textAlign: 'left', padding: '0.75rem' }}>Status</th>
              <th style={{ textAlign: 'left', padding: '0.75rem' }}>Actions</th>
            </tr>
          </thead>
          <tbody>
            {datasets.map((dataset) => (
              <tr key={dataset.id} style={{ borderBottom: '1px solid var(--surface-light)' }}>
                <td style={{ padding: '0.75rem' }}>{dataset.name}</td>
                <td style={{ padding: '0.75rem' }}>{dataset.size}</td>
                <td style={{ padding: '0.75rem' }}>{dataset.records.toLocaleString()}</td>
                <td style={{ padding: '0.75rem' }}>{dataset.lastModified}</td>
                <td style={{ padding: '0.75rem' }}>
                  <span className={`status status-${dataset.status === 'ready' ? 'success' : dataset.status === 'processing' ? 'warning' : 'error'}`}>
                    {dataset.status}
                  </span>
                </td>
                <td style={{ padding: '0.75rem' }}>
                  <button className="btn" style={{ padding: '0.5rem 1rem', marginRight: '0.5rem' }}>
                    View
                  </button>
                  <button className="btn btn-secondary" style={{ padding: '0.5rem 1rem' }}>
                    Delete
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}

export default Datasets
