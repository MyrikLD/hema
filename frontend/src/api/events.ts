import type { Event } from '../types';
import { get } from './client';

export async function listEvents(start: string, end: string): Promise<Event[]> {
  return get<Event[]>(`/events?start=${encodeURIComponent(start)}&end=${encodeURIComponent(end)}`);
}

export async function getEvent(id: number): Promise<Event> {
  return get<Event>(`/events/${id}`);
}
