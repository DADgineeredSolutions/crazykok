import { FormEvent, useState } from 'react'

const API_BASE = '/api'

type ImportCounts = {
  created: number
  updated: number
  skipped: number
  junk_deleted: number
}

type ImportResult = {
  filename: string
  counts: ImportCounts
}

export default function OpportunityImportWorkspace() {
  const [file, setFile] = useState<File | null>(null)
  const [seedVenues, setSeedVenues] = useState(true)
  const [cleanJunk, setCleanJunk] = useState(false)
  const [busy, setBusy] = useState(false)
  const [message, setMessage] = useState('')
  const [result, setResult] = useState<ImportResult | null>(null)

  const upload = async (event: FormEvent) => {
    event.preventDefault()
    if (!file) return
    setBusy(true)
    setMessage('')
    setResult(null)
    const body = new FormData()
    body.append('opportunities_file', file)
    body.append('seed_venues', String(seedVenues))
    body.append('clean_regression_junk', String(cleanJunk))
    try {
      const response = await fetch(`${API_BASE}/opportunity-imports/apply`, { method: 'POST', body })
      const payload = await response.json()
      if (!response.ok) throw new Error(payload.detail ?? 'Unable to import opportunities.')
      setResult(payload as ImportResult)
      setMessage('Opportunity import applied.')
      setFile(null)
    } catch (reason) {
      setMessage(reason instanceof Error ? reason.message : 'Unable to import opportunities.')
    } finally {
      setBusy(false)
    }
  }

  return (
    <main className="import-workspace">
      <section className="import-intro">
        <p className="eyebrow">Milestone 15 starter</p>
        <h2>Opportunity import</h2>
        <p>Import dated opportunities and recurring series while keeping venues as physical locations selected by stable venue ID.</p>
        <div className="research-file-options">
          <article>
            <h3>Template</h3>
            <p>Use this for researched opportunity rows. Each row is one dated opportunity; repeated names can share a series.</p>
            <a className="button-link" href={`${API_BASE}/opportunity-imports/template.csv`}>Download opportunity template</a>
          </article>
          <article>
            <h3>Local seed</h3>
            <p>Starter Emmen and TT Circuit Assen research rows used to populate the current local app.</p>
            <a className="button-link primary-action" href={`${API_BASE}/opportunity-imports/local-seed.csv`}>Download local seed CSV</a>
          </article>
        </div>
      </section>

      <form className="import-form" onSubmit={upload}>
        <section className="upload-card">
          <div>
            <p className="eyebrow">Apply CSV</p>
            <h3>Upload opportunities</h3>
            <p>Rows are upserted by name, date, venue, and source. Series are created or reused automatically.</p>
          </div>
          <label>Opportunity CSV<input type="file" accept=".csv,text/csv" onChange={(event) => setFile(event.target.files?.[0] ?? null)} required /></label>
          <label className="checkbox-label"><input type="checkbox" checked={seedVenues} onChange={(event) => setSeedVenues(event.target.checked)} /> Create missing seed venues</label>
          <label className="checkbox-label"><input type="checkbox" checked={cleanJunk} onChange={(event) => setCleanJunk(event.target.checked)} /> Clean regression junk opportunities</label>
        </section>
        <button className="primary-action" disabled={busy || !file}>{busy ? 'Importing…' : 'Apply opportunity import'}</button>
      </form>

      {message ? <p className="notice">{message}</p> : null}
      {result ? (
        <section className="preview-panel">
          <h3>Import result</h3>
          <div className="summary-strip">
            <span><strong>{result.counts.created}</strong> created</span>
            <span><strong>{result.counts.updated}</strong> updated</span>
            <span><strong>{result.counts.skipped}</strong> skipped</span>
            <span><strong>{result.counts.junk_deleted}</strong> junk deleted</span>
          </div>
        </section>
      ) : null}
    </main>
  )
}
