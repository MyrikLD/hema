import type { Visit } from '../types';
import { get } from './client';

export async function getMyHistory(limit = 50, offset = 0): Promise<Visit[]> {
  return get<Visit[]>(`/visits/me?limit=${limit}&offset=${offset}`);
}
