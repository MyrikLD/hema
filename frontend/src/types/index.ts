export interface User {
  username: string;
  name: string | null;
  gender: 'm' | 'f' | 'o';
  phone: string | null;
  is_trainer: boolean;
}

export interface AuthResponse {
  access_token: string;
  token_type: 'bearer';
}

export interface Event {
  id: number;
  name: string;
  color: string;
  date: string;       // "YYYY-MM-DD"
  time_start: string; // "HH:MM:SS"
  time_end: string;   // "HH:MM:SS"
  weekly_id: number | null;
  trainer_id: number | null;
  trainer_name: string | null;
  price: number;
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
  user_id: number | null;
  event_id: number | null;
  event_name: string | null;
  event_color: string | null;
}

export interface ScheduleEntry {
  id: number;
  name: string;
  color: string;
  weekday: number;    // 0=Monday … 6=Sunday
  time_start: string; // "HH:MM:SS"
  time_end: string;   // "HH:MM:SS"
  trainer_id: number | null;
  trainer_name: string | null;
}

