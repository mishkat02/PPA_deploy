// Backend base URL. Set VITE_API_URL at build time (e.g. on Render/Netlify);
// falls back to the local Flask server for development.
export const API_URL = (import.meta.env.VITE_API_URL || 'http://127.0.0.1:5000').replace(/\/+$/, '')
