import { useEffect, useMemo, useState } from 'react'
import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'
import recordsJson from './generated/adrs.json'
import { excerpt, filterRecords, highlight, stateFromUrl, stateToUrl } from './search'
import type { AdrRecord, SearchState } from './types'
import './docs.css'

const records = recordsJson as AdrRecord[]
const emptyState: SearchState = { query: '', status: '', category: '', tag: '', order: 'newest' }

function navigate(url: string) {
  window.history.pushState({}, '', url)
  window.dispatchEvent(new PopStateEvent('popstate'))
  window.scrollTo({ top: 0, behavior: 'auto' })
}

function Link({ href, children, className }: { href: string; children: React.ReactNode; className?: string }) {
  return <a href={href} className={className} onClick={(event) => { event.preventDefault(); navigate(href) }}>{children}</a>
}

function Metadata({ record }: { record: AdrRecord }) {
  return (
    <dl className="adr-meta">
      <div><dt>Status</dt><dd><span className={`status status-${record.status}`}>{record.status}</span></dd></div>
      <div><dt>Date</dt><dd>{record.date}</dd></div>
      <div><dt>Category</dt><dd>{record.category}</dd></div>
      <div><dt>Tags</dt><dd className="tag-row">{record.tags.map((tag) => <span className="tag" key={tag}>{tag}</span>)}</dd></div>
    </dl>
  )
}

function Overview() {
  const [state, setState] = useState(() => stateFromUrl(new URLSearchParams(window.location.search)))
  const result = useMemo(() => filterRecords(records, state), [state])
  const statuses = [...new Set(records.map((record) => record.status))].sort()
  const categories = [...new Set(records.map((record) => record.category))].sort()
  const tags = [...new Set(records.flatMap((record) => record.tags))].sort()

  useEffect(() => {
    window.history.replaceState({}, '', `/decisions${stateToUrl(state)}`)
  }, [state])

  const update = (field: keyof SearchState, value: string) => setState((current) => ({ ...current, [field]: value }))
  return (
    <>
      <section className="docs-hero">
        <p className="docs-kicker">Architecture memory, kept in Git</p>
        <h1>Decision Log</h1>
        <p>Why Crazy Kok is shaped the way it is—searchable, linked, and rendered directly from the repository.</p>
      </section>
      <section className="search-panel" aria-label="Decision filters">
        <label className="search-field">Search decisions<input type="search" value={state.query} onChange={(event) => update('query', event.target.value)} placeholder="Try calendar, privacy, SQLite…" /></label>
        <label>Status<select value={state.status} onChange={(event) => update('status', event.target.value)}><option value="">All statuses</option>{statuses.map((value) => <option key={value}>{value}</option>)}</select></label>
        <label>Category<select value={state.category} onChange={(event) => update('category', event.target.value)}><option value="">All categories</option>{categories.map((value) => <option key={value}>{value}</option>)}</select></label>
        <label>Tag<select value={state.tag} onChange={(event) => update('tag', event.target.value)}><option value="">All tags</option>{tags.map((value) => <option key={value}>{value}</option>)}</select></label>
        <label>Order<select value={state.order} onChange={(event) => update('order', event.target.value)}><option value="newest">Newest first</option><option value="oldest">Oldest first</option></select></label>
        <button type="button" className="quiet-button" onClick={() => setState(emptyState)}>Clear all</button>
      </section>
      <div className="result-heading"><h2>{result.length} decision{result.length === 1 ? '' : 's'}</h2><span>{records.length} total</span></div>
      {result.length ? <ol className="decision-list">{result.map((record) => (
        <li key={record.id}>
          <article className="decision-card">
            <div className="decision-id">ADR {record.id}</div>
            <h3><Link href={`/adr/${record.slug}${stateToUrl(state)}`}>{highlight(record.title, state.query)}</Link></h3>
            <div className="card-meta"><span className={`status status-${record.status}`}>{record.status}</span><span>{record.category}</span><time>{record.date}</time></div>
            <p>{highlight(excerpt(record, state.query), state.query)}</p>
            <div className="tag-row">{record.tags.map((tag) => <button key={tag} className="tag" onClick={() => update('tag', tag)}>{tag}</button>)}</div>
          </article>
        </li>
      ))}</ol> : <section className="no-results"><h2>No decisions found</h2><p>Those filters have painted us into a very tidy corner.</p><button onClick={() => setState(emptyState)}>Reset filters</button></section>}
    </>
  )
}

