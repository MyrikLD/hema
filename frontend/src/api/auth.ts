import type { AuthResponse, User } from '../types';
import { get, patch } from './client';

export async function login(username: string, password: string): Promise<AuthResponse> {
  const body = new URLSearchParams({ username, password });
  const response = await fetch('/api/users/login', {
    method: 'POST',
    headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    body,
  });
  if (!response.ok) {
    const data = await response.json().catch(() => ({}));
    throw new Error(data.detail || 'Login failed');
  }
  return response.json();
}

export async function register(data: {
  name: string;
  password: string;
  gender?: string;
  phone?: string;
}): Promise<User> {
  const response = await fetch('/api/users/registration', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data),
  });
  if (!response.ok) {
    const body = await response.json().catch(() => ({}));
    throw new Error(body.detail || 'Registration failed');
  }
  return response.json();
}

export async function getMe(): Promise<User> {
  return get<User>('/users/me');
}

export async function updateProfile(data: {
  name?: string;
  phone?: string;
  gender?: string;
  password?: string;
}): Promise<User> {
  return patch<User>('/users/', data);
}
