function Datasets() {
  const datasets = [
    { name: 'customer-data.csv', size: '2.4 MB', uploaded: '2024-11-15' },
    { name: 'knowledge-base.json', size: '1.8 MB', uploaded: '2024-11-18' },
    { name: 'training-set.txt', size: '3.2 MB', uploaded: '2024-11-20' },
  ];

  return (
    <div className="page">
      <div className="page-header">
        <h1 className="page-title">Datasets</h1>
        <p className="page-subtitle">Manage your training data and knowledge bases</p>
      </div>

      <div className="card">
        <h2 className="card-title">Upload New Dataset</h2>
        <div className="file-upload">
          <input type="file" id="dataset-upload" />
          <label htmlFor="dataset-upload">
            <div style={{ fontSize: '3rem', marginBottom: '1rem' }}>📁</div>
            <div>Click to upload or drag and drop</div>
            <div style={{ fontSize: '0.85rem', color: 'var(--text-secondary)', marginTop: '0.5rem' }}>
              Supported formats: CSV, JSON, TXT, PDF
            </div>
          </label>
        </div>
      </div>

      <div className="card">
        <h2 className="card-title">Existing Datasets</h2>
        <ul className="flow-list">
          {datasets.map((dataset, idx) => (
            <li key={idx} className="flow-item">
              <div>
                <div className="flow-name">{dataset.name}</div>
                <div className="flow-meta">
                  {dataset.size} • Uploaded {dataset.uploaded}
                </div>
              </div>
              <div>
                <button className="btn btn-secondary" style={{ marginRight: '0.5rem' }}>
                  View
                </button>
                <button className="btn btn-secondary">Delete</button>
              </div>
            </li>
          ))}
        </ul>
      </div>

      <div className="grid-2">
        <div className="card">
          <h3 className="card-title">Dataset Statistics</h3>
          <div className="card-content">
            <p><strong>Total Datasets:</strong> {datasets.length}</p>
            <p><strong>Total Size:</strong> 7.4 MB</p>
            <p><strong>Last Upload:</strong> 2024-11-20</p>
          </div>
        </div>
        <div className="card">
          <h3 className="card-title">Processing Queue</h3>
          <div className="card-content">
            <p>No datasets currently processing</p>
          </div>
        </div>
      </div>
    </div>
  );
}

export default Datasets;
