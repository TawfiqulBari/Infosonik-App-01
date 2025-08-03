import axios from 'axios';

// Create axios instance with base URL
// In production, use relative URLs since Traefik serves everything from the same domain
const api = axios.create({
  baseURL: process.env.NODE_ENV === 'production' ? '' : 'http://localhost:8000',
  headers: {
    'Content-Type': 'application/json',
  },
});

export default api;
