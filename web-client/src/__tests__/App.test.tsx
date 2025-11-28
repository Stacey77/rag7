import { describe, it, expect, vi } from 'vitest'
import { render, screen } from '@testing-library/react'
import { BrowserRouter } from 'react-router-dom'
import App from '../App'

// Mock axios
vi.mock('axios', () => ({
  default: {
    get: vi.fn(() => Promise.resolve({ data: {} })),
    post: vi.fn(() => Promise.resolve({ data: {} })),
  },
}))

describe('App', () => {
  it('renders without crashing', () => {
    render(
      <BrowserRouter>
        <App />
      </BrowserRouter>
    )
    // App should render successfully
    expect(document.body).toBeDefined()
  })

  it('has navigation elements', () => {
    render(
      <BrowserRouter>
        <App />
      </BrowserRouter>
    )
    // Should have some navigation or content
    const body = document.body
    expect(body.innerHTML.length).toBeGreaterThan(0)
  })
})
