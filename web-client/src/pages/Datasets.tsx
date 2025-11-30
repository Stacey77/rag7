import { useState } from 'react'

interface Dataset {
  id: string
  name: string
  size: string
  records: number
  lastModified: Date
}

const Datasets = () => {
  const [datasets] = useState<Dataset[]>([
    {
      id: '1',
      name: 'Customer Queries',
      size: '2.4 MB',
      records: 1247,
      lastModified: new Date('2024-01-15')
    },
    {
      id: '2',
      name: 'Product Descriptions',
      size: '5.8 MB',
      records: 3456,
      lastModified: new Date('2024-01-14')
    },
    {
      id: '3',
      name: 'Training Data',
      size: '18.2 MB',
      records: 9821,
      lastModified: new Date('2024-01-13')
    },
    {
      id: '4',
      name: 'Knowledge Base',
      size: '12.5 MB',
      records: 5678,
      lastModified: new Date('2024-01-12')
    },
  ])
  
  const [uploadProgress, setUploadProgress] = useState(0)
  
  const handleFileUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (file) {
      // Simulate upload
      let progress = 0
      const interval = setInterval(() => {
        progress += 10
        setUploadProgress(progress)
        if (progress >= 100) {
          clearInterval(interval)
          setTimeout(() => setUploadProgress(0), 1000)
        }
      }, 200)
    }
  }
  
  return (
    <div className="page-container fade-in">
      <h1>Datasets</h1>
      <p style={{ marginBottom: '2rem' }}>
        Manage your training data and knowledge bases.
      </p>
      
      <div className="card">
        <div className="card-header">
          <h3 className="card-title">Upload Dataset</h3>
        </div>
        
        <div className="input-group">
          <label className="input-label">Dataset Name</label>
          <input type="text" className="input" placeholder="Enter dataset name..." />
        </div>
        
        <div className="input-group">
          <label className="input-label">Dataset Type</label>
          <select className="select">
            <option>Training Data</option>
            <option>Knowledge Base</option>
            <option>Query Logs</option>
            <option>Custom</option>
          </select>
        </div>
        
        <div className="input-group">
          <label className="input-label">Upload File</label>
          <input 
            type="file" 
            className="input" 
            accept=".json,.csv,.txt"
            onChange={handleFileUpload}
          />
        </div>
        
        {uploadProgress > 0 && (
          <div style={{ marginBottom: '1rem' }}>
            <div style={{ 
              height: '8px', 
              background: 'var(--bg-tertiary)', 
              borderRadius: '4px',
              overflow: 'hidden'
            }}>
              <div style={{
                height: '100%',
                width: `${uploadProgress}%`,
                background: 'var(--accent-primary)',
                transition: 'width 0.3s ease',
                boxShadow: '0 0 10px var(--accent-primary)'
              }} />
            </div>
            <div style={{ textAlign: 'center', marginTop: '0.5rem', fontSize: '0.9rem' }}>
              {uploadProgress}% uploaded
            </div>
          </div>
        )}
        
        <button className="btn">Upload Dataset</button>
      </div>
      
      <div className="card">
        <div className="card-header">
          <h3 className="card-title">Available Datasets</h3>
        </div>
        
        <div style={{ overflowX: 'auto' }}>
          <table style={{ width: '100%', borderCollapse: 'collapse' }}>
            <thead>
              <tr style={{ borderBottom: '2px solid var(--border-color)' }}>
                <th style={{ padding: '1rem', textAlign: 'left', color: 'var(--accent-primary)' }}>Name</th>
                <th style={{ padding: '1rem', textAlign: 'left', color: 'var(--accent-primary)' }}>Size</th>
                <th style={{ padding: '1rem', textAlign: 'left', color: 'var(--accent-primary)' }}>Records</th>
                <th style={{ padding: '1rem', textAlign: 'left', color: 'var(--accent-primary)' }}>Last Modified</th>
                <th style={{ padding: '1rem', textAlign: 'left', color: 'var(--accent-primary)' }}>Actions</th>
              </tr>
            </thead>
            <tbody>
              {datasets.map(dataset => (
                <tr 
                  key={dataset.id}
                  style={{ 
                    borderBottom: '1px solid var(--border-color)',
                    transition: 'background 0.3s ease'
                  }}
                  onMouseEnter={(e) => e.currentTarget.style.background = 'var(--bg-tertiary)'}
                  onMouseLeave={(e) => e.currentTarget.style.background = 'transparent'}
                >
                  <td style={{ padding: '1rem' }}>{dataset.name}</td>
                  <td style={{ padding: '1rem', color: 'var(--text-secondary)' }}>{dataset.size}</td>
                  <td style={{ padding: '1rem', color: 'var(--text-secondary)' }}>
                    {dataset.records.toLocaleString()}
                  </td>
                  <td style={{ padding: '1rem', color: 'var(--text-secondary)' }}>
                    {dataset.lastModified.toLocaleDateString()}
                  </td>
                  <td style={{ padding: '1rem' }}>
                    <div className="flex-gap" style={{ gap: '0.5rem' }}>
                      <button className="btn" style={{ padding: '0.5rem 1rem', fontSize: '0.8rem' }}>
                        View
                      </button>
                      <button className="btn btn-secondary" style={{ padding: '0.5rem 1rem', fontSize: '0.8rem' }}>
                        Edit
                      </button>
                      <button className="btn btn-danger" style={{ padding: '0.5rem 1rem', fontSize: '0.8rem' }}>
                        Delete
                      </button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
      
      <div className="grid grid-3">
        <div className="card">
          <h4>Total Datasets</h4>
          <div style={{ fontSize: '2rem', fontWeight: 900, color: 'var(--accent-primary)', marginTop: '1rem' }}>
            {datasets.length}
          </div>
        </div>
        
        <div className="card">
          <h4>Total Records</h4>
          <div style={{ fontSize: '2rem', fontWeight: 900, color: 'var(--accent-secondary)', marginTop: '1rem' }}>
            {datasets.reduce((sum, d) => sum + d.records, 0).toLocaleString()}
          </div>
        </div>
        
        <div className="card">
          <h4>Total Size</h4>
          <div style={{ fontSize: '2rem', fontWeight: 900, color: 'var(--success)', marginTop: '1rem' }}>
            39 MB
          </div>
        </div>
      </div>
    </div>
  )
}

export default Datasets
