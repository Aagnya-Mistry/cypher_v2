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

// Uploads a file with a progress callback (fetch can't report upload progress, XMLHttpRequest can).
export async function apiUpload(path, formData, onProgress) {
  const { data } = await supabase.auth.getSession()
  const token = data.session?.access_token

  return new Promise((resolve, reject) => {
    const xhr = new XMLHttpRequest()
    xhr.open('POST', `/api${path}`)
    if (token) xhr.setRequestHeader('Authorization', `Bearer ${token}`)

    xhr.upload.onprogress = (e) => {
      if (e.lengthComputable) onProgress?.(Math.round((e.loaded / e.total) * 100))
    }
    xhr.onload = () => {
      let body = null
      try {
        body = JSON.parse(xhr.responseText)
      } catch {
        /* response was not JSON */
      }
      if (xhr.status >= 200 && xhr.status < 300) resolve(body)
      else reject(new Error(body?.detail || `Upload failed (${xhr.status})`))
    }
    xhr.onerror = () => reject(new Error('Network error, is the backend running?'))
    xhr.send(formData)
  })
}
