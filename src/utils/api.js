import axios from 'axios';

// Create axios instance with base URL
const api = axios.create({
  baseURL: 'https://infsnk-app-01.tawfiqulbari.work',
  headers: {
    'Content-Type': 'application/json',
  },
});

export default api;
