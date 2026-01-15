import { apiClient } from './client';
import { CalendarMonth } from '@/types/calendar';

export const calendarAPI = {
  getCurrentMonth: async (): Promise<CalendarMonth> => {
    const { data } = await apiClient.get('/api/calendar');
    return data;
  },
  
  getMonth: async (year: number, month: number): Promise<CalendarMonth> => {
    const { data } = await apiClient.get(`/api/calendar/${year}/${month}`);
    return data;

  },
};
