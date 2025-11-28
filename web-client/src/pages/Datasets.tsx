import { useState } from 'react'

interface Dataset {
  id: string
  name: string
  type: string
  size: string
  lastModified: string
  status: 'active' | 'processing' | 'archived'
}

function Datasets() {
  const [datasets] = useState<Dataset[]>([
    {
      id: '1',
      name: 'Customer Support Logs',
      type: 'Text',
      size: '2.4 GB',
      lastModified: '2024-01-15',
      status: 'active'
    },
    {
      id: '2',
      name: 'Product Documentation',
      type: 'Documents',
      size: '156 MB',
      lastModified: '2024-01-14',
      status: 'active'
    },
    {
      id: '3',
      name: 'Training Data Q4',
      type: 'CSV',
      size: '892 MB',
      lastModified: '2024-01-10',
      status: 'processing'
    },
    {
      id: '4',
      name: 'Historical Analytics',
      type: 'JSON',
      size: '3.1 GB',
      lastModified: '2024-01-05',
      status: 'archived'
    }
  ])

  return (
    <div className="datasets">
      <div className="flex-between mb-2">
        <div>
          <h1>Datasets</h1>
          <p>Manage your training and knowledge base data</p>
        </div>
        <button>Upload Dataset</button>
      </div>

      <div className="card">
        <div className="datasets-header flex-between mb-1">
          <h3>Available Datasets</h3>
          <div className="flex gap-1">
            <input 
              type="text" 
              placeholder="Search datasets..."
              style={{ width: '300px' }}
            />
            <select>
              <option>All Types</option>
              <option>Text</option>
              <option>Documents</option>
              <option>CSV</option>
              <option>JSON</option>
            </select>
          </div>
        </div>

        <div className="datasets-list">
          {datasets.map(dataset => (
            <div key={dataset.id} className="dataset-item card">
              <div className="flex-between">
                <div className="flex gap-1">
                  <div className="dataset-icon">📊</div>
                  <div>
                    <h4>{dataset.name}</h4>
                    <p className="dataset-meta">
                      {dataset.type} • {dataset.size} • Modified {dataset.lastModified}
                    </p>
                  </div>
                </div>
                <div className="flex gap-1">
                  <span className={`badge badge-${
                    dataset.status === 'active' ? 'success' : 
                    dataset.status === 'processing' ? 'warning' : 
                    'secondary'
                  }`}>
                    {dataset.status}
                  </span>
                  <button>View</button>
                  <button>Download</button>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>

      <div className="grid grid-3 mt-2">
        <div className="card">
          <h3>Storage Usage</h3>
          <div className="storage-bar">
            <div className="storage-used" style={{ width: '67%' }}></div>
          </div>
          <p className="mt-1">6.5 GB of 10 GB used</p>
        </div>

        <div className="card">
          <h3>Total Datasets</h3>
          <div className="stat-value" style={{ fontSize: '3rem', color: 'var(--accent-cyan)' }}>
            {datasets.length}
          </div>
        </div>

        <div className="card">
          <h3>Active Processing</h3>
          <div className="stat-value" style={{ fontSize: '3rem', color: 'var(--accent-purple)' }}>
            {datasets.filter(d => d.status === 'processing').length}
          </div>
        </div>
      </div>
    </div>
  )
}

export default Datasets
