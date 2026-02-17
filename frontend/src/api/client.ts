const BASE_URL = '/api';

class ApiError extends Error {
  status: number;
  constructor(status: number, message: string) {
    super(message);
    this.status = status;
  }
}

async function request<T>(
  path: string,
  options: RequestInit = {},
): Promise<T> {
  const token = localStorage.getItem('token');
  const headers: Record<string, string> = {
    'Content-Type': 'application/json',
    ...((options.headers as Record<string, string>) || {}),
  };
  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }

  const response = await fetch(`${BASE_URL}${path}`, {
    ...options,
    headers,
  });

  if (!response.ok) {
    if (response.status === 401) {
      localStorage.removeItem('token');
      window.location.href = '/login';
    }
    const body = await response.json().catch(() => ({}));
    throw new ApiError(response.status, body.detail || response.statusText);
  }

  if (response.status === 204) {
    return undefined as T;
  }

  return response.json();
}

export function get<T>(path: string): Promise<T> {
  return request<T>(path);
}

export function post<T>(path: string, body?: unknown): Promise<T> {
  return request<T>(path, {
    method: 'POST',
    body: body !== undefined ? JSON.stringify(body) : undefined,
  });
}

export function put<T>(path: string, body?: unknown): Promise<T> {
  return request<T>(path, {
    method: 'PUT',
    body: body !== undefined ? JSON.stringify(body) : undefined,
  });
}

export function patch<T>(path: string, body?: unknown): Promise<T> {
  return request<T>(path, {
    method: 'PATCH',
    body: body !== undefined ? JSON.stringify(body) : undefined,
  });
}

export function del<T>(path: string): Promise<T> {
  return request<T>(path, { method: 'DELETE' });
}

export { ApiError };
