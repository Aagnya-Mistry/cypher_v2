import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// In development, calls to /api/... go to the FastAPI backend, so the browser sees one site.
export default defineConfig({
  plugins: [react()],
  server: {
    proxy: {
      '/api': 'http://localhost:8000',
    },
  },
})
