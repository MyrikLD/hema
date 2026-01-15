import { Event } from './event';

export interface CalendarDay {
  date: string; // YYYY-MM-DD
  is_today: boolean;
  is_current_month: boolean;
  events: Event[];
}

export interface CalendarMonth {
  date: string;
  days: CalendarDay[];
  prev_date: string;
  next_date: string;
}
