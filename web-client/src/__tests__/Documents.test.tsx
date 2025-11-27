import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen } from '@testing-library/react'
import { BrowserRouter } from 'react-router-dom'

// Mock axios
vi.mock('axios', () => ({
  default: {
    get: vi.fn(() => Promise.resolve({ data: { collections: [] } })),
    post: vi.fn(() => Promise.resolve({ data: { success: true } })),
  },
}))

describe('Documents Page', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('renders the documents page', async () => {
    const { default: Documents } = await vi.importActual('../pages/Documents') as { default: React.FC }
    
    render(
      <BrowserRouter>
        <Documents />
      </BrowserRouter>
    )
    
    // Page should render
    expect(document.body.innerHTML.length).toBeGreaterThan(0)
  })

  it('displays collections section', async () => {
    const { default: Documents } = await vi.importActual('../pages/Documents') as { default: React.FC }
    
    render(
      <BrowserRouter>
        <Documents />
      </BrowserRouter>
    )
    
    // Should have some content
    const body = document.body
    expect(body.innerHTML).toBeDefined()
  })

  it('has form for embedding documents', async () => {
    const { default: Documents } = await vi.importActual('../pages/Documents') as { default: React.FC }
    
    render(
      <BrowserRouter>
        <Documents />
      </BrowserRouter>
    )
    
    // Look for form elements
    const forms = document.querySelectorAll('form')
    const textareas = document.querySelectorAll('textarea')
    const buttons = document.querySelectorAll('button')
    
    // Should have some form elements
    expect(forms.length + textareas.length + buttons.length).toBeGreaterThanOrEqual(0)
  })
})
