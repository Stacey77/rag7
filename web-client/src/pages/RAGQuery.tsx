import { useState } from 'react'
import axios from 'axios'

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

interface SearchResult {
  id: string
  text: string
  score: number
  metadata?: any
}

interface RAGResponse {
  query: string
  retrieved_context: string[]
  response: string
  top_k: number
}

function RAGQuery() {
  const [query, setQuery] = useState('')
  const [searchResults, setSearchResults] = useState<SearchResult[]>([])
  const [ragResponse, setRagResponse] = useState<RAGResponse | null>(null)
  const [topK, setTopK] = useState(5)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [mode, setMode] = useState<'search' | 'rag'>('rag')

  const handleSearch = async (e: React.FormEvent) => {
    e.preventDefault()
    
    if (!query.trim()) {
      setError('Please enter a search query')
      return
    }

    try {
      setLoading(true)
      setError(null)
      setSearchResults([])
      setRagResponse(null)

      const formData = new FormData()
      formData.append('text', query)
      formData.append('top_k', topK.toString())
      
      const response = await axios.post(`${API_URL}/rag/search`, formData)
      
      if (response.data.results) {
        setSearchResults(response.data.results)
      }
    } catch (err: any) {
      setError(`Search failed: ${err.response?.data?.detail || err.message}`)
      console.error('Search error:', err)
    } finally {
      setLoading(false)
    }
  }

  const handleRAGQuery = async (e: React.FormEvent) => {
    e.preventDefault()
    
    if (!query.trim()) {
      setError('Please enter a query')
      return
    }

    try {
      setLoading(true)
      setError(null)
      setSearchResults([])
      setRagResponse(null)

      const formData = new FormData()
      formData.append('query', query)
      formData.append('top_k', topK.toString())
      
      const response = await axios.post(`${API_URL}/rag/query`, formData)
      setRagResponse(response.data)
    } catch (err: any) {
      setError(`RAG query failed: ${err.response?.data?.detail || err.message}`)
      console.error('RAG query error:', err)
    } finally {
      setLoading(false)
    }
  }

  const handleSubmit = mode === 'search' ? handleSearch : handleRAGQuery

  return (
    <div style={{ padding: '20px', maxWidth: '1200px', margin: '0 auto' }}>
      <h1 style={{ 
        fontSize: '2.5rem', 
        marginBottom: '10px',
        background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
        WebkitBackgroundClip: 'text',
        WebkitTextFillColor: 'transparent'
      }}>
        🔍 RAG Query Interface
      </h1>
      <p style={{ color: '#888', marginBottom: '30px' }}>
        Search your embedded documents or perform retrieval-augmented generation queries
      </p>

      {/* Mode Selector */}
      <div style={{ 
        display: 'flex', 
        gap: '10px', 
        marginBottom: '20px',
        borderBottom: '2px solid #333'
      }}>
        <button
          onClick={() => setMode('rag')}
          style={{
            padding: '10px 20px',
            background: mode === 'rag' ? 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)' : 'transparent',
            border: 'none',
            color: mode === 'rag' ? '#fff' : '#888',
            cursor: 'pointer',
            borderRadius: '5px 5px 0 0',
            fontSize: '1rem',
            fontWeight: mode === 'rag' ? 'bold' : 'normal'
          }}
        >
          RAG Query
        </button>
        <button
          onClick={() => setMode('search')}
          style={{
            padding: '10px 20px',
            background: mode === 'search' ? 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)' : 'transparent',
            border: 'none',
            color: mode === 'search' ? '#fff' : '#888',
            cursor: 'pointer',
            borderRadius: '5px 5px 0 0',
            fontSize: '1rem',
            fontWeight: mode === 'search' ? 'bold' : 'normal'
          }}
        >
          Vector Search
        </button>
      </div>

      {/* Search Form */}
      <form onSubmit={handleSubmit} style={{ marginBottom: '30px' }}>
        <div style={{ 
          background: 'rgba(255, 255, 255, 0.05)', 
          padding: '20px', 
          borderRadius: '10px',
          border: '1px solid rgba(255, 255, 255, 0.1)'
        }}>
          <div style={{ marginBottom: '15px' }}>
            <label style={{ display: 'block', marginBottom: '8px', color: '#aaa' }}>
              {mode === 'rag' ? 'Your Question:' : 'Search Query:'}
            </label>
            <textarea
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder={mode === 'rag' ? 'Ask a question about your documents...' : 'Enter search terms...'}
              rows={3}
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

          <div style={{ display: 'flex', gap: '15px', alignItems: 'center' }}>
            <div style={{ flex: '0 0 150px' }}>
              <label style={{ display: 'block', marginBottom: '5px', color: '#aaa', fontSize: '0.9rem' }}>
                Top K Results:
              </label>
              <input
                type="number"
                value={topK}
                onChange={(e) => setTopK(Math.max(1, Math.min(20, parseInt(e.target.value) || 5)))}
                min="1"
                max="20"
                style={{
                  width: '100%',
                  padding: '8px',
                  background: 'rgba(0, 0, 0, 0.3)',
                  border: '1px solid rgba(255, 255, 255, 0.2)',
                  borderRadius: '5px',
                  color: '#fff',
                  fontSize: '1rem'
                }}
              />
            </div>

            <button
              type="submit"
              disabled={loading}
              style={{
                marginTop: 'auto',
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
              {loading ? '🔄 Processing...' : mode === 'rag' ? '🚀 Query RAG' : '🔍 Search'}
            </button>
          </div>
        </div>
      </form>

      {/* Error Display */}
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

      {/* RAG Response */}
      {ragResponse && (
        <div style={{ marginBottom: '30px' }}>
          <h2 style={{ fontSize: '1.5rem', marginBottom: '15px', color: '#667eea' }}>
            💡 RAG Response
          </h2>
          <div style={{
            background: 'rgba(102, 126, 234, 0.1)',
            border: '1px solid rgba(102, 126, 234, 0.3)',
            borderRadius: '10px',
            padding: '20px'
          }}>
            <div style={{ marginBottom: '15px' }}>
              <strong style={{ color: '#aaa' }}>Query:</strong>
              <p style={{ marginTop: '5px', color: '#fff' }}>{ragResponse.query}</p>
            </div>
            <div style={{ marginBottom: '15px' }}>
              <strong style={{ color: '#aaa' }}>Response:</strong>
              <p style={{ 
                marginTop: '5px', 
                color: '#fff', 
                fontSize: '1.1rem',
                lineHeight: '1.6'
              }}>
                {ragResponse.response}
              </p>
            </div>
            {ragResponse.retrieved_context && ragResponse.retrieved_context.length > 0 && (
              <div>
                <strong style={{ color: '#aaa' }}>Retrieved Context ({ragResponse.retrieved_context.length} documents):</strong>
                <div style={{ marginTop: '10px' }}>
                  {ragResponse.retrieved_context.map((ctx, idx) => (
                    <div
                      key={idx}
                      style={{
                        padding: '10px',
                        background: 'rgba(0, 0, 0, 0.2)',
                        borderLeft: '3px solid #667eea',
                        marginBottom: '8px',
                        borderRadius: '3px',
                        fontSize: '0.9rem',
                        color: '#ccc'
                      }}
                    >
                      {ctx}
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Search Results */}
      {searchResults.length > 0 && (
        <div>
          <h2 style={{ fontSize: '1.5rem', marginBottom: '15px', color: '#667eea' }}>
            📊 Search Results ({searchResults.length})
          </h2>
          <div style={{ display: 'grid', gap: '15px' }}>
            {searchResults.map((result, idx) => (
              <div
                key={result.id || idx}
                style={{
                  background: 'rgba(255, 255, 255, 0.05)',
                  border: '1px solid rgba(255, 255, 255, 0.1)',
                  borderRadius: '10px',
                  padding: '20px',
                  transition: 'all 0.3s'
                }}
                onMouseEnter={(e) => {
                  e.currentTarget.style.background = 'rgba(255, 255, 255, 0.08)'
                  e.currentTarget.style.borderColor = 'rgba(102, 126, 234, 0.5)'
                }}
                onMouseLeave={(e) => {
                  e.currentTarget.style.background = 'rgba(255, 255, 255, 0.05)'
                  e.currentTarget.style.borderColor = 'rgba(255, 255, 255, 0.1)'
                }}
              >
                <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '10px' }}>
                  <span style={{ 
                    color: '#667eea', 
                    fontWeight: 'bold',
                    fontSize: '0.9rem'
                  }}>
                    Result #{idx + 1}
                  </span>
                  <span style={{
                    padding: '3px 10px',
                    background: `rgba(102, 126, 234, ${Math.max(0.2, 1 - result.score)})`,
                    borderRadius: '12px',
                    fontSize: '0.85rem',
                    color: '#fff'
                  }}>
                    Score: {result.score.toFixed(4)}
                  </span>
                </div>
                <p style={{ 
                  color: '#fff', 
                  lineHeight: '1.6',
                  marginBottom: '8px'
                }}>
                  {result.text}
                </p>
                {result.metadata && (
                  <div style={{ 
                    fontSize: '0.85rem', 
                    color: '#888',
                    marginTop: '10px',
                    paddingTop: '10px',
                    borderTop: '1px solid rgba(255, 255, 255, 0.1)'
                  }}>
                    ID: {result.id}
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Empty State */}
      {!loading && !error && !ragResponse && searchResults.length === 0 && (
        <div style={{
          textAlign: 'center',
          padding: '60px 20px',
          color: '#666'
        }}>
          <div style={{ fontSize: '4rem', marginBottom: '20px' }}>🔍</div>
          <h3 style={{ fontSize: '1.5rem', marginBottom: '10px' }}>Ready to Search</h3>
          <p>Enter a query above to search your embedded documents or perform RAG queries</p>
        </div>
      )}
    </div>
  )
}

export default RAGQuery
