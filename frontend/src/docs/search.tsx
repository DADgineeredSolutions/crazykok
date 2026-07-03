import { Fragment, ReactNode } from 'react'
import type { AdrRecord, SearchState } from './types'

export function terms(query: string): string[] {
  return [...new Set(query.toLocaleLowerCase().trim().split(/\s+/).filter(Boolean))]
}

export function filterRecords(records: AdrRecord[], state: SearchState): AdrRecord[] {
  const needles = terms(state.query)
  return records
    .filter((record) => !state.status || record.status === state.status)
    .filter((record) => !state.category || record.category === state.category)
    .filter((record) => !state.tag || record.tags.includes(state.tag))
    .filter((record) => needles.every((needle) => record.searchText.toLocaleLowerCase().includes(needle)))
    .sort((left, right) => (state.order === 'newest' ? right.id.localeCompare(left.id) : left.id.localeCompare(right.id)))
}

export function excerpt(record: AdrRecord, query: string, length = 190): string {
  const haystack = record.searchText
  const needles = terms(query)
  const position = needles.reduce((found, needle) => {
    const candidate = haystack.toLocaleLowerCase().indexOf(needle)
    return candidate >= 0 && (found < 0 || candidate < found) ? candidate : found
  }, -1)
  const start = Math.max(0, position < 0 ? 0 : position - Math.floor(length / 3))
  const clipped = haystack.slice(start, start + length).trim()
  return `${start > 0 ? '…' : ''}${clipped}${start + length < haystack.length ? '…' : ''}`
}

export function highlight(value: string, query: string): ReactNode {
  const needles = terms(query).sort((a, b) => b.length - a.length)
  if (!needles.length) return value
  const escaped = needles.map((needle) => needle.replace(/[.*+?^${}()|[\]\\]/g, '\\$&'))
  const matcher = new RegExp(`(${escaped.join('|')})`, 'gi')
  return value.split(matcher).map((part, index) =>
    needles.includes(part.toLocaleLowerCase()) ? <mark key={`${part}-${index}`}>{part}</mark> : <Fragment key={`${part}-${index}`}>{part}</Fragment>,
  )
}

export function stateFromUrl(parameters: URLSearchParams): SearchState {
  return {
    query: parameters.get('q') ?? '',
    status: parameters.get('status') ?? '',
    category: parameters.get('category') ?? '',
    tag: parameters.get('tag') ?? '',
    order: parameters.get('order') === 'oldest' ? 'oldest' : 'newest',
  }
}

export function stateToUrl(state: SearchState): string {
  const parameters = new URLSearchParams()
  if (state.query) parameters.set('q', state.query)
  if (state.status) parameters.set('status', state.status)
  if (state.category) parameters.set('category', state.category)
  if (state.tag) parameters.set('tag', state.tag)
  if (state.order !== 'newest') parameters.set('order', state.order)
  const query = parameters.toString()
  return query ? `?${query}` : ''
}
