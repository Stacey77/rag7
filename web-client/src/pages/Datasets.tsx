import { useState } from 'react'

function Datasets() {
  const [datasets] = useState([
    { id: 1, name: 'Customer Reviews', size: '2.3 MB', records: 1543, updated: '2 hours ago' },
    { id: 2, name: 'Product Catalog', size: '5.1 MB', records: 3210, updated: '1 day ago' },
    { id: 3, name: 'Support Tickets', size: '8.7 MB', records: 5432, updated: '3 days ago' },
  ])

  return (
    <div className="page">
      <div className="page-header">
        <h1 className="page-title">Datasets</h1>
        <p className="page-description">
          Manage data sources for your AI agents
        </p>
      </div>

      <div className="card mb-3">
        <div className="card-header">
          <h2 className="card-title">Upload Dataset</h2>
        </div>
        <div className="card-content">
          <div className="form-group">
            <label className="form-label">Dataset Name</label>
            <input type="text" className="form-input" placeholder="e.g., Customer Feedback Q1 2024" />
          </div>
          <div className="form-group">
            <label className="form-label">File</label>
            <input type="file" className="form-input" accept=".csv,.json,.txt" />
          </div>
          <div className="form-group">
            <label className="form-label">Description</label>
            <textarea className="form-textarea" placeholder="Describe this dataset..."></textarea>
          </div>
          <button className="btn btn-primary">📤 Upload Dataset</button>
        </div>
      </div>

      <div className="card">
        <div className="card-header">
          <h2 className="card-title">Your Datasets</h2>
          <div className="text-muted" style={{ fontSize: '0.875rem' }}>
            {datasets.length} datasets
          </div>
        </div>
        <div className="card-content">
          <ul className="list">
            {datasets.map((dataset) => (
              <li key={dataset.id} className="list-item">
                <div>
                  <div className="list-item-title">📊 {dataset.name}</div>
                  <div className="list-item-meta">
                    {dataset.size} • {dataset.records.toLocaleString()} records • Updated {dataset.updated}
                  </div>
                </div>
                <div style={{ display: 'flex', gap: '0.5rem' }}>
                  <button className="btn btn-secondary">View</button>
                  <button className="btn btn-secondary">Export</button>
                  <button className="btn btn-secondary" style={{ color: 'var(--error-color)' }}>
                    Delete
                  </button>
                </div>
              </li>
            ))}
          </ul>
        </div>
      </div>

      <div className="grid grid-3 mt-3">
        <div className="card">
          <div className="card-header">
            <h3 className="card-title">Total Storage</h3>
          </div>
          <div className="card-content">
            <div style={{ fontSize: '1.5rem', fontWeight: 600 }}>16.1 MB</div>
            <div className="text-muted" style={{ fontSize: '0.875rem', marginTop: '0.5rem' }}>
              of 10 GB used
            </div>
          </div>
        </div>

        <div className="card">
          <div className="card-header">
            <h3 className="card-title">Total Records</h3>
          </div>
          <div className="card-content">
            <div style={{ fontSize: '1.5rem', fontWeight: 600 }}>10,185</div>
            <div className="text-muted" style={{ fontSize: '0.875rem', marginTop: '0.5rem' }}>
              across all datasets
            </div>
          </div>
        </div>

        <div className="card">
          <div className="card-header">
            <h3 className="card-title">Data Quality</h3>
          </div>
          <div className="card-content">
            <div style={{ fontSize: '1.5rem', fontWeight: 600 }}>98%</div>
            <div className="text-muted" style={{ fontSize: '0.875rem', marginTop: '0.5rem' }}>
              average quality score
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

export default Datasets
