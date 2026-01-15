import axios from 'axios';

// Определяем URL API в зависимости от окружения
function getApiUrl() {
  // Server-side в Docker: используем имя сервиса
  if (typeof window === 'undefined' && process.env.API_URL) {
    return process.env.API_URL;
  }
  // Client-side или dev: используем localhost
  return process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
}

export const apiClient = axios.create({
  baseURL: getApiUrl(),
  withCredentials: true,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Interceptor для Basic Auth
apiClient.interceptors.request.use((config) => {
  if (typeof window !== 'undefined') {
    const auth = localStorage.getItem('auth');
    if (auth) {
      config.headers.Authorization = `Basic ${auth}`;
    }
  }
  return config;
});

// Interceptor для обработки ошибок авторизации
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      if (typeof window !== 'undefined') {
        localStorage.removeItem('auth');
        window.location.href = '/login';
      }
    }
    return Promise.reject(error);
  }
);
