import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { useAuth } from '../auth/AuthContext'

export default function Signup() {
  const { signUp } = useAuth()
  const navigate = useNavigate()
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const [checkEmail, setCheckEmail] = useState(false)
  const [busy, setBusy] = useState(false)

  async function handleSubmit(e) {
    e.preventDefault()
    setError('')
    setBusy(true)
    const { data, error } = await signUp(email, password)
    setBusy(false)
    if (error) {
      setError(error.message) // e.g. password too short (Supabase enforces its own minimum)
      return
    }
    if (data.session) {
      navigate('/dashboard', { replace: true }) // email confirmation is turned off in Supabase
    } else {
      setCheckEmail(true) // email confirmation is on: Supabase sent a link
    }
  }

  if (checkEmail) {
    return (
      <main>
        <h1>Check your email</h1>
        <p>We sent a confirmation link to {email}. Open it, then <Link to="/login">log in</Link>.</p>
      </main>
    )
  }

  return (
    <main>
      <h1>Sign up</h1>
      <form onSubmit={handleSubmit}>
        <p>
          <label>Email<br /><input type="email" value={email} onChange={(e) => setEmail(e.target.value)} required autoComplete="email" /></label>
        </p>
        <p>
          <label>Password<br /><input type="password" value={password} onChange={(e) => setPassword(e.target.value)} required minLength={8} autoComplete="new-password" /></label>
        </p>
        <button type="submit" disabled={busy}>{busy ? 'Creating account…' : 'Sign up'}</button>
      </form>
      {error && <p role="alert">{error}</p>}
      <p>Already have an account? <Link to="/login">Log in</Link></p>
    </main>
  )
}
