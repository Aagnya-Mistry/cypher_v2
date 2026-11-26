export default function DocumentList({ documents, loading, error }) {
  return (
    <section>
      <h2>Your documents</h2>
      {loading && <p>Loading…</p>}
      {error && <p role="alert">{error}</p>}
      {!loading && !error && documents.length === 0 && <p>No documents yet. Upload one above.</p>}
      {documents.length > 0 && (
        <table border="1" cellPadding="6" style={{ borderCollapse: 'collapse' }}>
          <thead>
            <tr>
              <th>Company</th>
              <th>Year</th>
              <th>File</th>
              <th>Pages</th>
              <th>Size</th>
              <th>Status</th>
              <th>Uploaded</th>
            </tr>
          </thead>
          <tbody>
            {documents.map((d) => (
              <tr key={d.id}>
                <td>{d.company_name}</td>
                <td>{d.fiscal_year}</td>
                <td>{d.original_filename}</td>
                <td>{d.page_count}</td>
                <td>{(d.size_bytes / 1e6).toFixed(1)} MB</td>
                <td>{d.status}</td>
                <td>{new Date(d.created_at).toLocaleString()}</td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </section>
  )
}