function Portal() {
  return (
    <>
      <section className="docs-hero portal-hero">
        <p className="docs-kicker">One doorway, two kinds of truth</p>
        <h1>Project Docs</h1>
        <p>Read the decisions behind Crazy Kok or work directly with its live, machine-checked API contract.</p>
      </section>
      <section className="portal-grid" aria-label="Documentation areas">
        <article>
          <span className="portal-number">01</span>
          <h2>Decision Log</h2>
          <p>Search the architecture record: context, trade-offs, consequences, and the choices we intend to revisit.</p>
          <Link href="/decisions">Browse decisions →</Link>
        </article>
        <article>
          <span className="portal-number">02</span>
          <h2>API Reference</h2>
          <p>Explore the canonical OpenAPI description, run requests, inspect schemas, and follow live HAL links.</p>
          <a href="/api-reference">Open API reference →</a>
        </article>
      </section>
    </>
  )
}

function Detail({ slug }: { slug: string }) {
  const recordIndex = records.findIndex((record) => record.slug === slug)
  const record = records[recordIndex]
  const returnQuery = window.location.search
  if (!record) return <section className="not-found"><p className="docs-kicker">404</p><h1>Decision not found</h1><p>This ADR may have moved or never made it past the whiteboard.</p><Link href="/decisions">Return to the decision log</Link></section>
  const previous = records[recordIndex - 1]
  const next = records[recordIndex + 1]
  return (
    <>
      <Link className="back-link" href={`/decisions${returnQuery}`}>← All decisions</Link>
      <article className="adr-document">
        <header><p className="docs-kicker">ADR {record.id}</p><h1>{record.title}</h1><Metadata record={record} /></header>
        <div className="markdown"><ReactMarkdown remarkPlugins={[remarkGfm]} skipHtml>{record.markdown.replace(/^# ADR .+\n+/, '')}</ReactMarkdown></div>
      </article>
      <nav className="record-navigation" aria-label="Adjacent decisions">
        {previous ? <Link href={`/adr/${previous.slug}`}><small>Previous</small><strong>ADR {previous.id}: {previous.title}</strong></Link> : <span />}
        {next ? <Link href={`/adr/${next.slug}`}><small>Next</small><strong>ADR {next.id}: {next.title}</strong></Link> : <span />}
      </nav>
    </>
  )
}

export default function DocsApp() {
  const [path, setPath] = useState(window.location.pathname)
  useEffect(() => {
    const sync = () => setPath(window.location.pathname)
    window.addEventListener('popstate', sync)
    return () => window.removeEventListener('popstate', sync)
  }, [])
  const match = path.match(/^\/adr\/([^/]+)\/?$/)
  const page = match ? <Detail slug={decodeURIComponent(match[1])} /> : path === '/' ? <Portal /> : path === '/decisions' ? <Overview /> : <Detail slug="" />
  return <div className="docs-site"><header className="docs-header"><Link href="/" className="docs-brand"><img src="/crazykok-logo.png" alt="" /><span>Crazy Kok <strong>Docs</strong></span></Link><nav aria-label="Documentation"><Link href="/decisions">Decisions</Link><a href="/api-reference">API</a></nav><span className="read-only">Read-only · contract-driven</span></header><main>{page}</main><footer>Crazy Kok documentation · Repository and API contracts are the sources of truth</footer></div>
}
