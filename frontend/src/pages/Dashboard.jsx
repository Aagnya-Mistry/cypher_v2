import { useEffect, useState } from 'react'
import { useAuth } from '../auth/AuthContext'
import { apiFetch } from '../api/client'

export default function Dashboard() {
  const { user, signOut } = useAuth()
  const [backendUser, setBackendUser] = useState(null)
  const [error, setError] = useState('')

  useEffect(() => {
    // Asks our own backend "who am I?" to prove it accepts the Supabase login.
    apiFetch('/auth/me').then(setBackendUser).catch((e) => setError(e.message))
  }, [])

  return (
    <main>
      <h1>Dashboard</h1>
      <p>Logged in as {user?.email}</p>
      <p>
        Backend check:{' '}
        {error ? `failed (${error})` : backendUser ? `ok, user id ${backendUser.id}` : 'checking…'}
      </p>
      <p>Upload and history come next.</p>
      <button onClick={signOut}>Log out</button>
    </main>
  )
}
