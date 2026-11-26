import { supabase } from '../lib/supabase'

// The one way the frontend talks to our backend: adds the login token and turns errors into messages.
export async function apiFetch(path, options = {}) {
  const { data } = await supabase.auth.getSession()
  const token = data.session?.access_token

  const res = await fetch(`/api${path}`, {
    ...options,
    headers: {
      ...(options.headers || {}),
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
    },
  })

  if (!res.ok) {
    let message = `Request failed (${res.status})`
    try {
      message = (await res.json()).detail || message
    } catch {
      /* response was not JSON */
    }
    throw new Error(message)
  }
  return res.json()
}
