import { format, parse } from 'date-fns';
import { ru } from 'date-fns/locale';

export function formatDate(date: string | Date, formatStr: string): string {
  const dateObj = typeof date === 'string' ? new Date(date) : date;
  return format(dateObj, formatStr, { locale: ru });
}

export function formatTime(datetime: string): string {
  // Добавляем Z чтобы браузер понял что это UTC и сконвертировал в локальное
  const date = new Date(datetime + 'Z');
  return format(date, 'HH:mm');
}

export function formatDateTime(datetime: string): string {
  // Добавляем Z чтобы браузер понял что это UTC и сконвертировал в локальное
  const date = new Date(datetime + 'Z');
  return format(date, 'dd MMMM yyyy, HH:mm', { locale: ru });
}

export function getDayNumber(date: string): number {
  return new Date(date).getDate();
}
