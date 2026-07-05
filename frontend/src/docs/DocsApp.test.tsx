import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { beforeEach, describe, expect, it, vi } from 'vitest'
import DocsApp from './DocsApp'


describe('decision log application', () => {
  beforeEach(() => {
    window.history.replaceState({}, '', '/')
    window.scrollTo = vi.fn()
  })

  it('lists generated ADRs and searches their body and metadata', async () => {
    const user = userEvent.setup()
    window.history.replaceState({}, '', '/decisions')
    render(<DocsApp />)

    expect(screen.getByRole('heading', { name: 'Decision Log' })).toBeInTheDocument()
    expect(screen.getByText(/\d+ decisions/)).toBeInTheDocument()
    await user.type(screen.getByRole('searchbox', { name: 'Search decisions' }), 'filesystem gatekeeper')
    expect(screen.getByText('1 decision')).toBeInTheDocument()
    expect(screen.getByRole('link', { name: /Use A Filesystem-Backed Decision Log/i })).toBeInTheDocument()
  })

  it('offers decisions and the interactive API from the docs portal', () => {
    render(<DocsApp />)
    expect(screen.getByRole('heading', { name: 'Project Docs' })).toBeInTheDocument()
    expect(screen.getByRole('link', { name: /Browse decisions/ })).toHaveAttribute('href', '/decisions')
    expect(screen.getByRole('link', { name: /Open API reference/ })).toHaveAttribute('href', '/api-reference')
  })

  it('renders a direct ADR route with adjacent navigation', () => {
    window.history.replaceState({}, '', '/adr/filesystem-backed-decision-log')
    render(<DocsApp />)

    expect(screen.getByRole('heading', { name: 'Use A Filesystem-Backed Decision Log', level: 1 })).toBeInTheDocument()
    expect(screen.getByRole('navigation', { name: 'Adjacent decisions' })).toBeInTheDocument()
    expect(screen.getByText(/Keep ADR Markdown files/)).toBeInTheDocument()
  })

  it('shows a useful not-found view', () => {
    window.history.replaceState({}, '', '/adr/not-real')
    render(<DocsApp />)
    expect(screen.getByRole('heading', { name: 'Decision not found' })).toBeInTheDocument()
  })
})
