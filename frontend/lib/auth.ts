export function isAuthenticated(): boolean {
  if (typeof window === 'undefined') return false;
  return !!localStorage.getItem('auth');
}

export function setAuth(username: string, password: string) {
  const credentials = btoa(`${username}:${password}`);
  localStorage.setItem('auth', credentials);
}

export function clearAuth() {
  localStorage.removeItem('auth');
}

export function getAuthHeader(): string | null {
  if (typeof window === 'undefined') return null;
  return localStorage.getItem('auth');
}
