import axios from 'axios';

const api = axios.create({
    // baseURL: localStorage.getItem('api_url') || 'https://kitabistan.up.railway.app/api',
    baseURL: localStorage.getItem('api_url') || import.meta.env.VITE_API_URL
});


// Attach JWT token to every request
api.interceptors.request.use((config) => {
    const token = localStorage.getItem('access_token');
    if (token) {
        config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
});

export default api;