import { useEffect, useState } from 'react'
import { useAuth } from '../auth/AuthContext'
import { apiFetch } from '../api/client'
import UploadForm from '../components/UploadForm'
import DocumentList from '../components/DocumentList'

export default function Dashboard() {
  const { user, signOut } = useAuth()
  const [documents, setDocuments] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  useEffect(() => {
    apiFetch('/documents')
      .then(setDocuments)
      .catch((e) => setError(e.message))
      .finally(() => setLoading(false))
  }, [])

  return (
    <main>
      <h1>Dashboard</h1>
      <p>
        Logged in as {user?.email} · <button onClick={signOut}>Log out</button>
      </p>
      <UploadForm onUploaded={(doc) => setDocuments((prev) => [doc, ...prev])} />
      <DocumentList documents={documents} loading={loading} error={error} />
    </main>
  )
}
