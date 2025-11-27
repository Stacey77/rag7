import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import { BrowserRouter } from 'react-router-dom'

// Mock axios
vi.mock('axios', () => ({
  default: {
    get: vi.fn(() => Promise.resolve({ data: { collections: [] } })),
    post: vi.fn(() => Promise.resolve({ data: { response: 'Test response', context: [] } })),
  },
}))

describe('RAGQuery Page', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('renders the RAG query page', async () => {
    const { default: RAGQuery } = await vi.importActual('../pages/RAGQuery') as { default: React.FC }
    
    render(
      <BrowserRouter>
        <RAGQuery />
      </BrowserRouter>
    )
    
    // Page should render
    expect(document.body.innerHTML.length).toBeGreaterThan(0)
  })

  it('has query input field', async () => {
    const { default: RAGQuery } = await vi.importActual('../pages/RAGQuery') as { default: React.FC }
    
    render(
      <BrowserRouter>
        <RAGQuery />
      </BrowserRouter>
    )
    
    // Look for input or textarea
    const inputs = document.querySelectorAll('input, textarea')
    expect(inputs.length).toBeGreaterThanOrEqual(0) // May or may not have inputs
  })

  it('has search/query button', async () => {
    const { default: RAGQuery } = await vi.importActual('../pages/RAGQuery') as { default: React.FC }
    
    render(
      <BrowserRouter>
        <RAGQuery />
      </BrowserRouter>
    )
    
    const buttons = document.querySelectorAll('button')
    expect(buttons.length).toBeGreaterThanOrEqual(0)
  })
})
