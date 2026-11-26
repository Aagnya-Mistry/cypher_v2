import { useState } from 'react'
import { apiUpload } from '../api/client'

const FISCAL_YEARS = ['FY2024-25', 'FY2025-26']
const MAX_MB = 50

export default function UploadForm({ onUploaded }) {
  const [companyName, setCompanyName] = useState('')
  const [fiscalYear, setFiscalYear] = useState(FISCAL_YEARS[0])
  const [file, setFile] = useState(null)
  const [progress, setProgress] = useState(null)
  const [error, setError] = useState('')
  const [message, setMessage] = useState('')

  async function handleSubmit(e) {
    e.preventDefault()
    setError('')
    setMessage('')
    if (file.size > MAX_MB * 1024 * 1024) {
      setError(`File is larger than ${MAX_MB} MB`) // checked here too, so the user doesn't wait for a doomed upload
      return
    }
    const form = new FormData()
    form.append('file', file)
    form.append('company_name', companyName)
    form.append('fiscal_year', fiscalYear)

    setProgress(0)
    try {
      const doc = await apiUpload('/documents', form, setProgress)
      setMessage(`Uploaded ${doc.company_name} (${doc.page_count} pages)`)
      setCompanyName('')
      setFile(null)
      e.target.reset()
      onUploaded(doc)
    } catch (err) {
      setError(err.message)
    } finally {
      setProgress(null)
    }
  }

  const uploading = progress !== null
  return (
    <section>
      <h2>Upload an annual report</h2>
      <form onSubmit={handleSubmit}>
        <p>
          <label>Company name<br />
            <input value={companyName} onChange={(e) => setCompanyName(e.target.value)} required minLength={2} maxLength={100} />
          </label>
        </p>
        <p>
          <label>Financial year<br />
            <select value={fiscalYear} onChange={(e) => setFiscalYear(e.target.value)}>
              {FISCAL_YEARS.map((fy) => <option key={fy}>{fy}</option>)}
            </select>
          </label>
        </p>
        <p>
          <label>PDF (max {MAX_MB} MB)<br />
            <input type="file" accept="application/pdf" onChange={(e) => setFile(e.target.files[0] || null)} required />
          </label>
        </p>
        <button type="submit" disabled={uploading || !file}>
          {uploading ? `Uploading… ${progress}%` : 'Upload'}
        </button>
        {uploading && <p><progress value={progress} max={100} /></p>}
      </form>
      {message && <p>{message}</p>}
      {error && <p role="alert">{error}</p>}
    </section>
  )
}
