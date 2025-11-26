import { useState, useEffect } from 'react'
import axios from 'axios'

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

interface Collection {
  name: string
  num_entities: number
  description: string
}

function Documents() {
  const [collections, setCollections] = useState<Collection[]>([])
  const [selectedCollection, setSelectedCollection] = useState('text_embeddings')
  const [documents, setDocuments] = useState<string[]>([])
  const [newDocument, setNewDocument] = useState('')
  const [file, setFile] = useState<File | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [success, setSuccess] = useState<string | null>(null)

  useEffect(() => {
    loadCollections()
  }, [])

  const loadCollections = async () => {
    try {
      setLoading(true)
      const response = await axios.get(`${API_URL}/rag/collections`)
      setCollections(response.data.collections || [])
    } catch (err: any) {
      setError(`Failed to load collections: ${err.message}`)
      console.error('Error loading collections:', err)
    } finally {
      setLoading(false)
    }
  }

  const handleEmbedText = async (e: React.FormEvent) => {
    e.preventDefault()
    
    if (!newDocument.trim()) {
      setError('Please enter some text to embed')
      return
    }

    try {
      setLoading(true)
      setError(null)
      setSuccess(null)

      const formData = new FormData()
      formData.append('texts', newDocument)
      formData.append('collection_name', selectedCollection)
      
      const response = await axios.post(`${API_URL}/rag/embed`, formData)
      
      setSuccess(`Successfully embedded ${response.data.count} document(s)`)
      setNewDocument('')
      setDocuments([...documents, newDocument])
      
      // Refresh collections to update counts
      setTimeout(loadCollections, 500)
    } catch (err: any) {
      setError(`Embedding failed: ${err.response?.data?.detail || err.message}`)
      console.error('Embedding error:', err)
    } finally {
      setLoading(false)
    }
  }

  const handleEmbedImage = async (e: React.FormEvent) => {
    e.preventDefault()
    
    if (!file) {
      setError('Please select an image file')
      return
    }

    try {
      setLoading(true)
      setError(null)
      setSuccess(null)

      const formData = new FormData()
      formData.append('file', file)
      formData.append('collection_name', 'image_embeddings')
      
      const response = await axios.post(`${API_URL}/rag/embed_image`, formData)
      
      setSuccess(`Successfully embedded image: ${response.data.filename}`)
      setFile(null)
      
      // Reset file input
      const fileInput = document.getElementById('file-input') as HTMLInputElement
      if (fileInput) fileInput.value = ''
      
      setTimeout(loadCollections, 500)
    } catch (err: any) {
      setError(`Image embedding failed: ${err.response?.data?.detail || err.message}`)
      console.error('Image embedding error:', err)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div style={{ padding: '20px', maxWidth: '1200px', margin: '0 auto' }}>
      <h1 style={{ 
        fontSize: '2.5rem', 
        marginBottom: '10px',
        background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
        WebkitBackgroundClip: 'text',
        WebkitTextFillColor: 'transparent'
      }}>
        📚 Document Management
      </h1>
      <p style={{ color: '#888', marginBottom: '30px' }}>
        Embed text documents and images into the vector database for semantic search
      </p>

      {/* Collections Overview */}
      <div style={{ marginBottom: '30px' }}>
        <h2 style={{ fontSize: '1.5rem', marginBottom: '15px', color: '#667eea' }}>
          📊 Collections
        </h2>
        <div style={{ 
          display: 'grid', 
          gridTemplateColumns: 'repeat(auto-fill, minmax(250px, 1fr))', 
          gap: '15px' 
        }}>
          {collections.map((collection) => (
            <div
              key={collection.name}
              style={{
                background: 'rgba(255, 255, 255, 0.05)',
                border: '1px solid rgba(255, 255, 255, 0.1)',
                borderRadius: '10px',
                padding: '20px',
                cursor: 'pointer',
                transition: 'all 0.3s',
                ...(selectedCollection === collection.name && {
                  borderColor: '#667eea',
                  background: 'rgba(102, 126, 234, 0.1)'
                })
              }}
              onClick={() => setSelectedCollection(collection.name)}
              onMouseEnter={(e) => {
                if (selectedCollection !== collection.name) {
                  e.currentTarget.style.background = 'rgba(255, 255, 255, 0.08)'
                }
              }}
              onMouseLeave={(e) => {
                if (selectedCollection !== collection.name) {
                  e.currentTarget.style.background = 'rgba(255, 255, 255, 0.05)'
                }
              }}
            >
              <div style={{ 
                fontSize: '2rem', 
                marginBottom: '10px' 
              }}>
                {collection.name.includes('image') ? '🖼️' : '📄'}
              </div>
              <h3 style={{ 
                fontSize: '1.1rem', 
                marginBottom: '8px',
                color: '#fff'
              }}>
                {collection.name}
              </h3>
              <p style={{ 
                fontSize: '0.9rem', 
                color: '#888',
                marginBottom: '5px'
              }}>
                {collection.description || 'No description'}
              </p>
              <div style={{
                marginTop: '10px',
                padding: '5px 10px',
                background: 'rgba(102, 126, 234, 0.2)',
                borderRadius: '15px',
                display: 'inline-block',
                fontSize: '0.85rem',
                color: '#667eea'
              }}>
                {collection.num_entities.toLocaleString()} embeddings
              </div>
            </div>
          ))}
          
          {collections.length === 0 && !loading && (
            <div style={{
              gridColumn: '1 / -1',
              textAlign: 'center',
              padding: '40px',
              color: '#666'
            }}>
              No collections found. Embed some documents to create collections.
            </div>
          )}
        </div>
      </div>

      {/* Messages */}
      {error && (
        <div style={{
          padding: '15px',
          background: 'rgba(255, 0, 0, 0.1)',
          border: '1px solid rgba(255, 0, 0, 0.3)',
          borderRadius: '5px',
          color: '#ff6b6b',
          marginBottom: '20px'
        }}>
          ❌ {error}
        </div>
      )}

      {success && (
        <div style={{
          padding: '15px',
          background: 'rgba(0, 255, 0, 0.1)',
          border: '1px solid rgba(0, 255, 0, 0.3)',
          borderRadius: '5px',
          color: '#51cf66',
          marginBottom: '20px'
        }}>
          ✅ {success}
        </div>
      )}

      {/* Embed Text Documents */}
      <div style={{ marginBottom: '30px' }}>
        <h2 style={{ fontSize: '1.5rem', marginBottom: '15px', color: '#667eea' }}>
          📝 Embed Text Documents
        </h2>
        <form onSubmit={handleEmbedText}>
          <div style={{ 
            background: 'rgba(255, 255, 255, 0.05)', 
            padding: '20px', 
            borderRadius: '10px',
            border: '1px solid rgba(255, 255, 255, 0.1)'
          }}>
            <div style={{ marginBottom: '15px' }}>
              <label style={{ display: 'block', marginBottom: '8px', color: '#aaa' }}>
                Collection:
              </label>
              <select
                value={selectedCollection}
                onChange={(e) => setSelectedCollection(e.target.value)}
                style={{
                  width: '100%',
                  padding: '10px',
                  background: 'rgba(0, 0, 0, 0.3)',
                  border: '1px solid rgba(255, 255, 255, 0.2)',
                  borderRadius: '5px',
                  color: '#fff',
                  fontSize: '1rem'
                }}
              >
                <option value="text_embeddings">text_embeddings</option>
                {collections.filter(c => !c.name.includes('image')).map(c => (
                  <option key={c.name} value={c.name}>{c.name}</option>
                ))}
              </select>
            </div>

            <div style={{ marginBottom: '15px' }}>
              <label style={{ display: 'block', marginBottom: '8px', color: '#aaa' }}>
                Document Text:
              </label>
              <textarea
                value={newDocument}
                onChange={(e) => setNewDocument(e.target.value)}
                placeholder="Enter your document text here... You can embed multiple paragraphs."
                rows={6}
                style={{
                  width: '100%',
                  padding: '12px',
                  background: 'rgba(0, 0, 0, 0.3)',
                  border: '1px solid rgba(255, 255, 255, 0.2)',
                  borderRadius: '5px',
                  color: '#fff',
                  fontSize: '1rem',
                  fontFamily: 'inherit',
                  resize: 'vertical'
                }}
              />
            </div>

            <button
              type="submit"
              disabled={loading}
              style={{
                padding: '10px 30px',
                background: loading ? '#555' : 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                border: 'none',
                borderRadius: '5px',
                color: '#fff',
                cursor: loading ? 'not-allowed' : 'pointer',
                fontSize: '1rem',
                fontWeight: 'bold',
                transition: 'all 0.3s'
              }}
            >
              {loading ? '🔄 Embedding...' : '🚀 Embed Document'}
            </button>
          </div>
        </form>
      </div>

      {/* Embed Images */}
      <div style={{ marginBottom: '30px' }}>
        <h2 style={{ fontSize: '1.5rem', marginBottom: '15px', color: '#667eea' }}>
          🖼️ Embed Images
        </h2>
        <form onSubmit={handleEmbedImage}>
          <div style={{ 
            background: 'rgba(255, 255, 255, 0.05)', 
            padding: '20px', 
            borderRadius: '10px',
            border: '1px solid rgba(255, 255, 255, 0.1)'
          }}>
            <div style={{ marginBottom: '15px' }}>
              <label style={{ display: 'block', marginBottom: '8px', color: '#aaa' }}>
                Select Image:
              </label>
              <input
                id="file-input"
                type="file"
                accept="image/*"
                onChange={(e) => setFile(e.target.files?.[0] || null)}
                style={{
                  width: '100%',
                  padding: '10px',
                  background: 'rgba(0, 0, 0, 0.3)',
                  border: '1px solid rgba(255, 255, 255, 0.2)',
                  borderRadius: '5px',
                  color: '#fff',
                  fontSize: '1rem'
                }}
              />
              <p style={{ 
                fontSize: '0.85rem', 
                color: '#666', 
                marginTop: '5px' 
              }}>
                Supported formats: JPG, PNG, GIF, etc.
              </p>
            </div>

            {file && (
              <div style={{ 
                marginBottom: '15px',
                padding: '10px',
                background: 'rgba(102, 126, 234, 0.1)',
                borderRadius: '5px'
              }}>
                <strong style={{ color: '#667eea' }}>Selected:</strong> {file.name} ({(file.size / 1024).toFixed(2)} KB)
              </div>
            )}

            <button
              type="submit"
              disabled={loading || !file}
              style={{
                padding: '10px 30px',
                background: loading || !file ? '#555' : 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                border: 'none',
                borderRadius: '5px',
                color: '#fff',
                cursor: loading || !file ? 'not-allowed' : 'pointer',
                fontSize: '1rem',
                fontWeight: 'bold',
                transition: 'all 0.3s'
              }}
            >
              {loading ? '🔄 Embedding...' : '🚀 Embed Image'}
            </button>
          </div>
        </form>
      </div>

      {/* Recently Embedded Documents */}
      {documents.length > 0 && (
        <div>
          <h2 style={{ fontSize: '1.5rem', marginBottom: '15px', color: '#667eea' }}>
            📋 Recently Embedded (This Session)
          </h2>
          <div style={{ display: 'grid', gap: '10px' }}>
            {documents.map((doc, idx) => (
              <div
                key={idx}
                style={{
                  background: 'rgba(255, 255, 255, 0.05)',
                  border: '1px solid rgba(255, 255, 255, 0.1)',
                  borderRadius: '5px',
                  padding: '15px',
                  fontSize: '0.9rem',
                  color: '#ccc'
                }}
              >
                {doc.length > 200 ? doc.substring(0, 200) + '...' : doc}
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}

export default Documents
