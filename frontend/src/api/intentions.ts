import type { Intention, IntentionWithUser } from '../types';
import { post, del, get } from './client';

export async function signUp(eventId: number): Promise<Intention> {
  return post<Intention>('/intentions', { event_id: eventId });
}

export async function cancelSignUp(eventId: number): Promise<void> {
  return del<void>(`/intentions/${eventId}`);
}

export async function getAttendees(eventId: number): Promise<IntentionWithUser[]> {
  return get<IntentionWithUser[]>(`/intentions/event/${eventId}`);
}

export async function hasIntention(eventId: number): Promise<boolean> {
  const res = await get<{ has_intention: boolean }>(`/intentions/me/${eventId}`);
  return res.has_intention;
}
