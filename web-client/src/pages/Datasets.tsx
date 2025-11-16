import { useState } from 'react'

const Datasets = () => {
  const [datasets] = useState([
    { name: 'Customer Data', size: '2.4 MB', records: 1250, status: 'active' },
    { name: 'Product Catalog', size: '1.1 MB', records: 500, status: 'active' },
    { name: 'Sales History', size: '5.7 MB', records: 3400, status: 'processing' },
  ])

  return (
    <div>
      <h1>Datasets Management</h1>
      <p style={{ color: 'var(--text-secondary)', marginBottom: '2rem' }}>
        Upload and manage datasets for AI training and analysis
      </p>

      <div className="flex-between mb-3">
        <div>
          <button className="btn btn-primary" style={{ marginRight: '1rem' }}>
            ➕ Upload Dataset
          </button>
          <button className="btn btn-secondary">
            🔄 Refresh
          </button>
        </div>
        <div>
          <input 
            type="text" 
            placeholder="Search datasets..." 
            style={{ width: '300px' }}
          />
        </div>
      </div>

      <div className="card">
        <div className="card-header">
          <h3>Available Datasets</h3>
        </div>
        <div className="flow-list">
          {datasets.map((dataset, idx) => (
            <div key={idx} className="flow-item">
              <div>
                <h4 style={{ margin: 0, marginBottom: '0.25rem' }}>{dataset.name}</h4>
                <div style={{ fontSize: '0.85rem', color: 'var(--text-secondary)' }}>
                  {dataset.size} • {dataset.records} records
                </div>
              </div>
              <div style={{ display: 'flex', gap: '0.5rem', alignItems: 'center' }}>
                <span className={`status-badge status-${dataset.status === 'active' ? 'online' : 'processing'}`}>
                  {dataset.status}
                </span>
                <button className="btn btn-secondary" style={{ padding: '0.5rem 1rem' }}>
                  View
                </button>
              </div>
            </div>
          ))}
        </div>
      </div>

      <div className="grid grid-2 mt-4">
        <div className="card">
          <div className="card-header">
            <h3>Upload New Dataset</h3>
          </div>
          <div className="file-upload">
            <div style={{ fontSize: '3rem', marginBottom: '1rem' }}>📁</div>
            <p>Drag and drop files here</p>
            <p style={{ fontSize: '0.85rem', color: 'var(--text-secondary)' }}>
              Supported formats: CSV, JSON, TXT
            </p>
          </div>
        </div>

        <div className="card">
          <div className="card-header">
            <h3>Dataset Statistics</h3>
          </div>
          <div className="mb-2">
            <div style={{ color: 'var(--text-secondary)' }}>Total Datasets</div>
            <h2 style={{ margin: '0.5rem 0' }}>{datasets.length}</h2>
          </div>
          <div className="mb-2">
            <div style={{ color: 'var(--text-secondary)' }}>Total Size</div>
            <h2 style={{ margin: '0.5rem 0' }}>9.2 MB</h2>
          </div>
          <div>
            <div style={{ color: 'var(--text-secondary)' }}>Total Records</div>
            <h2 style={{ margin: '0.5rem 0' }}>5,150</h2>
          </div>
        </div>
      </div>
    </div>
  )
}

export default Datasets
