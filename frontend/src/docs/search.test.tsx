import { render, screen } from '@testing-library/react'
import { describe, expect, it } from 'vitest'
import { excerpt, filterRecords, highlight, stateFromUrl, stateToUrl, terms } from './search'
import type { AdrRecord, SearchState } from './types'

const record = (overrides: Partial<AdrRecord>): AdrRecord => ({
  schemaVersion: 1,
  id: '0001',
  slug: 'local-first',
  title: 'Build Local First',
  status: 'accepted',
  date: '2026-07-03',
  category: 'architecture',
  tags: ['local-first'],
  keywords: ['offline application'],
  supersedes: [],
  supersededBy: [],
  markdown: '# ADR 0001: Build Local First',
  searchText: '0001 Build Local First accepted architecture local-first offline application private portable browser tool',
  sourcePath: 'docs/adr/0001-local-first.md',
  ...overrides,
})

const state = (overrides: Partial<SearchState> = {}): SearchState => ({ query: '', status: '', category: '', tag: '', order: 'newest', ...overrides })

describe('decision search', () => {
  it('normalises unique query terms', () => expect(terms(' Local  local SQLite ')).toEqual(['local', 'sqlite']))

  it('uses AND semantics across metadata and body text', () => {
    const records = [record({}), record({ id: '0002', slug: 'remote', title: 'Remote API', searchText: '0002 remote API network' })]
    expect(filterRecords(records, state({ query: 'local private' })).map((item) => item.id)).toEqual(['0001'])
    expect(filterRecords(records, state({ query: 'local network' }))).toEqual([])
  })

  it('combines filters and ordering', () => {
    const records = [record({}), record({ id: '0002', slug: 'draft', status: 'proposed', category: 'product', tags: ['scope'] })]
    expect(filterRecords(records, state({ status: 'accepted', category: 'architecture', tag: 'local-first' })).map((item) => item.id)).toEqual(['0001'])
    expect(filterRecords(records, state({ order: 'oldest' })).map((item) => item.id)).toEqual(['0001', '0002'])
  })

  it('round-trips bookmarkable URL state', () => {
    const expected = state({ query: 'calendar feed', category: 'architecture', tag: 'ics', order: 'oldest' })
    expect(stateFromUrl(new URLSearchParams(stateToUrl(expected)))).toEqual(expected)
  })

  it('creates a relevant clipped excerpt', () => expect(excerpt(record({}), 'portable', 35)).toContain('portable'))

  it('highlights text without treating the query as markup', () => {
    render(<p>{highlight('Use SQLite safely', 'sqlite <script>')}</p>)
    expect(screen.getByText('SQLite', { selector: 'mark' })).toBeInTheDocument()
    expect(document.querySelector('script')).toBeNull()
  })
})
