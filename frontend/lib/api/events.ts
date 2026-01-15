import { apiClient } from './client';
import { Event } from '@/types/event';

export interface CreateEventData {
  name: string;
  color?: string;
  start: string;
  end: string;
}

export const eventsAPI = {
  list: async (start: string, end: string): Promise<Event[]> => {
    const { data } = await apiClient.get('/api/events', {
      params: { start, end },
    });
    return data;
  },
  
  getById: async (id: number): Promise<Event> => {
    const { data } = await apiClient.get(`/api/events/${id}`);
    return data;
  },
  
  create: async (eventData: CreateEventData): Promise<Event> => {
    const { data } = await apiClient.post('/api/events', eventData);
    return data;
  },
  
  update: async (id: number, event: Partial<Event>): Promise<Event> => {
    const { data } = await apiClient.put(`/api/events/${id}`, event);
    return data;
  },
  
  delete: async (id: number): Promise<void> => {
    await apiClient.delete(`/api/events/${id}`);
  },

  take: async (id: number): Promise<Event> => {
    const { data } = await apiClient.post(`/api/events/take/${id}`);
    return data;
  },
};
