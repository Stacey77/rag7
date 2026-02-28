import { useState } from 'react'

interface Dataset {
  id: string
  name: string
  size: string
  type: string
  modified: string
}

function Datasets() {
  const [datasets] = useState<Dataset[]>([
    {
      id: '1',
      name: 'Customer Feedback',
      size: '2.5 MB',
      type: 'CSV',
      modified: '2 hours ago',
    },
    {
      id: '2',
      name: 'Product Catalog',
      size: '5.1 MB',
      type: 'JSON',
      modified: '1 day ago',
    },
    {
      id: '3',
      name: 'Training Data',
      size: '120 MB',
      type: 'JSONL',
      modified: '3 days ago',
    },
    {
      id: '4',
      name: 'User Analytics',
      size: '8.7 MB',
      type: 'CSV',
      modified: '1 week ago',
    },
  ])

  return (
    <div className="datasets fade-in">
      <div className="page-header">
        <h1 className="glow">DATASETS</h1>
        <p className="text-secondary">Manage your data sources and training sets</p>
      </div>

      <div className="card">
        <div className="card-header flex justify-between items-center">
          <h3 className="card-title">Available Datasets</h3>
          <button className="btn btn-accent">
            <span style={{ marginRight: '8px' }}>➕</span>
            Upload Dataset
          </button>
        </div>

        <div className="datasets-grid">
          {datasets.map(dataset => (
            <div key={dataset.id} className="dataset-item">
              <div className="dataset-icon">📁</div>
              <div className="dataset-info">
                <h4 className="dataset-name">{dataset.name}</h4>
                <div className="dataset-meta">
                  <span className="badge badge-info">{dataset.type}</span>
                  <span className="text-muted">{dataset.size}</span>
                </div>
                <p className="text-muted" style={{ fontSize: '0.85rem', marginTop: '4px' }}>
                  Modified {dataset.modified}
                </p>
              </div>
              <div className="dataset-actions">
                <button className="btn-icon" title="View">👁️</button>
                <button className="btn-icon" title="Download">⬇️</button>
                <button className="btn-icon" title="Delete">🗑️</button>
              </div>
            </div>
          ))}
        </div>
      </div>

      <div className="grid grid-3 mt-3">
        <div className="card">
          <div className="card-header">
            <h3 className="card-title">Storage</h3>
          </div>
          <div className="text-center" style={{ padding: 'var(--spacing-lg)' }}>
            <div className="stat-value">136.3 MB</div>
            <div className="stat-label">Used</div>
            <div className="mt-2">
              <div className="progress-bar">
                <div className="progress-fill" style={{ width: '27%' }}></div>
              </div>
              <p className="text-muted" style={{ marginTop: '8px', fontSize: '0.85rem' }}>
                27% of 500 MB
              </p>
            </div>
          </div>
        </div>

        <div className="card">
          <div className="card-header">
            <h3 className="card-title">Total Datasets</h3>
          </div>
          <div className="text-center" style={{ padding: 'var(--spacing-lg)' }}>
            <div className="stat-value">{datasets.length}</div>
            <div className="stat-label">Active</div>
          </div>
        </div>

        <div className="card">
          <div className="card-header">
            <h3 className="card-title">Last Upload</h3>
          </div>
          <div className="text-center" style={{ padding: 'var(--spacing-lg)' }}>
            <div className="stat-value">2h</div>
            <div className="stat-label">Ago</div>
          </div>
        </div>
      </div>

      <style>{`
        .datasets-grid {
          display: flex;
          flex-direction: column;
          gap: var(--spacing-md);
        }

        .dataset-item {
          display: flex;
          align-items: center;
          gap: var(--spacing-md);
          padding: var(--spacing-md);
          background: var(--accent-bg);
          border: 1px solid var(--border-color);
          border-radius: 8px;
          transition: all 0.3s ease;
        }

        .dataset-item:hover {
          border-color: var(--primary-color);
          box-shadow: var(--border-glow);
        }

        .dataset-icon {
          font-size: 2.5rem;
          min-width: 60px;
          text-align: center;
        }

        .dataset-info {
          flex: 1;
        }

        .dataset-name {
          margin: 0 0 var(--spacing-xs) 0;
          color: var(--primary-color);
          font-size: 1.1rem;
        }

        .dataset-meta {
          display: flex;
          align-items: center;
          gap: var(--spacing-sm);
        }

        .dataset-actions {
          display: flex;
          gap: var(--spacing-sm);
        }

        .stat-value {
          font-size: 2rem;
          font-weight: 900;
          color: var(--primary-color);
          margin-bottom: var(--spacing-xs);
          text-shadow: 0 0 10px rgba(0, 212, 255, 0.5);
        }

        .stat-label {
          font-size: 0.85rem;
          color: var(--text-secondary);
          text-transform: uppercase;
          letter-spacing: 1px;
        }

        .progress-bar {
          width: 100%;
          height: 8px;
          background: var(--accent-bg);
          border-radius: 4px;
          overflow: hidden;
          border: 1px solid var(--border-color);
        }

        .progress-fill {
          height: 100%;
          background: linear-gradient(90deg, var(--primary-color), var(--accent-color));
          transition: width 0.3s ease;
        }
      `}</style>
    </div>
  )
}

export default Datasets
