export interface User {
  name: string;
  gender: 'm' | 'f' | 'o';
  phone: string | null;
}

export interface AuthResponse {
  access_token: string;
  token_type: 'bearer';
}

export interface Event {
  id: number;
  name: string;
  color: string;
  start: string;
  end: string;
  weekly_id: number | null;
  trainer_id: number | null;
}

export interface Intention {
  id: number;
  user_id: number;
  event_id: number;
}

export interface IntentionWithUser {
  id: number;
  user_id: number;
  event_id: number;
  user_name: string;
}

export interface Visit {
  timestamp: string;
  uid: string;
  user_id: number | null;
  event_id: number | null;
  event_name: string | null;
  event_color: string | null;
}

export interface CalendarDay {
  date: string;
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
