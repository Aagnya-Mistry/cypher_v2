import { Link } from 'react-router-dom'
import { useAuth } from '../auth/AuthContext'

export default function Landing() {
  const { user } = useAuth()
  return (
    <main>
      <h1>cypher-v2</h1>
      <p>
        Upload an Indian listed company's annual report. AI agents check it against SEBI's corporate
        governance rules (LODR) and give a verdict for each rule, with a quote and page number as evidence.
      </p>
      {user ? (
        <p><Link to="/dashboard">Go to dashboard</Link></p>
      ) : (
        <p>
          <Link to="/login">Log in</Link> · <Link to="/signup">Sign up</Link>
        </p>
      )}
    </main>
  )
}
